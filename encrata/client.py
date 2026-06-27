from __future__ import annotations

from typing import Any, Iterator, Sequence

import httpx
import time
import random
from concurrent.futures import ThreadPoolExecutor

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

from ._constants import (
    BACKOFF_FACTOR as _BACKOFF_FACTOR,
    DEFAULT_BASE_URL as _DEFAULT_BASE_URL,
    INITIAL_BACKOFF as _INITIAL_BACKOFF,
    MAX_BACKOFF as _MAX_BACKOFF,
    MAX_RETRIES as _MAX_RETRIES,
    RETRYABLE_STATUS_CODES as _RETRYABLE_STATUS_CODES,
    USER_AGENT as _USER_AGENT,
    parse_retry_after as _parse_retry_after,
)

__all__ = ["Encrata"]


class Encrata:
    """Encrata API client.

    Usage::

        from encrata import Encrata

        client = Encrata("enc_live_...")

        person = client.lookup("elon@tesla.com")
        print(person.name, person.company)
    """

    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = _DEFAULT_BASE_URL,
        timeout: int = 30,
        max_retries: int = _MAX_RETRIES,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        if not api_key:
            raise AuthenticationError("API key is required.")
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        self._client = httpx.Client(
            timeout=timeout,
            transport=transport,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "User-Agent": _USER_AGENT,
            },
        )

    # ── Lifecycle ─────────────────────────────────────

    def __enter__(self) -> "Encrata":
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()

    def close(self) -> None:
        """Close the underlying HTTP connection pool."""
        self._client.close()


    # ── Email Intelligence ────────────────────────────

    def lookup(
        self,
        email: str,
        *,
        fields: Sequence[str] | None = None,
        nocache: bool = False,
    ) -> Person:
        """Look up a person by email address.

        Args:
            email: The email address to look up.
            fields: Optional list of fields to return.
            nocache: If ``True``, bypass the cache and run a fresh lookup.

        Returns:
            A :class:`Person` with the enrichment results.
        """
        params: dict[str, Any] = {}
        if fields:
            params["fields"] = ",".join(fields)
        if nocache:
            params["nocache"] = "1"

        data = self._post("/api/agent/lookup", {"email": email}, params=params)
        return Person.from_dict(data)

    def validate(self, email: str) -> Validation:
        """Validate an email address (free — no credits used)."""
        data = self._post("/api/agent/validate", {"email": email})
        return Validation.from_dict(data)

    def breaches(self, email: str) -> BreachReport:
        """Check data breach exposure for an email (free — no credits used)."""
        data = self._post("/api/agent/breaches", {"email": email})
        return BreachReport.from_dict(data)

    def lookup_many(
        self,
        emails: Sequence[str],
        *,
        fields: Sequence[str] | None = None,
        nocache: bool = False,
        return_exceptions: bool = False,
        max_workers: int = 10,
    ) -> list[Person | BaseException]:
        """Look up many emails concurrently using a thread pool.

        Results are returned in the same order as ``emails``. Set
        ``return_exceptions=True`` to get failures inline instead of raising
        (so one bad email doesn't discard the results you already paid for).
        """
        items = list(emails)
        if not items:
            return []

        def _one(email: str) -> Person:
            return self.lookup(email, fields=fields, nocache=nocache)

        workers = max(1, min(max_workers, len(items)))
        with ThreadPoolExecutor(max_workers=workers) as pool:
            futures = [pool.submit(_one, email) for email in items]
            results: list[Person | BaseException] = []
            for future in futures:
                try:
                    results.append(future.result())
                except BaseException as exc:  # noqa: BLE001
                    if not return_exceptions:
                        raise
                    results.append(exc)
            return results

    # ── Monitors ──────────────────────────────────────

    def list_monitors(self) -> list[Monitor]:
        """List all monitors."""
        data = self._get("/api/agent/monitors")
        return [Monitor.from_dict(m) for m in data.get("monitors", [])]

    def create_monitor(
        self,
        name: str,
        *,
        emails: Sequence[str] | None = None,
        frequency: str = "monthly",
        change_detection: str = "diff_only",
        list_id: str | None = None,
    ) -> Monitor:
        """Create a new monitor.

        Args:
            name: Monitor name.
            emails: Email addresses to monitor.
            frequency: ``"weekly"``, ``"biweekly"``, ``"monthly"``, or ``"quarterly"``.
            change_detection: ``"diff_only"`` or ``"full_refresh"``.
            list_id: Optional contact list ID to use as the data source.
        """
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
        data = self._post("/api/agent/monitors", body)
        return Monitor.from_dict(data)

    def get_monitor(self, monitor_id: str) -> Monitor:
        """Get a monitor by ID."""
        data = self._get(f"/api/agent/monitors/{monitor_id}")
        return Monitor.from_dict(data)

    def trigger_run(self, monitor_id: str) -> dict[str, Any]:
        """Trigger an immediate monitoring run.

        Returns:
            A dict with ``run_id``, ``status``, and ``message``.
        """
        return self._post(f"/api/agent/monitors/{monitor_id}/run", {})

    def list_runs(
        self,
        monitor_id: str,
        *,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[MonitorRun], int]:
        """List runs for a specific monitor.

        Returns:
            A tuple of (runs, total_count).
        """
        data = self._get(
            f"/api/agent/monitors/{monitor_id}/runs",
            params={"limit": limit, "offset": offset},
        )
        runs = [MonitorRun.from_dict(r) for r in data.get("runs", [])]
        return runs, data.get("total", len(runs))

    def iter_runs(
        self,
        monitor_id: str,
        *,
        limit: int = 100,
        offset: int = 0,
    ) -> Iterator[MonitorRun]:
        """Yield all runs for a monitor, fetching additional pages as needed."""
        if limit <= 0:
            raise ValueError("limit must be greater than 0")

        while True:
            runs, total = self.list_runs(monitor_id, limit=limit, offset=offset)
            if not runs:
                return

            yield from runs

            offset += len(runs)
            if offset >= total:
                return

    def get_run_results(
        self,
        monitor_id: str,
        run_id: str,
        *,
        changes_only: bool = False,
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[list[MonitorSnapshot], int]:
        """Get results for a specific run.

        Returns:
            A tuple of (snapshots, total_count).
        """
        params: dict[str, Any] = {"limit": limit, "offset": offset}
        if changes_only:
            params["changes_only"] = "true"
        data = self._get(
            f"/api/agent/monitors/{monitor_id}/runs/{run_id}/results",
            params=params,
        )
        snapshots = [MonitorSnapshot.from_dict(s) for s in data.get("results", [])]
        return snapshots, data.get("total", len(snapshots))

    def iter_run_results(
        self,
        monitor_id: str,
        run_id: str,
        *,
        changes_only: bool = False,
        limit: int = 100,
        offset: int = 0,
    ) -> Iterator[MonitorSnapshot]:
        """Yield all results for a run, fetching additional pages as needed."""
        if limit <= 0:
            raise ValueError("limit must be greater than 0")

        while True:
            snapshots, total = self.get_run_results(
                monitor_id,
                run_id,
                changes_only=changes_only,
                limit=limit,
                offset=offset,
            )
            if not snapshots:
                return

            yield from snapshots

            offset += len(snapshots)
            if offset >= total:
                return

    def list_all_runs(
        self,
        *,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[MonitorRun], int]:
        """List all runs across all monitors.

        Returns:
            A tuple of (runs, total_count).
        """
        data = self._get(
            "/api/agent/monitoring/runs",
            params={"limit": limit, "offset": offset},
        )
        runs = [MonitorRun.from_dict(r) for r in data.get("runs", [])]
        return runs, data.get("total", len(runs))

    def iter_all_runs(
        self,
        *,
        limit: int = 100,
        offset: int = 0,
    ) -> Iterator[MonitorRun]:
        """Yield all runs across monitors, fetching additional pages as needed."""
        if limit <= 0:
            raise ValueError("limit must be greater than 0")

        while True:
            runs, total = self.list_all_runs(limit=limit, offset=offset)
            if not runs:
                return

            yield from runs

            offset += len(runs)
            if offset >= total:
                return

    def list_all_results(
        self,
        *,
        changes_only: bool = False,
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[list[MonitorSnapshot], int]:
        """List all enrichment results across all monitors.

        Returns:
            A tuple of (snapshots, total_count).
        """
        params: dict[str, Any] = {"limit": limit, "offset": offset}
        if changes_only:
            params["changes_only"] = "true"
        data = self._get("/api/agent/monitoring/results", params=params)
        snapshots = [MonitorSnapshot.from_dict(s) for s in data.get("results", [])]
        return snapshots, data.get("total", len(snapshots))

    def iter_all_results(
        self,
        *,
        changes_only: bool = False,
        limit: int = 100,
        offset: int = 0,
    ) -> Iterator[MonitorSnapshot]:
        """Yield all results across monitors, fetching additional pages as needed."""
        if limit <= 0:
            raise ValueError("limit must be greater than 0")

        while True:
            snapshots, total = self.list_all_results(
                changes_only=changes_only,
                limit=limit,
                offset=offset,
            )
            if not snapshots:
                return

            yield from snapshots

            offset += len(snapshots)
            if offset >= total:
                return

    # ── Contact Lists ─────────────────────────────────

    def list_contact_lists(self) -> list[ContactList]:
        """List all contact lists."""
        data = self._get("/api/agent/lists")
        if isinstance(data, list):
            return [ContactList.from_dict(cl) for cl in data]
        return [ContactList.from_dict(cl) for cl in data.get("lists", data)]

    def create_contact_list(
        self,
        name: str,
        *,
        emails: Sequence[str] | None = None,
    ) -> ContactList:
        """Create a new contact list.

        Args:
            name: List name.
            emails: Optional initial emails to add.
        """
        body: dict[str, Any] = {"name": name}
        if emails:
            body["emails"] = list(emails)
        data = self._post("/api/agent/lists", body)
        return ContactList.from_dict(data)

    def get_contact_list(self, list_id: str) -> ContactList:
        """Get a contact list by ID."""
        data = self._get(f"/api/agent/lists/{list_id}")
        return ContactList.from_dict(data)

    def delete_contact_list(self, list_id: str) -> None:
        """Delete a contact list."""
        self._delete(f"/api/agent/lists/{list_id}")

    def list_contact_list_emails(self, list_id: str) -> list[str]:
        """List all emails in a contact list."""
        data = self._get(f"/api/agent/lists/{list_id}/emails")
        if isinstance(data, list):
            return [e.get("email", e) if isinstance(e, dict) else e for e in data]
        return data.get("emails", [])

    def add_contact_list_emails(self, list_id: str, emails: Sequence[str]) -> int:
        """Add emails to a contact list. Returns count of emails added."""
        data = self._post(f"/api/agent/lists/{list_id}/emails", {"emails": list(emails)})
        return data.get("added", 0)

    def delete_contact_list_emails(self, list_id: str, emails: Sequence[str]) -> int:
        """Remove emails from a contact list. Returns count of emails removed."""
        data = self._request(
            "DELETE",
            f"/api/agent/lists/{list_id}/emails",
            body={"emails": list(emails)},
        )
        return data.get("deleted", 0)

    # ── Internals ─────────────────────────────────────

    def _get(
        self,
        path: str,
        *,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
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
                # Read/connect timeout — retry, then give up.
                if attempt < self.max_retries:
                    self._sleep_backoff(attempt, None)
                    attempt += 1
                    continue
                raise APIConnectionError(
                    f"Request timed out after {self.timeout}s"
                ) from e
            except httpx.RequestError as e:
                # Network blip / connection error — retry.
                if attempt < self.max_retries:
                    self._sleep_backoff(attempt, None)
                    attempt += 1
                    continue
                raise APIConnectionError(f"Connection error: {e}") from e

            # Retry only transient server/rate-limit errors.
            if (
                resp.status_code in _RETRYABLE_STATUS_CODES
                and attempt < self.max_retries
            ):
                self._sleep_backoff(attempt, resp)
                attempt += 1
                continue

            if resp.status_code >= 400:
                raise self._to_error(resp)

            if not resp.content:
                return {}
            return resp.json()

    def _sleep_backoff(self, attempt: int, resp: httpx.Response | None) -> None:
        """Wait before the next retry: honour Retry-After, else full jitter."""
        # If the server tells us how long to wait (429/503), respect it —
        # but never longer than the ceiling.
        if resp is not None:
            retry_after = _parse_retry_after(resp.headers.get("Retry-After"))
            if retry_after is not None:
                time.sleep(min(retry_after, _MAX_BACKOFF))
                return
        time.sleep(self._backoff_delay(attempt))

    def _backoff_delay(self, attempt: int) -> float:
        """Full-jitter exponential backoff, capped at MAX_BACKOFF.

        Returns a random delay in ``[0, min(base * factor**attempt, cap)]`` so
        that many clients retrying at once spread their load instead of
        spiking together (the AWS "full jitter" strategy).
        """
        ceiling = min(_INITIAL_BACKOFF * (_BACKOFF_FACTOR ** attempt), _MAX_BACKOFF)
        return random.uniform(0, ceiling)

    def _to_error(self, resp: httpx.Response) -> Exception:
        """Map an HTTP status code to the right exception."""
        try:
            err = resp.json()
        except ValueError:
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
