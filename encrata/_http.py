"""Shared HTTP transport: request, retry/backoff, and error mapping."""

from __future__ import annotations

import asyncio
import random
import time
from typing import Any

import httpx

from ._constants import (
    BACKOFF_FACTOR,
    INITIAL_BACKOFF,
    MAX_BACKOFF,
    RETRYABLE_STATUS_CODES,
    parse_retry_after,
)
from .exceptions import (
    APIConnectionError,
    APIError,
    AuthenticationError,
    InsufficientCreditsError,
    InvalidRequestError,
    RateLimitError,
)


def decode_success_response(resp: httpx.Response) -> Any:
    """Decode a successful response body.

    Empty bodies are valid for some endpoints. Non-empty non-JSON bodies are
    surfaced as SDK errors so callers do not see raw JSONDecodeError traces.
    """
    if not resp.content or not resp.text.strip():
        return {}
    try:
        return resp.json()
    except ValueError as e:
        content_type = resp.headers.get("Content-Type", "unknown")
        preview = resp.text[:200].replace("\n", "\\n")
        raise APIError(
            "Invalid JSON response from Encrata API "
            f"(status={resp.status_code}, content_type={content_type}): {preview}",
            status_code=resp.status_code,
        ) from e


def to_error(resp: Any) -> Exception:
    """Map an HTTP status code to the right exception."""
    try:
        err = resp.json()
    except Exception:  # noqa: BLE001
        err = {}
    if not isinstance(err, dict):
        err = {}

    msg = err.get("message") or err.get("error") or resp.reason_phrase
    code = resp.status_code

    if code == 401:
        return AuthenticationError(msg, status_code=code)
    if code == 402:
        return InsufficientCreditsError(msg, status_code=code)
    if code == 400:
        return InvalidRequestError(msg, status_code=code)
    if code == 429:
        return RateLimitError(msg, status_code=code)
    return APIError(msg, status_code=code)


def backoff_delay(attempt: int) -> float:
    """Full-jitter exponential backoff, capped at MAX_BACKOFF.

    Returns a random delay in ``[0, min(base * factor**attempt, cap)]`` so
    that many clients retrying at once spread their load instead of
    spiking together (the AWS "full jitter" strategy).
    """
    ceiling = min(INITIAL_BACKOFF * (BACKOFF_FACTOR ** attempt), MAX_BACKOFF)
    return random.uniform(0, ceiling)


class SyncHTTPMixin:
    """Sync request/retry/backoff. Expects ``base_url``, ``timeout``,
    ``max_retries``, and ``_client`` on the instance."""

    base_url: str
    timeout: int
    max_retries: int
    _client: httpx.Client

    def _get(self, path: str, *, params: dict[str, Any] | None = None) -> dict[str, Any]:
        return self._request("GET", path, params=params)

    def _post(
        self,
        path: str,
        body: dict[str, Any],
        *,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        return self._request("POST", path, body=body, params=params)

    def _delete(self, path: str) -> dict[str, Any]:
        return self._request("DELETE", path)

    def _request(
        self,
        method: str,
        path: str,
        *,
        body: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        url = f"{self.base_url}{path}"

        attempt = 0
        while True:
            try:
                resp = self._client.request(
                    method,
                    url,
                    params=params or None,
                    json=body if body else None,
                )
            except httpx.TimeoutException as e:
                if attempt < self.max_retries:
                    self._sleep_backoff(attempt, None)
                    attempt += 1
                    continue
                raise APIConnectionError(
                    f"Request timed out after {self.timeout}s"
                ) from e
            except httpx.RequestError as e:
                if attempt < self.max_retries:
                    self._sleep_backoff(attempt, None)
                    attempt += 1
                    continue
                raise APIConnectionError(f"Connection error: {e}") from e

            if (
                resp.status_code in RETRYABLE_STATUS_CODES
                and attempt < self.max_retries
            ):
                self._sleep_backoff(attempt, resp)
                attempt += 1
                continue

            if resp.status_code >= 400:
                raise to_error(resp)

            return decode_success_response(resp)

    def _sleep_backoff(self, attempt: int, resp: httpx.Response | None) -> None:
        """Wait before the next retry: honour Retry-After, else full jitter."""
        if resp is not None:
            retry_after = parse_retry_after(resp.headers.get("Retry-After"))
            if retry_after is not None:
                time.sleep(min(retry_after, MAX_BACKOFF))
                return
        time.sleep(backoff_delay(attempt))


class AsyncHTTPMixin:
    """Async request/retry/backoff. Expects ``base_url``, ``max_retries``,
    and ``_client`` on the instance."""

    base_url: str
    max_retries: int
    _client: httpx.AsyncClient

    async def _get(
        self, path: str, *, params: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        return await self._request("GET", path, params=params)

    async def _post(
        self,
        path: str,
        body: dict[str, Any],
        *,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        return await self._request("POST", path, body=body, params=params)

    async def _request(
        self,
        method: str,
        path: str,
        *,
        body: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        url = f"{self.base_url}{path}"
        attempt = 0
        while True:
            try:
                resp = await self._client.request(
                    method,
                    url,
                    params=params or None,
                    json=body if body is not None else None,
                )
            except httpx.RequestError as e:
                if attempt < self.max_retries:
                    await self._sleep_backoff(attempt, None)
                    attempt += 1
                    continue
                raise APIConnectionError(f"Connection error: {e}") from e

            if (
                resp.status_code in RETRYABLE_STATUS_CODES
                and attempt < self.max_retries
            ):
                await self._sleep_backoff(attempt, resp)
                attempt += 1
                continue

            if resp.status_code >= 400:
                raise to_error(resp)

            return decode_success_response(resp)

    async def _sleep_backoff(self, attempt: int, resp: Any | None) -> None:
        """Wait before the next retry: honour Retry-After, else full jitter."""
        if resp is not None:
            retry_after = parse_retry_after(resp.headers.get("Retry-After"))
            if retry_after is not None:
                await asyncio.sleep(min(retry_after, MAX_BACKOFF))
                return
        await asyncio.sleep(backoff_delay(attempt))
