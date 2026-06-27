"""Tests for the monitor endpoints."""

from __future__ import annotations

import pytest

import mock_data as data


def test_list_monitors(client, transport):
    transport.respond(data.MONITORS_RESPONSE)

    monitors = client.list_monitors()

    assert transport.method() == "GET"
    assert transport.url().endswith("/api/agent/monitors")
    assert len(monitors) == 1
    assert monitors[0].id == "mon_123"
    assert monitors[0].name == "Sales VIPs"
    assert monitors[0].tracked_fields == ["name", "company", "role"]


def test_list_monitors_empty(client, transport):
    transport.respond({})

    assert client.list_monitors() == []


def test_create_monitor_minimal_body(client, transport):
    transport.respond(data.MONITOR)

    client.create_monitor("Sales VIPs")

    assert transport.method() == "POST"
    assert transport.body() == {
        "name": "Sales VIPs",
        "frequency": "monthly",
        "change_detection": "diff_only",
    }


def test_create_monitor_with_list_source(client, transport):
    transport.respond(data.MONITOR)

    client.create_monitor("Sales VIPs", list_id="list_456", frequency="weekly")

    body = transport.body()
    assert body["frequency"] == "weekly"
    assert body["data_source_type"] == "list"
    assert body["data_source_ref"] == "list_456"


def test_create_monitor_with_emails(client, transport):
    transport.respond(data.MONITOR)

    client.create_monitor("Sales VIPs", emails=["a@x.com", "b@x.com"])

    assert transport.body()["emails"] == ["a@x.com", "b@x.com"]


def test_get_monitor(client, transport):
    transport.respond(data.MONITOR)

    monitor = client.get_monitor("mon_123")

    assert transport.url().endswith("/api/agent/monitors/mon_123")
    assert monitor.id == "mon_123"


def test_trigger_run_returns_dict(client, transport):
    transport.respond(data.TRIGGER_RUN_RESPONSE)

    result = client.trigger_run("mon_123")

    assert transport.method() == "POST"
    assert transport.url().endswith("/api/agent/monitors/mon_123/run")
    assert result == data.TRIGGER_RUN_RESPONSE


def test_list_runs_returns_runs_and_total(client, transport):
    transport.respond(data.RUNS_RESPONSE)

    runs, total = client.list_runs("mon_123", limit=5, offset=10)

    url = transport.url()
    assert "/api/agent/monitors/mon_123/runs" in url
    assert "limit=5" in url
    assert "offset=10" in url
    assert total == 1
    assert runs[0].id == "run_789"
    assert runs[0].changes_detected == 3


def test_iter_runs_fetches_pages_until_total(client, transport):
    first = {**data.MONITOR_RUN, "id": "run_1"}
    second = {**data.MONITOR_RUN, "id": "run_2"}
    third = {**data.MONITOR_RUN, "id": "run_3"}
    transport.respond({"runs": [first, second], "total": 3})
    transport.respond({"runs": [third], "total": 3})

    runs = list(client.iter_runs("mon_123", limit=2))

    assert [run.id for run in runs] == ["run_1", "run_2", "run_3"]
    assert "limit=2" in transport.url(0)
    assert "offset=0" in transport.url(0)
    assert "limit=2" in transport.url(1)
    assert "offset=2" in transport.url(1)


def test_get_run_results_changes_only(client, transport):
    transport.respond(data.RESULTS_RESPONSE)

    snapshots, total = client.get_run_results(
        "mon_123", "run_789", changes_only=True
    )

    url = transport.url()
    assert "/api/agent/monitors/mon_123/runs/run_789/results" in url
    assert "changes_only=true" in url
    assert total == 1
    assert snapshots[0].email == "elon@tesla.com"
    assert snapshots[0].has_changes is True


def test_get_run_results_without_changes_only(client, transport):
    transport.respond(data.RESULTS_RESPONSE)

    client.get_run_results("mon_123", "run_789")

    assert "changes_only" not in transport.url()


def test_iter_run_results_fetches_pages_until_total(client, transport):
    first = {**data.SNAPSHOT, "id": "snap_1", "email": "a@example.com"}
    second = {**data.SNAPSHOT, "id": "snap_2", "email": "b@example.com"}
    transport.respond({"results": [first], "total": 2})
    transport.respond({"results": [second], "total": 2})

    snapshots = list(
        client.iter_run_results(
            "mon_123",
            "run_789",
            changes_only=True,
            limit=1,
        )
    )

    assert [snapshot.email for snapshot in snapshots] == [
        "a@example.com",
        "b@example.com",
    ]
    assert "changes_only=true" in transport.url(0)
    assert "offset=0" in transport.url(0)
    assert "offset=1" in transport.url(1)


def test_list_all_runs(client, transport):
    transport.respond(data.RUNS_RESPONSE)

    runs, total = client.list_all_runs()

    assert transport.url().split("?")[0].endswith("/api/agent/monitoring/runs")
    assert total == 1
    assert len(runs) == 1


def test_iter_all_runs_fetches_pages_until_total(client, transport):
    first = {**data.MONITOR_RUN, "id": "run_1"}
    second = {**data.MONITOR_RUN, "id": "run_2"}
    transport.respond({"runs": [first], "total": 2})
    transport.respond({"runs": [second], "total": 2})

    runs = list(client.iter_all_runs(limit=1))

    assert [run.id for run in runs] == ["run_1", "run_2"]
    assert transport.url(0).split("?")[0].endswith("/api/agent/monitoring/runs")
    assert "offset=1" in transport.url(1)


def test_list_all_results(client, transport):
    transport.respond(data.RESULTS_RESPONSE)

    snapshots, total = client.list_all_results(changes_only=True)

    url = transport.url()
    assert "/api/agent/monitoring/results" in url
    assert "changes_only=true" in url
    assert total == 1
    assert len(snapshots) == 1


def test_iter_all_results_fetches_pages_until_total(client, transport):
    first = {**data.SNAPSHOT, "id": "snap_1", "email": "a@example.com"}
    second = {**data.SNAPSHOT, "id": "snap_2", "email": "b@example.com"}
    transport.respond({"results": [first], "total": 2})
    transport.respond({"results": [second], "total": 2})

    snapshots = list(client.iter_all_results(changes_only=True, limit=1))

    assert [snapshot.email for snapshot in snapshots] == [
        "a@example.com",
        "b@example.com",
    ]
    assert "/api/agent/monitoring/results" in transport.url(0)
    assert "changes_only=true" in transport.url(0)
    assert "offset=1" in transport.url(1)


def test_iter_paginated_methods_reject_non_positive_limit(client):
    with pytest.raises(ValueError, match="limit must be greater than 0"):
        list(client.iter_all_runs(limit=0))
