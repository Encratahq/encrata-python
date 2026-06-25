"""Test helpers: an httpx-backed mock transport.

No network calls, no API key, no credits are ever used. Queue outcomes with
``respond(...)`` / ``error(...)`` (FIFO), inject ``MockTransport.httpx_transport``
into the client, then inspect captured requests via ``body()`` / ``url()`` /
``method()`` / ``header()``.
"""

from __future__ import annotations

import json
from typing import Any

import httpx


def make_http_error(
    code: int,
    body: Any = None,
    msg: str | None = None,
    headers: dict[str, str] | None = None,
) -> httpx.Response:
    """Build an ``httpx.Response`` representing an HTTP error status."""
    kwargs: dict[str, Any] = {"headers": headers or {}}
    if body is not None:
        kwargs["json"] = body
    if msg is not None:
        kwargs["extensions"] = {"reason_phrase": msg.encode()}
    return httpx.Response(code, **kwargs)


def _build_response(payload: Any, status: int) -> httpx.Response:
    if payload is None:
        return httpx.Response(status)
    if isinstance(payload, (bytes, bytearray)):
        return httpx.Response(status, content=bytes(payload))
    if isinstance(payload, str):
        return httpx.Response(status, content=payload.encode())
    return httpx.Response(status, json=payload)


class MockTransport:
    """Queue-based httpx transport stand-in.

    Pass ``self.httpx_transport`` to ``Encrata(transport=...)``.
    """

    def __init__(self) -> None:
        self.requests: list[httpx.Request] = []
        self._outcomes: list[tuple[str, Any, int]] = []
        self.httpx_transport = httpx.MockTransport(self._handle)

    # -- queue programmed outcomes --------------------------------------
    def respond(self, payload: Any = None, status: int = 200) -> "MockTransport":
        self._outcomes.append(("resp", payload, status))
        return self

    def error(self, item: Any) -> "MockTransport":
        """Queue an error. ``item`` may be an ``httpx.Response`` (an HTTP error
        status to return) or an ``Exception`` (a transport error to raise)."""
        self._outcomes.append(("err", item, 0))
        return self

    # -- the httpx handler ----------------------------------------------
    def _handle(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        if not self._outcomes:
            raise AssertionError(f"No mock outcome queued for {request.url}")
        kind, item, status = self._outcomes.pop(0)
        if kind == "err":
            if isinstance(item, httpx.Response):
                return item
            raise item
        return _build_response(item, status)

    # -- request inspection ---------------------------------------------
    @property
    def call_count(self) -> int:
        return len(self.requests)

    def body(self, i: int = -1) -> Any:
        content = self.requests[i].content
        return json.loads(content) if content else None

    def url(self, i: int = -1) -> str:
        return str(self.requests[i].url)

    def method(self, i: int = -1) -> str:
        return self.requests[i].method

    def header(self, name: str, i: int = -1) -> str | None:
        return self.requests[i].headers.get(name)

