from __future__ import annotations

import asyncio
import random
from typing import Any, Sequence

import httpx

from ._constants import (
    BACKOFF_FACTOR,
    DEFAULT_BASE_URL,
    INITIAL_BACKOFF,
    MAX_BACKOFF,
    MAX_RETRIES,
    RETRYABLE_STATUS_CODES,
    USER_AGENT,
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
from .types import (
    BreachReport,
    ContactList,
    Monitor,
    MonitorRun,
    MonitorSnapshot,
    Person,
    Validation,
)

__all__ = ["AsyncEncrata"]


class AsyncEncrata:
    """Async Encrata API client (httpx-based).

    Usage::

        import asyncio
        from encrata import AsyncEncrata

        async def main():
            async with AsyncEncrata("enc_live_...") as client:
                person = await client.lookup("elon@tesla.com")
                print(person.name, person.company)

                # Bulk enrichment loop, run concurrently:
                people = await client.lookup_many(
                    ["a@x.com", "b@x.com", "c@x.com"]
                )

        asyncio.run(main())
    """

    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = DEFAULT_BASE_URL,
        timeout: int = 30,
        max_retries: int = MAX_RETRIES,
        max_concurrency: int = 10,
        transport: "httpx.AsyncBaseTransport | None" = None,
    ) -> None:
        if not api_key:
            raise AuthenticationError("API key is required.")

        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.max_retries = max_retries
        self._semaphore = asyncio.Semaphore(max_concurrency)
        self._client = httpx.AsyncClient(
            timeout=timeout,
            transport=transport,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "User-Agent": USER_AGENT,
            },
        )

    # ── Lifecycle ─────────────────────────────────────

    async def __aenter__(self) -> "AsyncEncrata":
        return self

    async def __aexit__(self, *exc: object) -> None:
        await self.aclose()

    async def aclose(self) -> None:
        """Close the underlying HTTP connection pool."""
        await self._client.aclose()

    # ── Email Intelligence ────────────────────────────

    async def lookup(
        self,
        email: str,
        *,
        fields: Sequence[str] | None = None,
        nocache: bool = False,
    ) -> Person:
        """Look up a person by email address."""
        params: dict[str, Any] = {}
        if fields:
            params["fields"] = ",".join(fields)
        if nocache:
            params["nocache"] = "1"
        data = await self._post("/api/agent/lookup", {"email": email}, params=params)
        return Person.from_dict(data)

    async def validate(self, email: str) -> Validation:
        """Validate an email address (free — no credits used)."""
        data = await self._post("/api/agent/validate", {"email": email})
        return Validation.from_dict(data)

    async def breaches(self, email: str) -> BreachReport:
        """Check data breach exposure for an email (free — no credits used)."""
        data = await self._post("/api/agent/breaches", {"email": email})
        return BreachReport.from_dict(data)

    async def lookup_many(
        self,
        emails: Sequence[str],
        *,
        fields: Sequence[str] | None = None,
        nocache: bool = False,
        return_exceptions: bool = False,
    ) -> list[Person | BaseException]:
        """Look up many emails concurrently (bounded by ``max_concurrency``).

        Results are returned in the same order as ``emails``. Set
        ``return_exceptions=True`` to get failures inline instead of raising.
        """

        async def _one(email: str) -> Person:
            async with self._semaphore:
                return await self.lookup(email, fields=fields, nocache=nocache)

        return await asyncio.gather(
            *(_one(e) for e in emails),
            return_exceptions=return_exceptions,
        )

    # ── Monitors ──────────────────────────────────────

    async def list_monitors(self) -> list[Monitor]:
        """List all monitors."""
        data = await self._get("/api/agent/monitors")
        return [Monitor.from_dict(m) for m in data.get("monitors", [])]

    async def create_monitor(
        self,
        name: str,
        *,
        emails: Sequence[str] | None = None,
        frequency: str = "monthly",
        change_detection: str = "diff_only",
        list_id: str | None = None,
    ) -> Monitor:
        """Create a new monitor."""
        body: dict[str, Any] = {
            "name": name,
            "frequency": frequency,
            "change_detection": change_detection,
        }
        if list_id:
            body["data_source_type"] = "list"
            body["data_source_ref"] = list_id
        if emails:
            body["emails"] = list(emails)
        data = await self._post("/api/agent/monitors", body)
        return Monitor.from_dict(data)

    async def get_monitor(self, monitor_id: str) -> Monitor:
        """Get a monitor by ID."""
        data = await self._get(f"/api/agent/monitors/{monitor_id}")
        return Monitor.from_dict(data)

    async def trigger_run(self, monitor_id: str) -> dict[str, Any]:
        """Trigger an immediate monitoring run."""
        return await self._post(f"/api/agent/monitors/{monitor_id}/run", {})

    async def list_runs(
        self,
        monitor_id: str,
        *,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[MonitorRun], int]:
        """List runs for a specific monitor. Returns (runs, total)."""
        data = await self._get(
            f"/api/agent/monitors/{monitor_id}/runs",
            params={"limit": limit, "offset": offset},
        )
        runs = [MonitorRun.from_dict(r) for r in data.get("runs", [])]
        return runs, data.get("total", len(runs))

    async def get_run_results(
        self,
        monitor_id: str,
        run_id: str,
        *,
        changes_only: bool = False,
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[list[MonitorSnapshot], int]:
        """Get results for a specific run. Returns (snapshots, total)."""
        params: dict[str, Any] = {"limit": limit, "offset": offset}
        if changes_only:
            params["changes_only"] = "true"
        data = await self._get(
            f"/api/agent/monitors/{monitor_id}/runs/{run_id}/results",
            params=params,
        )
        snapshots = [MonitorSnapshot.from_dict(s) for s in data.get("results", [])]
        return snapshots, data.get("total", len(snapshots))

    async def list_all_runs(
        self,
        *,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[MonitorRun], int]:
        """List all runs across all monitors. Returns (runs, total)."""
        data = await self._get(
            "/api/agent/monitoring/runs",
            params={"limit": limit, "offset": offset},
        )
        runs = [MonitorRun.from_dict(r) for r in data.get("runs", [])]
        return runs, data.get("total", len(runs))

    async def list_all_results(
        self,
        *,
        changes_only: bool = False,
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[list[MonitorSnapshot], int]:
        """List all enrichment results across all monitors. Returns (snapshots, total)."""
        params: dict[str, Any] = {"limit": limit, "offset": offset}
        if changes_only:
            params["changes_only"] = "true"
        data = await self._get("/api/agent/monitoring/results", params=params)
        snapshots = [MonitorSnapshot.from_dict(s) for s in data.get("results", [])]
        return snapshots, data.get("total", len(snapshots))

    # ── Contact Lists ─────────────────────────────────

    async def list_contact_lists(self) -> list[ContactList]:
        """List all contact lists."""
        data = await self._get("/api/agent/lists")
        if isinstance(data, list):
            return [ContactList.from_dict(cl) for cl in data]
        return [ContactList.from_dict(cl) for cl in data.get("lists", data)]

    async def create_contact_list(
        self,
        name: str,
        *,
        emails: Sequence[str] | None = None,
    ) -> ContactList:
        """Create a new contact list."""
        body: dict[str, Any] = {"name": name}
        if emails:
            body["emails"] = list(emails)
        data = await self._post("/api/agent/lists", body)
        return ContactList.from_dict(data)

    async def get_contact_list(self, list_id: str) -> ContactList:
        """Get a contact list by ID."""
        data = await self._get(f"/api/agent/lists/{list_id}")
        return ContactList.from_dict(data)

    async def delete_contact_list(self, list_id: str) -> None:
        """Delete a contact list."""
        await self._request("DELETE", f"/api/agent/lists/{list_id}")

    async def list_contact_list_emails(self, list_id: str) -> list[str]:
        """List all emails in a contact list."""
        data = await self._get(f"/api/agent/lists/{list_id}/emails")
        if isinstance(data, list):
            return [e.get("email", e) if isinstance(e, dict) else e for e in data]
        return data.get("emails", [])

    async def add_contact_list_emails(
        self, list_id: str, emails: Sequence[str]
    ) -> int:
        """Add emails to a contact list. Returns count added."""
        data = await self._post(
            f"/api/agent/lists/{list_id}/emails", {"emails": list(emails)}
        )
        return data.get("added", 0)

    async def delete_contact_list_emails(
        self, list_id: str, emails: Sequence[str]
    ) -> int:
        """Remove emails from a contact list. Returns count removed."""
        data = await self._request(
            "DELETE",
            f"/api/agent/lists/{list_id}/emails",
            body={"emails": list(emails)},
        )
        return data.get("deleted", 0)

    # ── Internals ─────────────────────────────────────

    async def _get(
        self,
        path: str,
        *,
        params: dict[str, Any] | None = None,
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
                # Network blip — retry, then give up.
                if attempt < self.max_retries:
                    await self._sleep_backoff(attempt, None)
                    attempt += 1
                    continue
                raise APIConnectionError(f"Connection error: {e}") from e

            # Retry only transient server/rate-limit errors.
            if (
                resp.status_code in RETRYABLE_STATUS_CODES
                and attempt < self.max_retries
            ):
                await self._sleep_backoff(attempt, resp)
                attempt += 1
                continue

            if resp.status_code >= 400:
                raise self._to_error(resp)

            if not resp.content:
                return {}
            return resp.json()

    async def _sleep_backoff(self, attempt: int, resp: Any | None) -> None:
        """Wait before the next retry: honour Retry-After, else full jitter."""
        if resp is not None:
            retry_after = parse_retry_after(resp.headers.get("Retry-After"))
            if retry_after is not None:
                await asyncio.sleep(min(retry_after, MAX_BACKOFF))
                return
        await asyncio.sleep(self._backoff_delay(attempt))

    def _backoff_delay(self, attempt: int) -> float:
        """Full-jitter exponential backoff, capped at MAX_BACKOFF.

        Returns a random delay in ``[0, min(base * factor**attempt, cap)]`` so
        that many clients retrying at once spread their load instead of
        spiking together (the AWS "full jitter" strategy).
        """
        ceiling = min(INITIAL_BACKOFF * (BACKOFF_FACTOR ** attempt), MAX_BACKOFF)
        return random.uniform(0, ceiling)

    def _to_error(self, resp: Any) -> Exception:
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
