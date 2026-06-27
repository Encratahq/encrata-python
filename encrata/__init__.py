"""Encrata — Email intelligence API for Python."""

from ._version import __version__
from .client import Encrata
from .async_client import AsyncEncrata
from .types import (
    BreachInfo,
    BreachReport,
    ContactList,
    Monitor,
    MonitorRun,
    MonitorSnapshot,
    NewsArticle,
    Person,
    Publication,
    RegisteredServices,
    Socials,
    Validation,
)
from .exceptions import (
    APIConnectionError,
    APIError,
    AuthenticationError,
    EncrataError,
    InsufficientCreditsError,
    InvalidRequestError,
    RateLimitError,
)

__all__ = [
    # Client
    "Encrata",
    "AsyncEncrata",
    # Types
    "Person",
    "Socials",
    "BreachInfo",
    "BreachReport",
    "NewsArticle",
    "Publication",
    "RegisteredServices",
    "Validation",
    "Monitor",
    "MonitorRun",
    "MonitorSnapshot",
    "ContactList",
    # Exceptions
    "EncrataError",
    "AuthenticationError",
    "InsufficientCreditsError",
    "InvalidRequestError",
    "RateLimitError",
    "APIConnectionError",
    "APIError",
    # Metadata
    "__version__",
]
