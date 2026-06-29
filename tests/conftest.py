"""Shared pytest fixtures for the Encrata SDK test suite."""

from __future__ import annotations

import pytest

from encrata import Encrata
from helpers import MockTransport


@pytest.fixture
def transport() -> MockTransport:
    """An httpx-backed mock transport to inject into the client."""
    return MockTransport()


@pytest.fixture(autouse=True)
def sleeps(monkeypatch) -> list[float]:
    """Capture (and neutralise) all backoff sleeps so tests never wait."""
    recorded: list[float] = []
    monkeypatch.setattr("encrata._http.time.sleep", recorded.append)
    return recorded


@pytest.fixture
def client(transport) -> Encrata:
    """A client with a fake key. Retries enabled (2) for retry tests."""
    return Encrata("enc_test_key", max_retries=2, transport=transport.httpx_transport)
