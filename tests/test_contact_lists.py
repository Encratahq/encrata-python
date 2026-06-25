"""Tests for the contact-list endpoints."""

from __future__ import annotations

import mock_data as data


def test_list_contact_lists_array_response(client, transport):
    transport.respond([data.CONTACT_LIST])

    lists = client.list_contact_lists()

    assert transport.method() == "GET"
    assert transport.url().endswith("/api/agent/lists")
    assert len(lists) == 1
    assert lists[0].id == "list_456"
    assert lists[0].email_count == 3


def test_list_contact_lists_wrapped_response(client, transport):
    transport.respond({"lists": [data.CONTACT_LIST]})

    lists = client.list_contact_lists()

    assert len(lists) == 1
    assert lists[0].name == "Sales VIPs"


def test_create_contact_list(client, transport):
    transport.respond(data.CONTACT_LIST)

    client.create_contact_list("Sales VIPs", emails=["a@x.com"])

    assert transport.method() == "POST"
    assert transport.body() == {"name": "Sales VIPs", "emails": ["a@x.com"]}


def test_create_contact_list_without_emails(client, transport):
    transport.respond(data.CONTACT_LIST)

    client.create_contact_list("Sales VIPs")

    assert transport.body() == {"name": "Sales VIPs"}


def test_get_contact_list(client, transport):
    transport.respond(data.CONTACT_LIST)

    cl = client.get_contact_list("list_456")

    assert transport.url().endswith("/api/agent/lists/list_456")
    assert cl.id == "list_456"


def test_delete_contact_list(client, transport):
    transport.respond(None, status=204)

    result = client.delete_contact_list("list_456")

    assert result is None
    assert transport.method() == "DELETE"
    assert transport.url().endswith("/api/agent/lists/list_456")


def test_list_emails_array_of_strings(client, transport):
    transport.respond(["a@x.com", "b@x.com"])

    emails = client.list_contact_list_emails("list_456")

    assert emails == ["a@x.com", "b@x.com"]
    assert transport.url().endswith("/api/agent/lists/list_456/emails")


def test_list_emails_array_of_objects(client, transport):
    transport.respond([{"email": "a@x.com"}, {"email": "b@x.com"}])

    emails = client.list_contact_list_emails("list_456")

    assert emails == ["a@x.com", "b@x.com"]


def test_list_emails_wrapped_response(client, transport):
    transport.respond({"emails": ["a@x.com"]})

    emails = client.list_contact_list_emails("list_456")

    assert emails == ["a@x.com"]


def test_add_emails_returns_count(client, transport):
    transport.respond({"added": 2})

    added = client.add_contact_list_emails("list_456", ["a@x.com", "b@x.com"])

    assert added == 2
    assert transport.method() == "POST"
    assert transport.body() == {"emails": ["a@x.com", "b@x.com"]}


def test_delete_emails_returns_count_and_sends_body(client, transport):
    transport.respond({"deleted": 1})

    deleted = client.delete_contact_list_emails("list_456", ["a@x.com"])

    assert deleted == 1
    assert transport.method() == "DELETE"
    assert transport.url().endswith("/api/agent/lists/list_456/emails")
    assert transport.body() == {"emails": ["a@x.com"]}
