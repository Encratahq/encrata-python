"""Synchronous Encrata API client."""

from __future__ import annotations

import httpx

from ._constants import (
    DEFAULT_BASE_URL as _DEFAULT_BASE_URL,
    MAX_RETRIES as _MAX_RETRIES,
    USER_AGENT as _USER_AGENT,
)
from ._http import SyncHTTPMixin
from .exceptions import AuthenticationError
from .resources.bulk import BulkSyncMixin
from .resources.contacts import ContactsSyncMixin
from .resources.face import FaceSyncMixin
from .resources.monitors import MonitorsSyncMixin
from .resources.osint import OSINTSyncMixin
from .resources.people import PeopleSyncMixin
from .resources.web import WebSyncMixin

__all__ = ["Encrata"]


class Encrata(
    SyncHTTPMixin,
    PeopleSyncMixin,
    OSINTSyncMixin,
    WebSyncMixin,
    FaceSyncMixin,
    BulkSyncMixin,
    MonitorsSyncMixin,
    ContactsSyncMixin,
):
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
