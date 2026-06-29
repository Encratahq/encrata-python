"""Public dataclass types for the Encrata SDK."""

from __future__ import annotations

from .person import (
    BreachInfo,
    BreachReport,
    NewsArticle,
    Person,
    Publication,
    RegisteredServices,
    Socials,
    Validation,
)
from .osint import (
    CompanyInfo,
    CompanyOfficer,
    CompanyProfile,
    CompanyResult,
    CompanyShareholder,
    DarkWebResult,
    DarkWebSearch,
    DomainInfo,
    DomainSSL,
    DomainThreatIntel,
    DomainWhois,
    GoogleResult,
    GoogleSearch,
    IPASN,
    IPCompany,
    IPInfo,
    IPLocation,
    IPThreat,
    PhoneBreaches,
    PhoneCarrier,
    PhoneCountry,
    PhoneFormat,
    PhoneInfo,
    PhoneMessaging,
    PhoneRegistration,
    PhoneRisk,
    PhoneValidation,
)
from .web import ExtractResult, ScrapeResult, ScreenshotResult
from .monitors import ContactList, Monitor, MonitorRun, MonitorSnapshot
from .face import FaceMatch, FaceSearch
from .bulk import BulkSearchResponse
from .workflows import Workflow, WorkflowRun, WorkflowRunStep, WorkflowSecret, WorkflowStep, WorkflowTemplate
from .keys import ApiKey

__all__ = [
    # People
    "Socials",
    "BreachInfo",
    "RegisteredServices",
    "NewsArticle",
    "Publication",
    "Person",
    "Validation",
    "BreachReport",
    # IP
    "IPLocation",
    "IPASN",
    "IPCompany",
    "IPThreat",
    "IPInfo",
    # Phone
    "PhoneFormat",
    "PhoneCountry",
    "PhoneCarrier",
    "PhoneMessaging",
    "PhoneValidation",
    "PhoneRegistration",
    "PhoneRisk",
    "PhoneBreaches",
    "PhoneInfo",
    # Domain
    "DomainWhois",
    "DomainSSL",
    "DomainThreatIntel",
    "DomainInfo",
    # Company
    "CompanyResult",
    "CompanyOfficer",
    "CompanyShareholder",
    "CompanyProfile",
    "CompanyInfo",
    # Google
    "GoogleResult",
    "GoogleSearch",
    # Dark web
    "DarkWebResult",
    "DarkWebSearch",
    # Face
    "FaceMatch",
    "FaceSearch",
    "BulkSearchResponse",
    "Workflow",
    "WorkflowStep",
    "WorkflowRun",
    "WorkflowRunStep",
    "WorkflowTemplate",
    "WorkflowSecret",
    "ApiKey",
    # Web tools
    "ScrapeResult",
    "ExtractResult",
    "ScreenshotResult",
    # Monitoring & contacts
    "Monitor",
    "MonitorRun",
    "MonitorSnapshot",
    "ContactList",
]
