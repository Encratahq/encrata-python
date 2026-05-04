from __future__ import annotations

import json
from typing import Any, Sequence
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode

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

__all__ = ["Encrata"]

_DEFAULT_BASE_URL = "https://api.encrata.com"

# Short field codes accepted by the API
FIELDS = {
    "name": "n",
    "email": "e",
    "company": "co",
    "role": "role",
    "industry": "ind",
    "location": "loc",
    "birthplace": "bloc",
    "current_location": "cloc",
    "bio": "bio",
    "age": "age",
    "gender": "g",
    "education": "edu",
    "phone": "ph",
    "photo": "pic",
    "validity": "v",
    "socials": "s",
    "breaches": "b",
    "registered_services": "reg",
    "news": "news",
    "publications": "pub",
}


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
    ) -> None:
        if not api_key:
            raise AuthenticationError("API key is required.")
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

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
        params = ""
        if fields:
            codes = [FIELDS.get(f, f) for f in fields]
            params += f"?fields={','.join(codes)}"
            if nocache:
                params += "&nocache=1"
        elif nocache:
            params += "?nocache=1"

        data = self._post(f"/api/agent/lookup{params}", {"e": email})
        return Person.from_dict(data)

    def validate(self, email: str) -> Validation:
        """Validate an email address (free — no credits used)."""
        data = self._post("/api/agent/validate", {"e": email})
        return Validation.from_dict(data)

    def breaches(self, email: str) -> BreachReport:
        """Check data breach exposure for an email (free — no credits used)."""
        data = self._post("/api/agent/breaches", {"e": email})
        return BreachReport.from_dict(data)

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
        if params:
            path = f"{path}?{urlencode(params)}"
        return self._request("GET", path)

    def _post(self, path: str, body: dict[str, Any]) -> dict[str, Any]:
        return self._request("POST", path, body=body)

    def _delete(self, path: str) -> dict[str, Any]:
        return self._request("DELETE", path)

    def _request(
        self,
        method: str,
        path: str,
        *,
        body: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        url = f"{self.base_url}{path}"
        payload = json.dumps(body).encode() if body else None

        req = Request(
            url,
            data=payload,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "User-Agent": "encrata-python/0.2.0",
            },
            method=method,
        )

        try:
            with urlopen(req, timeout=self.timeout) as resp:
                raw = resp.read()
                if not raw:
                    return {}
                return json.loads(raw)
        except HTTPError as e:
            body_bytes = e.read()
            try:
                err = json.loads(body_bytes)
            except (json.JSONDecodeError, ValueError):
                err = {}

            msg = err.get("m") or err.get("error") or e.reason
            code = e.code

            if code == 401:
                raise AuthenticationError(msg, status_code=code) from e
            if code == 402:
                raise InsufficientCreditsError(msg, status_code=code) from e
            if code == 400:
                raise InvalidRequestError(msg, status_code=code) from e
            if code == 429:
                raise RateLimitError(msg, status_code=code) from e
            raise APIError(msg, status_code=code) from e
        except URLError as e:
            raise APIConnectionError(f"Connection error: {e.reason}") from e
