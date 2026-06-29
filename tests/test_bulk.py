"""Tests for bulk lookup SSE streaming."""

from __future__ import annotations

import pytest

from encrata import Person


SSE_STREAM = (
    b'data: {"email":"alice@x.com","name":"Alice","company":"Acme"}\n\n'
    b'data: {"email":"bob@y.com","name":"Bob","company":"Startup"}\n\n'
    b"data: [DONE]\n"
)

BULK_SEARCH_STREAM = (
    b'event: start\n'
    b'data: {"total":2}\n\n'
    b'event: result\n'
    b'data: {"query":"8.8.8.8","ip":"8.8.8.8","company":{"name":"Google Public DNS"}}\n\n'
    b'event: result\n'
    b'data: {"query":"1.1.1.1","ip":"1.1.1.1","company":{"name":"Cloudflare"}}\n\n'
    b'event: end\n'
    b'data: {"credits_used":2}\n\n'
)


def test_bulk_lookup_streams_people(client, transport):
    transport.respond(SSE_STREAM)
    people = list(client.bulk_lookup(["alice@x.com", "bob@y.com"]))

    assert [p.name for p in people] == ["Alice", "Bob"]
    assert all(isinstance(p, Person) for p in people)


def test_bulk_lookup_posts_emails(client, transport):
    transport.respond(SSE_STREAM)
    list(client.bulk_lookup(["alice@x.com", "bob@y.com"]))

    assert transport.body() == {"emails": ["alice@x.com", "bob@y.com"]}
    assert transport.url().endswith("/api/agent/bulk-lookup")


def test_bulk_lookup_passes_fields(client, transport):
    transport.respond(b"data: [DONE]\n")
    list(client.bulk_lookup(["a@x.com"], fields=["name", "company"]))

    assert "fields=name%2Ccompany" in transport.url()


def test_bulk_lookup_empty_stream(client, transport):
    transport.respond(b"data: [DONE]\n")
    assert list(client.bulk_lookup(["a@x.com"])) == []


def test_bulk_ip_search_collects_sse_results(client, transport):
    transport.respond(BULK_SEARCH_STREAM)

    res = client.bulk_ip_search(["8.8.8.8", "1.1.1.1"])

    assert res.credits_used == 2
    assert [r["query"] for r in res.results] == ["8.8.8.8", "1.1.1.1"]
    assert res.results[0]["company"]["name"] == "Google Public DNS"
    assert transport.body() == {"queries": ["8.8.8.8", "1.1.1.1"]}
    assert transport.url().endswith("/api/bulk-ip-search")


def test_bulk_search_collects_wrapped_json_sse_response(client, transport):
    transport.respond(
        b'data: {"results":[{"query":"example.com","domain":"example.com"}],"credits_used":1}\n\n'
    )

    res = client.bulk_domain_search(["example.com"])

    assert res.credits_used == 1
    assert res.results == [{"query": "example.com", "domain": "example.com"}]
