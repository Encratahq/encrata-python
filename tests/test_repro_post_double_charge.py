"""Reproduction: does the SDK re-send a credit-charging POST on a 5xx/timeout?

If `lookup` (a POST that charges credits) is retried after the server already
processed the first attempt, the user is billed twice for one logical call.
These tests PROVE the current behavior; they are expected to show the POST
being sent more than once.
"""

from __future__ import annotations

import httpx
import pytest

from encrata import Encrata
from helpers import MockTransport, make_http_error

PERSON = {"name": "Elon", "email": "elon@tesla.com", "company": "Tesla"}


def _client(transport: MockTransport) -> Encrata:
    return Encrata("enc_test_key", max_retries=2, transport=transport.httpx_transport)


def test_lookup_resends_post_after_502(transport: MockTransport) -> None:
    """Server returns 502 on attempt 1, 200 on attempt 2."""
    transport.error(make_http_error(502)).respond(PERSON)

    person = _client(transport).lookup("elon@tesla.com")

    # The lookup "succeeded" from the caller's view...
    assert person.name == "Elon"

    # ...but the POST was sent TWICE. On a real server that already charged a
    # credit on attempt 1, this means the user paid twice.
    assert transport.call_count == 2
    assert transport.method(0) == "POST"
    assert transport.method(1) == "POST"
    assert "/api/agent/lookup" in transport.url(0)
    assert "/api/agent/lookup" in transport.url(1)


def test_lookup_resends_post_after_timeout(transport: MockTransport) -> None:
    """A connection timeout on attempt 1 also triggers a resend."""
    transport.error(httpx.ConnectTimeout("boom")).respond(PERSON)

    person = _client(transport).lookup("elon@tesla.com")

    assert person.name == "Elon"
    assert transport.call_count == 2  # POST re-sent after timeout


def test_no_idempotency_key_sent(transport: MockTransport) -> None:
    """There is currently no Idempotency-Key header to let the server dedupe."""
    transport.respond(PERSON)

    _client(transport).lookup("elon@tesla.com")

    assert transport.header("Idempotency-Key") is None
    assert transport.header("idempotency-key") is None
