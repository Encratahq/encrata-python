"""Web tool types: scrape, extract, screenshot."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class ScrapeResult:
    """Scraped page content as clean markdown plus status and metadata."""
    success: bool = False
    url: str = ""
    status_code: int = 0
    content: str = ""
    metadata: dict[str, Any] | None = None
    credits: float = 0.0
    latency_ms: int = 0

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ScrapeResult:
        return cls(
            success=data.get("success", False),
            url=data.get("url", ""),
            status_code=data.get("status_code", 0),
            content=data.get("content", ""),
            metadata=data.get("metadata"),
            credits=data.get("credits", 0.0),
            latency_ms=data.get("latency_ms", 0),
        )


@dataclass
class ExtractResult:
    """Extracted page data — markdown content or selector-keyed JSON.

    ``extracted`` is a markdown string in ``markdown`` mode, or a dict keyed by
    your selectors in ``selectors`` mode.
    """
    success: bool = False
    url: str = ""
    status_code: int = 0
    extracted: Any = None
    metadata: dict[str, Any] | None = None
    error_code: str | None = None
    error: str | None = None
    credits: float = 0.0
    latency_ms: int = 0

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ExtractResult:
        return cls(
            success=data.get("success", False),
            url=data.get("url", ""),
            status_code=data.get("status_code", 0),
            extracted=data.get("extracted"),
            metadata=data.get("metadata"),
            error_code=data.get("error_code"),
            error=data.get("error"),
            credits=data.get("credits", 0.0),
            latency_ms=data.get("latency_ms", 0),
        )


@dataclass
class ScreenshotResult:
    """A captured page screenshot as base64-encoded image data."""
    success: bool = False
    url: str = ""
    status_code: int = 0
    screenshot: str = ""
    format: str = ""
    metadata: dict[str, Any] | None = None
    error_code: str | None = None
    error: str | None = None
    credits: float = 0.0
    latency_ms: int = 0

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ScreenshotResult:
        return cls(
            success=data.get("success", False),
            url=data.get("url", ""),
            status_code=data.get("status_code", 0),
            screenshot=data.get("screenshot", ""),
            format=data.get("format", ""),
            metadata=data.get("metadata"),
            error_code=data.get("error_code"),
            error=data.get("error"),
            credits=data.get("credits", 0.0),
            latency_ms=data.get("latency_ms", 0),
        )
