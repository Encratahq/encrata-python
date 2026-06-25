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
