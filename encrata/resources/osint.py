"""OSINT lookups: IP, phone, domain, company, Google dork, dark web."""

from __future__ import annotations

from ..types import (
    CompanyInfo,
    DarkWebSearch,
    DomainInfo,
    GoogleSearch,
    IPInfo,
    PhoneInfo,
)


class OSINTSyncMixin:
    def ip(self, ip: str) -> IPInfo:
        """Look up geolocation, ASN, company, and threat data for an IP address."""
        data = self._post("/api/agent/ip", {"ip": ip})
        return IPInfo.from_dict(data)

    def phone_lookup(self, query: str) -> PhoneInfo:
        """Look up carrier, format, country, validation, risk, and breach data for a phone number."""
        data = self._post("/api/agent/phone", {"query": query})
        return PhoneInfo.from_dict(data)

    def domain_search(self, query: str) -> DomainInfo:
        """Look up WHOIS, DNS, SSL, threat intel, and recon data for a domain."""
        data = self._post("/api/agent/domain", {"query": query})
        return DomainInfo.from_dict(data)

    def company_search(self, query: str) -> CompanyInfo:
        """Find people and a unified company profile by company name."""
        data = self._post("/api/agent/company", {"query": query})
        return CompanyInfo.from_dict(data)

    def google_search(self, query: str) -> GoogleSearch:
        """Run a Google dork query with free OSINT enrichment."""
        data = self._post("/api/agent/google", {"query": query})
        return GoogleSearch.from_dict(data)

    def darkweb_search(self, query: str, *, offset: int = 0) -> DarkWebSearch:
        """Search dark web intelligence for leaks, forums, markets, and chat mentions."""
        data = self._post("/api/agent/darkweb", {"query": query, "offset": offset})
        return DarkWebSearch.from_dict(data)


class OSINTAsyncMixin:
    async def ip(self, ip: str) -> IPInfo:
        """Look up geolocation, ASN, company, and threat data for an IP address."""
        data = await self._post("/api/agent/ip", {"ip": ip})
        return IPInfo.from_dict(data)

    async def phone_lookup(self, query: str) -> PhoneInfo:
        """Look up carrier, format, country, validation, risk, and breach data for a phone number."""
        data = await self._post("/api/agent/phone", {"query": query})
        return PhoneInfo.from_dict(data)

    async def domain_search(self, query: str) -> DomainInfo:
        """Look up WHOIS, DNS, SSL, threat intel, and recon data for a domain."""
        data = await self._post("/api/agent/domain", {"query": query})
        return DomainInfo.from_dict(data)

    async def company_search(self, query: str) -> CompanyInfo:
        """Find people and a unified company profile by company name."""
        data = await self._post("/api/agent/company", {"query": query})
        return CompanyInfo.from_dict(data)

    async def google_search(self, query: str) -> GoogleSearch:
        """Run a Google dork query with free OSINT enrichment."""
        data = await self._post("/api/agent/google", {"query": query})
        return GoogleSearch.from_dict(data)

    async def darkweb_search(self, query: str, *, offset: int = 0) -> DarkWebSearch:
        """Search dark web intelligence for leaks, forums, markets, and chat mentions."""
        data = await self._post("/api/agent/darkweb", {"query": query, "offset": offset})
        return DarkWebSearch.from_dict(data)
