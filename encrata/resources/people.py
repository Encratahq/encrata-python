"""People intelligence: lookup, validate, breaches, bulk lookup."""

from __future__ import annotations

import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Sequence

from ..types import BreachReport, Person, Validation


class PeopleSyncMixin:
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


class PeopleAsyncMixin:
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
