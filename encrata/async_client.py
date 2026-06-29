"""Asynchronous Encrata API client."""

from __future__ import annotations

import asyncio

import httpx

from ._constants import (
    DEFAULT_BASE_URL,
    MAX_RETRIES,
    USER_AGENT,
)
from ._http import AsyncHTTPMixin
from .exceptions import AuthenticationError
from .resources.bulk import BulkAsyncMixin
from .resources.contacts import ContactsAsyncMixin
from .resources.face import FaceAsyncMixin
from .resources.monitors import MonitorsAsyncMixin
from .resources.osint import OSINTAsyncMixin
from .resources.people import PeopleAsyncMixin
from .resources.web import WebAsyncMixin
from .resources.workflows import WorkflowsAsyncMixin
from .resources.keys import KeysAsyncMixin

__all__ = ["AsyncEncrata"]


class AsyncEncrata(
    AsyncHTTPMixin,
    PeopleAsyncMixin,
    OSINTAsyncMixin,
    WebAsyncMixin,
    FaceAsyncMixin,
    BulkAsyncMixin,
    MonitorsAsyncMixin,
    ContactsAsyncMixin,
    WorkflowsAsyncMixin,
    KeysAsyncMixin,
):
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
