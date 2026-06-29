from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Socials:
    """Social media profiles."""
    linkedin: str | None = None
    twitter: str | None = None
    instagram: str | None = None
    facebook: str | None = None
    github: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> Socials | None:
        if not data:
            return None
        return cls(
            linkedin=data.get("linkedin"),
            twitter=data.get("twitter"),
            instagram=data.get("instagram"),
            facebook=data.get("facebook"),
            github=data.get("github"),
        )


@dataclass
class BreachInfo:
    """Data breach exposure information."""
    count: int = 0
    services: list[str] = field(default_factory=list)
    exposed_data: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> BreachInfo | None:
        if not data:
            return None
        return cls(
            count=data.get("count", 0),
            services=data.get("services", []),
            exposed_data=data.get("exposed_data", []),
        )


@dataclass
class RegisteredServices:
    """Services where the email is registered."""
    count: int = 0
    services: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> RegisteredServices | None:
        if not data:
            return None
        return cls(
            count=data.get("count", 0),
            services=data.get("services", []),
        )


@dataclass
class NewsArticle:
    """A news mention."""
    title: str = ""
    url: str = ""
    date: str = ""
    source: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> NewsArticle:
        return cls(
            title=data.get("title", ""),
            url=data.get("url", ""),
            date=data.get("date", ""),
            source=data.get("source", ""),
        )


@dataclass
class Publication:
    """An academic publication."""
    title: str = ""
    url: str = ""
    year: int | None = None
    citations: int = 0

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Publication:
        return cls(
            title=data.get("title", ""),
            url=data.get("url", ""),
            year=data.get("year"),
            citations=data.get("citations", 0),
        )


@dataclass
class Person:
    """Complete person intelligence from an email lookup."""
    name: str | None = None
    email: str | None = None
    company: str | None = None
    role: str | None = None
    industry: str | None = None
    location: str | None = None
    birthplace: str | None = None
    current_location: str | None = None
    bio: str | None = None
    age: str | None = None
    gender: str | None = None
    education: str | None = None
    phone: str | None = None
    photo_url: str | None = None
    validity: str | None = None
    socials: Socials | None = None
    breaches: BreachInfo | None = None
    registered_services: RegisteredServices | None = None
    news: list[NewsArticle] = field(default_factory=list)
    publications: list[Publication] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Person:
        news = [NewsArticle.from_dict(n) for n in data.get("news", [])]
        pubs = [Publication.from_dict(p) for p in data.get("publications", [])]

        return cls(
            name=data.get("name"),
            email=data.get("email"),
            company=data.get("company"),
            role=data.get("role"),
            industry=data.get("industry"),
            location=data.get("location"),
            birthplace=data.get("birthplace"),
            current_location=data.get("current_location"),
            bio=data.get("bio"),
            age=data.get("age"),
            gender=data.get("gender"),
            education=data.get("education"),
            phone=data.get("phone"),
            photo_url=data.get("photo"),
            validity=data.get("validity"),
            socials=Socials.from_dict(data.get("socials")),
            breaches=BreachInfo.from_dict(data.get("breaches")),
            registered_services=RegisteredServices.from_dict(data.get("registered_services")),
            news=news,
            publications=pubs,
        )


@dataclass
class Validation:
    """Email validation result."""
    email: str
    validity: str
    message: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Validation:
        return cls(
            email=data.get("email", ""),
            validity=data.get("validity", "unknown"),
            message=data.get("message", ""),
        )


@dataclass
class BreachReport:
    """Breach check result."""
    email: str
    count: int
    services: list[str]
    exposed_data: list[str]
    message: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> BreachReport:
        return cls(
            email=data.get("email", ""),
            count=data.get("count", 0),
            services=data.get("services", []),
            exposed_data=data.get("exposed_data", []),
            message=data.get("message", ""),
        )


# ── IP Intelligence Types ─────────────────────────────────────────────


@dataclass
class IPLocation:
    """Geolocation for an IP address."""
    city: str = ""
    region: str = ""
    country: str = ""
    country_code: str = ""
    postal_code: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> IPLocation | None:
        if not data:
            return None
        return cls(
            city=data.get("city", ""),
            region=data.get("region", ""),
            country=data.get("country", ""),
            country_code=data.get("country_code", ""),
            postal_code=data.get("postal_code", ""),
        )


@dataclass
class IPASN:
    """Autonomous-system information for an IP address."""
    number: int = 0
    org: str = ""
    isp: str = ""
    type: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> IPASN | None:
        if not data:
            return None
        return cls(
            number=data.get("number", 0),
            org=data.get("org", ""),
            isp=data.get("isp", ""),
            type=data.get("type", ""),
        )


@dataclass
class IPCompany:
    """Company associated with an IP address."""
    name: str = ""
    domain: str = ""
    type: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> IPCompany | None:
        if not data:
            return None
        return cls(
            name=data.get("name", ""),
            domain=data.get("domain", ""),
            type=data.get("type", ""),
        )


@dataclass
class IPThreat:
    """Threat indicators for an IP address."""
    is_tor: bool = False
    is_proxy: bool = False
    is_vpn: bool = False
    is_abuser: bool = False
    is_bot: bool = False

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> IPThreat | None:
        if not data:
            return None
        return cls(
            is_tor=data.get("is_tor", False),
            is_proxy=data.get("is_proxy", False),
            is_vpn=data.get("is_vpn", False),
            is_abuser=data.get("is_abuser", False),
            is_bot=data.get("is_bot", False),
        )


@dataclass
class IPInfo:
    """IP intelligence result: geolocation, ASN, company, and threat data."""
    query: str = ""
    ip: str = ""
    location: IPLocation | None = None
    asn: IPASN | None = None
    company: IPCompany | None = None
    threat: IPThreat | None = None
    credits: float = 0.0

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> IPInfo:
        return cls(
            query=data.get("query", ""),
            ip=data.get("ip", ""),
            location=IPLocation.from_dict(data.get("location")),
            asn=IPASN.from_dict(data.get("asn")),
            company=IPCompany.from_dict(data.get("company")),
            threat=IPThreat.from_dict(data.get("threat")),
            credits=data.get("credits", 0.0),
        )


# ── Phone Intelligence Types ──────────────────────────────────────────


@dataclass
class PhoneFormat:
    """Phone number formats."""
    international: str = ""
    local: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> PhoneFormat | None:
        if not data:
            return None
        return cls(international=data.get("international", ""), local=data.get("local", ""))


@dataclass
class PhoneCountry:
    """Country and location details for a phone number."""
    code: str = ""
    name: str = ""
    prefix: str = ""
    region: str = ""
    city: str = ""
    timezone: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> PhoneCountry | None:
        if not data:
            return None
        return cls(
            code=data.get("code", ""),
            name=data.get("name", ""),
            prefix=data.get("prefix", ""),
            region=data.get("region", ""),
            city=data.get("city", ""),
            timezone=data.get("timezone", ""),
        )


@dataclass
class PhoneCarrier:
    """Carrier information."""
    name: str = ""
    line_type: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> PhoneCarrier | None:
        if not data:
            return None
        return cls(name=data.get("name", ""), line_type=data.get("line_type", ""))


@dataclass
class PhoneMessaging:
    """SMS gateway information."""
    sms_domain: str = ""
    sms_email: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> PhoneMessaging | None:
        if not data:
            return None
        return cls(sms_domain=data.get("sms_domain", ""), sms_email=data.get("sms_email", ""))


@dataclass
class PhoneValidation:
    """Validation and activity signals."""
    is_valid: bool = False
    line_status: str = ""
    is_voip: bool = False
    minimum_age: int = 0

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> PhoneValidation | None:
        if not data:
            return None
        return cls(
            is_valid=data.get("is_valid", False),
            line_status=data.get("line_status", ""),
            is_voip=data.get("is_voip", False),
            minimum_age=data.get("minimum_age", 0),
        )


@dataclass
class PhoneRegistration:
    """Registration information."""
    name: str = ""
    type: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> PhoneRegistration | None:
        if not data:
            return None
        return cls(name=data.get("name", ""), type=data.get("type", ""))


@dataclass
class PhoneRisk:
    """Risk assessment for a phone number."""
    risk_level: str = ""
    is_disposable: bool = False
    is_abuse_detected: bool = False

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> PhoneRisk | None:
        if not data:
            return None
        return cls(
            risk_level=data.get("risk_level", ""),
            is_disposable=data.get("is_disposable", False),
            is_abuse_detected=data.get("is_abuse_detected", False),
        )


@dataclass
class PhoneBreaches:
    """Breach exposure data for a phone number."""
    total_breaches: int = 0
    date_first_breached: str = ""
    date_last_breached: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> PhoneBreaches | None:
        if not data:
            return None
        return cls(
            total_breaches=data.get("total_breaches", 0),
            date_first_breached=data.get("date_first_breached", ""),
            date_last_breached=data.get("date_last_breached", ""),
        )


@dataclass
class PhoneInfo:
    """Phone intelligence result: carrier, format, country, validation, risk, and breaches."""
    query: str = ""
    phone: str = ""
    valid: bool = False
    location: str = ""
    type: str = ""
    format: PhoneFormat | None = None
    country: PhoneCountry | None = None
    carrier: PhoneCarrier | None = None
    messaging: PhoneMessaging | None = None
    validation: PhoneValidation | None = None
    registration: PhoneRegistration | None = None
    risk: PhoneRisk | None = None
    breaches: PhoneBreaches | None = None
    credits: float = 0.0

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PhoneInfo:
        return cls(
            query=data.get("query", ""),
            phone=data.get("phone", ""),
            valid=data.get("valid", False),
            location=data.get("location", ""),
            type=data.get("type", ""),
            format=PhoneFormat.from_dict(data.get("format")),
            country=PhoneCountry.from_dict(data.get("country")),
            carrier=PhoneCarrier.from_dict(data.get("carrier")),
            messaging=PhoneMessaging.from_dict(data.get("messaging")),
            validation=PhoneValidation.from_dict(data.get("validation")),
            registration=PhoneRegistration.from_dict(data.get("registration")),
            risk=PhoneRisk.from_dict(data.get("risk")),
            breaches=PhoneBreaches.from_dict(data.get("breaches")),
            credits=data.get("credits", 0.0),
        )


# ── Domain Intelligence Types ─────────────────────────────────────────


@dataclass
class DomainWhois:
    """WHOIS registration data."""
    registrar: str = ""
    created: str = ""
    expires: str = ""
    name_servers: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> DomainWhois | None:
        if not data:
            return None
        return cls(
            registrar=data.get("registrar", ""),
            created=data.get("created", ""),
            expires=data.get("expires", ""),
            name_servers=data.get("name_servers", []),
        )


@dataclass
class DomainSSL:
    """SSL/TLS certificate details."""
    issuer: str = ""
    valid_from: str = ""
    valid_to: str = ""
    subject_alt_names: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> DomainSSL | None:
        if not data:
            return None
        return cls(
            issuer=data.get("issuer", ""),
            valid_from=data.get("valid_from", ""),
            valid_to=data.get("valid_to", ""),
            subject_alt_names=data.get("subject_alt_names", []),
        )


@dataclass
class DomainThreatIntel:
    """Reputation / threat indicators for the domain."""
    malicious: bool = False
    categories: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> DomainThreatIntel | None:
        if not data:
            return None
        return cls(
            malicious=data.get("malicious", False),
            categories=data.get("categories", []),
        )


@dataclass
class DomainInfo:
    """Domain intelligence: WHOIS, DNS, SSL, threat data, and deep recon.

    The ``intel``, ``company``, ``report``, and ``extras`` blocks are returned as
    raw dicts because their structure is deep and source-dependent.
    """
    domain: str = ""
    whois: DomainWhois | None = None
    dns: dict[str, Any] | None = None
    ssl: DomainSSL | None = None
    threat_intel: DomainThreatIntel | None = None
    intel: dict[str, Any] | None = None
    company: dict[str, Any] | None = None
    report: dict[str, Any] | None = None
    extras: dict[str, Any] | None = None
    credits: float = 0.0

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> DomainInfo:
        return cls(
            domain=data.get("domain", ""),
            whois=DomainWhois.from_dict(data.get("whois")),
            dns=data.get("dns"),
            ssl=DomainSSL.from_dict(data.get("ssl")),
            threat_intel=DomainThreatIntel.from_dict(data.get("threat_intel")),
            intel=data.get("intel"),
            company=data.get("company"),
            report=data.get("report"),
            extras=data.get("extras"),
            credits=data.get("credits", 0.0),
        )


# ── Company Search Types ──────────────────────────────────────────────


@dataclass
class CompanyResult:
    """A person found at a company."""
    email: str | None = None
    name: str | None = None
    role: str | None = None
    linkedin: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CompanyResult:
        return cls(
            email=data.get("email"),
            name=data.get("name"),
            role=data.get("role"),
            linkedin=data.get("linkedin"),
        )


@dataclass
class CompanyOfficer:
    """A company officer (director, secretary)."""
    name: str | None = None
    role: str | None = None
    appointed_on: str | None = None
    nationality: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CompanyOfficer:
        return cls(
            name=data.get("name"),
            role=data.get("role"),
            appointed_on=data.get("appointed_on"),
            nationality=data.get("nationality"),
        )


@dataclass
class CompanyShareholder:
    """A person with significant control (PSC)."""
    name: str | None = None
    natures_of_control: list[str] = field(default_factory=list)
    nationality: str | None = None
    notified_on: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CompanyShareholder:
        return cls(
            name=data.get("name"),
            natures_of_control=data.get("natures_of_control") or [],
            nationality=data.get("nationality"),
            notified_on=data.get("notified_on"),
        )


@dataclass
class CompanyProfile:
    """Unified company profile merged from multiple sources."""
    name: str | None = None
    domain: str | None = None
    description: str | None = None
    founding_date: str | None = None
    industry: str | None = None
    company_type: str | None = None
    status: str | None = None
    employee_count: int | None = None
    revenue: str | None = None
    total_funding: str | None = None
    address: str | None = None
    country: str | None = None
    phone: str | None = None
    website: str | None = None
    logo: str | None = None
    linkedin: str | None = None
    twitter: str | None = None
    ticker: str | None = None
    registration_number: str | None = None
    jurisdiction: str | None = None
    sic_codes: list[str] = field(default_factory=list)
    officers: list[CompanyOfficer] = field(default_factory=list)
    shareholders: list[CompanyShareholder] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> CompanyProfile | None:
        if not data:
            return None
        return cls(
            name=data.get("name"),
            domain=data.get("domain"),
            description=data.get("description"),
            founding_date=data.get("founding_date"),
            industry=data.get("industry"),
            company_type=data.get("company_type"),
            status=data.get("status"),
            employee_count=data.get("employee_count"),
            revenue=data.get("revenue"),
            total_funding=data.get("total_funding"),
            address=data.get("address"),
            country=data.get("country"),
            phone=data.get("phone"),
            website=data.get("website"),
            logo=data.get("logo"),
            linkedin=data.get("linkedin"),
            twitter=data.get("twitter"),
            ticker=data.get("ticker"),
            registration_number=data.get("registration_number"),
            jurisdiction=data.get("jurisdiction"),
            sic_codes=data.get("sic_codes") or [],
            officers=[CompanyOfficer.from_dict(o) for o in data.get("officers", [])],
            shareholders=[CompanyShareholder.from_dict(s) for s in data.get("shareholders", [])],
        )


@dataclass
class CompanyInfo:
    """Company search result: people found plus a unified company profile."""
    company: str = ""
    results: list[CompanyResult] = field(default_factory=list)
    profile: CompanyProfile | None = None
    total: int = 0
    credits: float = 0.0

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CompanyInfo:
        return cls(
            company=data.get("company", ""),
            results=[CompanyResult.from_dict(r) for r in data.get("results", [])],
            profile=CompanyProfile.from_dict(data.get("profile")),
            total=data.get("total", 0),
            credits=data.get("credits", 0.0),
        )


# ── Monitoring Types ──────────────────────────────────────────────────


@dataclass
class Monitor:
    """A monitoring configuration."""
    id: str = ""
    name: str = ""
    status: str = ""
    frequency: str = ""
    change_detection: str = ""
    data_source_type: str = ""
    data_source_ref: str = ""
    email_count: int = 0
    tracked_fields: list[str] = field(default_factory=list)
    last_run_at: str | None = None
    next_run_at: str | None = None
    created_at: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Monitor:
        return cls(
            id=data.get("id", ""),
            name=data.get("name", ""),
            status=data.get("status", ""),
            frequency=data.get("frequency", ""),
            change_detection=data.get("change_detection", ""),
            data_source_type=data.get("data_source_type", ""),
            data_source_ref=data.get("data_source_ref", ""),
            email_count=data.get("email_count", 0),
            tracked_fields=data.get("tracked_fields") or [],
            last_run_at=data.get("last_run_at"),
            next_run_at=data.get("next_run_at"),
            created_at=data.get("created_at", ""),
        )


@dataclass
class MonitorRun:
    """A monitoring run."""
    id: str = ""
    monitor_id: str = ""
    monitor_name: str = ""
    status: str = ""
    total_records: int = 0
    changes_detected: int = 0
    credits_used: int = 0
    started_at: str | None = None
    completed_at: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> MonitorRun:
        return cls(
            id=data.get("id", ""),
            monitor_id=data.get("monitor_id", ""),
            monitor_name=data.get("monitor_name", ""),
            status=data.get("status", ""),
            total_records=data.get("total_records", 0),
            changes_detected=data.get("changes_detected", 0),
            credits_used=data.get("credits_used", 0),
            started_at=data.get("started_at"),
            completed_at=data.get("completed_at"),
        )


@dataclass
class MonitorSnapshot:
    """An enrichment result snapshot from a monitoring run."""
    id: str = ""
    email: str = ""
    has_changes: bool = False
    changes: Any = None
    data: Any = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> MonitorSnapshot:
        return cls(
            id=data.get("id", ""),
            email=data.get("email", ""),
            has_changes=data.get("has_changes", False),
            changes=data.get("changes"),
            data=data.get("data"),
        )


@dataclass
class ContactList:
    """A contact list."""
    id: str = ""
    name: str = ""
    email_count: int = 0
    created_at: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ContactList:
        return cls(
            id=data.get("id", ""),
            name=data.get("name", ""),
            email_count=data.get("email_count", 0),
            created_at=data.get("created_at", ""),
        )
