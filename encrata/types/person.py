"""Person intelligence types."""

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
            citations=data.get("cited_by", 0),
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
            breaches=BreachInfo.from_dict(data.get("breach")),
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
