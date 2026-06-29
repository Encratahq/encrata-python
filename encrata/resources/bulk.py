"""Bulk operations: stream-enrich up to 1,000 emails in one request (SSE)."""

from __future__ import annotations

import json
from typing import AsyncIterable, AsyncIterator, Iterable, Iterator, Sequence

from .._http import to_error
from ..types import BulkSearchResponse, Person


def _parse_sse_line(line: str) -> str | None:
    """Extract the payload from an SSE ``data:`` line, or None to skip."""
    if not line:
        return None
    if line.startswith("data:"):
        return line[5:].strip()
    return None


def _bulk_search_response_from_sse(lines: Iterable[str]) -> BulkSearchResponse:
    """Collect a bulk search SSE stream into a BulkSearchResponse."""
    results: list[dict[str, object]] = []
    credits_used = 0

    for line in lines:
        payload = _parse_sse_line(line)
        if payload is None:
            continue
        if payload == "[DONE]":
            break

        item = json.loads(payload)
        if not isinstance(item, dict):
            continue
        if "results" in item:
            data = BulkSearchResponse.from_dict(item)
            results.extend(data.results)
            credits_used = data.credits_used
            continue
        if "credits_used" in item:
            credits_used = int(item.get("credits_used") or 0)
            continue
        if set(item) <= {"total"}:
            continue
        results.append(item)

    if credits_used == 0:
        credits_used = len(results)
    return BulkSearchResponse(results=results, credits_used=credits_used)


async def _bulk_search_response_from_async_sse(
    lines: AsyncIterable[str],
) -> BulkSearchResponse:
    """Collect an async bulk search SSE stream into a BulkSearchResponse."""
    results: list[dict[str, object]] = []
    credits_used = 0

    async for line in lines:
        payload = _parse_sse_line(line)
        if payload is None:
            continue
        if payload == "[DONE]":
            break

        item = json.loads(payload)
        if not isinstance(item, dict):
            continue
        if "results" in item:
            data = BulkSearchResponse.from_dict(item)
            results.extend(data.results)
            credits_used = data.credits_used
            continue
        if "credits_used" in item:
            credits_used = int(item.get("credits_used") or 0)
            continue
        if set(item) <= {"total"}:
            continue
        results.append(item)

    if credits_used == 0:
        credits_used = len(results)
    return BulkSearchResponse(results=results, credits_used=credits_used)


class BulkSyncMixin:
    def bulk_lookup(
        self,
        emails: Sequence[str],
        *,
        fields: Sequence[str] | None = None,
    ) -> Iterator[Person]:
        """Enrich up to 1,000 emails, yielding a :class:`Person` per result as it streams.

        Results arrive via Server-Sent Events, so you can start processing the
        first hit before the rest finish. Each successful email costs 1 credit.
        """
        params = {"fields": ",".join(fields)} if fields else None
        with self._client.stream(
            "POST",
            f"{self.base_url}/api/agent/bulk-lookup",
            json={"emails": list(emails)},
            params=params,
        ) as resp:
            if resp.status_code >= 400:
                resp.read()
                raise to_error(resp)
            for line in resp.iter_lines():
                payload = _parse_sse_line(line)
                if payload is None:
                    continue
                if payload == "[DONE]":
                    break
                yield Person.from_dict(json.loads(payload))

    def bulk_google_search(self, queries: Sequence[str]) -> BulkSearchResponse:
        """Run up to 100 Google/SERP searches in one request (1 credit each)."""
        return self._bulk_search("/api/bulk-google-search", queries)

    def bulk_company_search(self, queries: Sequence[str]) -> BulkSearchResponse:
        """Enrich up to 100 companies (names or domains) in one request (1 credit each)."""
        return self._bulk_search("/api/bulk-company-search", queries)

    def bulk_domain_search(self, queries: Sequence[str]) -> BulkSearchResponse:
        """Run domain intelligence on up to 100 domains in one request (1 credit each)."""
        return self._bulk_search("/api/bulk-domain-search", queries)

    def bulk_ip_search(self, queries: Sequence[str]) -> BulkSearchResponse:
        """Run IP intelligence on up to 100 addresses in one request (1 credit each)."""
        return self._bulk_search("/api/bulk-ip-search", queries)

    def _bulk_search(self, path: str, queries: Sequence[str]) -> BulkSearchResponse:
        with self._client.stream(
            "POST",
            f"{self.base_url}{path}",
            json={"queries": list(queries)},
        ) as resp:
            if resp.status_code >= 400:
                resp.read()
                raise to_error(resp)
            return _bulk_search_response_from_sse(resp.iter_lines())


class BulkAsyncMixin:
    async def bulk_lookup(
        self,
        emails: Sequence[str],
        *,
        fields: Sequence[str] | None = None,
    ) -> AsyncIterator[Person]:
        """Enrich up to 1,000 emails, yielding a :class:`Person` per result as it streams."""
        params = {"fields": ",".join(fields)} if fields else None
        async with self._client.stream(
            "POST",
            f"{self.base_url}/api/agent/bulk-lookup",
            json={"emails": list(emails)},
            params=params,
        ) as resp:
            if resp.status_code >= 400:
                await resp.aread()
                raise to_error(resp)
            async for line in resp.aiter_lines():
                payload = _parse_sse_line(line)
                if payload is None:
                    continue
                if payload == "[DONE]":
                    break
                yield Person.from_dict(json.loads(payload))

    async def bulk_google_search(self, queries: Sequence[str]) -> BulkSearchResponse:
        """Run up to 100 Google/SERP searches in one request (1 credit each)."""
        return await self._bulk_search("/api/bulk-google-search", queries)

    async def bulk_company_search(self, queries: Sequence[str]) -> BulkSearchResponse:
        """Enrich up to 100 companies (names or domains) in one request (1 credit each)."""
        return await self._bulk_search("/api/bulk-company-search", queries)

    async def bulk_domain_search(self, queries: Sequence[str]) -> BulkSearchResponse:
        """Run domain intelligence on up to 100 domains in one request (1 credit each)."""
        return await self._bulk_search("/api/bulk-domain-search", queries)

    async def bulk_ip_search(self, queries: Sequence[str]) -> BulkSearchResponse:
        """Run IP intelligence on up to 100 addresses in one request (1 credit each)."""
        return await self._bulk_search("/api/bulk-ip-search", queries)

    async def _bulk_search(self, path: str, queries: Sequence[str]) -> BulkSearchResponse:
        async with self._client.stream(
            "POST",
            f"{self.base_url}{path}",
            json={"queries": list(queries)},
        ) as resp:
            if resp.status_code >= 400:
                await resp.aread()
                raise to_error(resp)
            return await _bulk_search_response_from_async_sse(resp.aiter_lines())
