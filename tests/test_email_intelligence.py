"""Tests for the email-intelligence endpoints (lookup, validate, breaches).

These verify the SHORT-key wire encoding/decoding that the hand-written
client relies on.
"""

from __future__ import annotations

from urllib.parse import parse_qs, urlsplit

import mock_data as data


def _query(url: str) -> dict[str, list[str]]:
    """Parse a URL's query string into decoded {name: [values]} pairs."""
    return parse_qs(urlsplit(url).query)


# ── lookup ────────────────────────────────────────────────────────────

def test_lookup_decodes_response(client, transport):
    transport.respond(data.PERSON)

    person = client.lookup("elon@tesla.com")

    assert person.name == "Elon Musk"
    assert person.company == "Tesla"
    assert person.role == "CEO"
    assert person.location == "Austin, Texas"
    assert person.photo_url == "https://cdn.encrata.com/p/elon.jpg"
    assert person.validity == "valid"


def test_lookup_decodes_nested_objects(client, transport):
    transport.respond(data.PERSON)

    person = client.lookup("elon@tesla.com")

    assert person.socials is not None
    assert person.socials.linkedin == "https://linkedin.com/in/elonmusk"
    assert person.socials.github == "https://github.com/elonmusk"
    assert person.socials.instagram is None

    assert person.breaches is not None
    assert person.breaches.count == 2
    assert person.breaches.services == ["Adobe", "LinkedIn"]
    assert person.breaches.exposed_data == ["email", "password"]

    assert person.registered_services is not None
    assert person.registered_services.count == 3

    assert len(person.news) == 1
    assert person.news[0].source == "Reuters"
    assert len(person.publications) == 1
    assert person.publications[0].year == 2020
    assert person.publications[0].citations == 42


def test_lookup_sends_full_email_body(client, transport):
    transport.respond(data.PERSON)

    client.lookup("elon@tesla.com")

    assert transport.method() == "POST"
    assert transport.url().endswith("/api/agent/lookup")
    assert transport.body() == {"email": "elon@tesla.com"}


def test_lookup_fields_passed_as_names(client, transport):
    transport.respond(data.PERSON)

    client.lookup("elon@tesla.com", fields=["name", "company", "socials"])

    assert _query(transport.url())["fields"] == ["name,company,socials"]


def test_lookup_unknown_field_passes_through(client, transport):
    transport.respond(data.PERSON)

    client.lookup("elon@tesla.com", fields=["name", "unknown_field"])

    assert _query(transport.url())["fields"] == ["name,unknown_field"]


def test_lookup_nocache_only(client, transport):
    transport.respond(data.PERSON)

    client.lookup("elon@tesla.com", nocache=True)

    assert "nocache=1" in transport.url()
    assert "fields=" not in transport.url()


def test_lookup_fields_and_nocache(client, transport):
    transport.respond(data.PERSON)

    client.lookup("elon@tesla.com", fields=["name"], nocache=True)

    url = transport.url()
    assert "fields=name" in url
    assert "nocache=1" in url


# ── lookup_many ───────────────────────────────────────────────────────

def test_lookup_many_returns_all_in_order(client, transport):
    transport.respond(data.PERSON).respond(data.PERSON).respond(data.PERSON)

    results = client.lookup_many(
        ["a@x.com", "b@x.com", "c@x.com"], max_workers=1
    )

    assert len(results) == 3
    assert all(p.name == "Elon Musk" for p in results)


def test_lookup_many_empty_returns_empty(client, transport):
    assert client.lookup_many([]) == []


def test_lookup_many_inline_exceptions(client, transport):
    from encrata import InvalidRequestError
    from helpers import make_http_error

    # Sequential (max_workers=1) so the queued error maps to the 2nd email.
    transport.respond(data.PERSON).error(make_http_error(400)).respond(data.PERSON)

    results = client.lookup_many(
        ["a@x.com", "bad@x.com", "c@x.com"],
        return_exceptions=True,
        max_workers=1,
    )

    assert results[0].name == "Elon Musk"
    assert isinstance(results[1], InvalidRequestError)
    assert results[2].name == "Elon Musk"


def test_lookup_many_raises_without_return_exceptions(client, transport):
    import pytest

    from encrata import InvalidRequestError
    from helpers import make_http_error

    transport.respond(data.PERSON).error(make_http_error(400))

    with pytest.raises(InvalidRequestError):
        client.lookup_many(["a@x.com", "bad@x.com"], max_workers=1)


# ── validate ──────────────────────────────────────────────────────────

def test_validate_decodes_response(client, transport):
    transport.respond(data.VALIDATION)

    result = client.validate("elon@tesla.com")

    assert result.email == "elon@tesla.com"
    assert result.validity == "valid"
    assert result.message == "Deliverable mailbox."


def test_validate_sends_full_email_body(client, transport):
    transport.respond(data.VALIDATION)

    client.validate("elon@tesla.com")

    assert transport.method() == "POST"
    assert transport.url().endswith("/api/agent/validate")
    assert transport.body() == {"email": "elon@tesla.com"}


# ── breaches ──────────────────────────────────────────────────────────

def test_breaches_decodes_response(client, transport):
    transport.respond(data.BREACH_REPORT)

    report = client.breaches("elon@tesla.com")

    assert report.email == "elon@tesla.com"
    assert report.count == 2
    assert report.services == ["Adobe", "LinkedIn"]
    assert report.exposed_data == ["email", "password"]
    assert report.message == "Found in 2 breaches."


def test_breaches_hits_correct_endpoint(client, transport):
    transport.respond(data.BREACH_REPORT)

    client.breaches("elon@tesla.com")

    assert transport.url().endswith("/api/agent/breaches")


# ── auth headers ──────────────────────────────────────────────────────

def test_request_sets_auth_and_content_type(client, transport):
    transport.respond(data.VALIDATION)

    client.validate("elon@tesla.com")

    assert transport.header("Authorization") == "Bearer enc_test_key"
    assert transport.header("Content-Type") == "application/json"
    assert transport.header("User-Agent").startswith("encrata-python/")
