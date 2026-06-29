"""Web tools: scrape, extract, screenshot."""

from __future__ import annotations

from typing import Any

from ..types import ExtractResult, ScrapeResult, ScreenshotResult


def _build_extract_body(
    url: str,
    mode: str,
    selectors: dict[str, str] | None,
    render_js: bool,
    block_ads: bool,
    block_trackers: bool,
    wait_for: str | None,
    timeout: int | None,
    headers: dict[str, str] | None,
) -> dict[str, Any]:
    body: dict[str, Any] = {
        "url": url,
        "mode": mode,
        "render_js": render_js,
        "block_ads": block_ads,
        "block_trackers": block_trackers,
    }
    if selectors is not None:
        body["selectors"] = selectors
    if wait_for is not None:
        body["wait_for"] = wait_for
    if timeout is not None:
        body["timeout"] = timeout
    if headers is not None:
        body["headers"] = headers
    return body


def _build_screenshot_body(
    url: str,
    full_page: bool,
    format: str,
    selector: str | None,
    render_js: bool,
    block_ads: bool,
    block_trackers: bool,
    wait_for: str | None,
    timeout: int | None,
    headers: dict[str, str] | None,
) -> dict[str, Any]:
    body: dict[str, Any] = {
        "url": url,
        "full_page": full_page,
        "format": format,
        "render_js": render_js,
        "block_ads": block_ads,
        "block_trackers": block_trackers,
    }
    if selector is not None:
        body["selector"] = selector
    if wait_for is not None:
        body["wait_for"] = wait_for
    if timeout is not None:
        body["timeout"] = timeout
    if headers is not None:
        body["headers"] = headers
    return body


class WebSyncMixin:
    def scrape(self, url: str, *, render_js: bool = True) -> ScrapeResult:
        """Scrape a URL and return clean, LLM-ready markdown with metadata."""
        data = self._post("/api/agent/scrape", {"url": url, "render_js": render_js})
        return ScrapeResult.from_dict(data)

    def extract(
        self,
        url: str,
        *,
        mode: str = "markdown",
        selectors: dict[str, str] | None = None,
        render_js: bool = True,
        block_ads: bool = True,
        block_trackers: bool = True,
        wait_for: str | None = None,
        timeout: int | None = None,
        headers: dict[str, str] | None = None,
    ) -> ExtractResult:
        """Extract structured data from a page as markdown or selector-keyed JSON."""
        body = _build_extract_body(
            url, mode, selectors, render_js, block_ads, block_trackers,
            wait_for, timeout, headers,
        )
        data = self._post("/api/agent/extract", body)
        return ExtractResult.from_dict(data)

    def screenshot(
        self,
        url: str,
        *,
        full_page: bool = True,
        format: str = "png",
        selector: str | None = None,
        render_js: bool = True,
        block_ads: bool = True,
        block_trackers: bool = True,
        wait_for: str | None = None,
        timeout: int | None = None,
        headers: dict[str, str] | None = None,
    ) -> ScreenshotResult:
        """Capture a full-page screenshot of a URL as a base64 PNG or JPEG."""
        body = _build_screenshot_body(
            url, full_page, format, selector, render_js, block_ads, block_trackers,
            wait_for, timeout, headers,
        )
        data = self._post("/api/agent/screenshot", body)
        return ScreenshotResult.from_dict(data)


class WebAsyncMixin:
    async def scrape(self, url: str, *, render_js: bool = True) -> ScrapeResult:
        """Scrape a URL and return clean, LLM-ready markdown with metadata."""
        data = await self._post("/api/agent/scrape", {"url": url, "render_js": render_js})
        return ScrapeResult.from_dict(data)

    async def extract(
        self,
        url: str,
        *,
        mode: str = "markdown",
        selectors: dict[str, str] | None = None,
        render_js: bool = True,
        block_ads: bool = True,
        block_trackers: bool = True,
        wait_for: str | None = None,
        timeout: int | None = None,
        headers: dict[str, str] | None = None,
    ) -> ExtractResult:
        """Extract structured data from a page as markdown or selector-keyed JSON."""
        body = _build_extract_body(
            url, mode, selectors, render_js, block_ads, block_trackers,
            wait_for, timeout, headers,
        )
        data = await self._post("/api/agent/extract", body)
        return ExtractResult.from_dict(data)

    async def screenshot(
        self,
        url: str,
        *,
        full_page: bool = True,
        format: str = "png",
        selector: str | None = None,
        render_js: bool = True,
        block_ads: bool = True,
        block_trackers: bool = True,
        wait_for: str | None = None,
        timeout: int | None = None,
        headers: dict[str, str] | None = None,
    ) -> ScreenshotResult:
        """Capture a full-page screenshot of a URL as a base64 PNG or JPEG."""
        body = _build_screenshot_body(
            url, full_page, format, selector, render_js, block_ads, block_trackers,
            wait_for, timeout, headers,
        )
        data = await self._post("/api/agent/screenshot", body)
        return ScreenshotResult.from_dict(data)
