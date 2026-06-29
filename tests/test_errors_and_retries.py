"""Tests for error mapping, retries, and backoff."""

from __future__ import annotations

import httpx
import pytest

import mock_data as data
from helpers import make_http_error

from encrata import (
    Encrata,
    APIConnectionError,
    APIError,
    AuthenticationError,
    InsufficientCreditsError,
    InvalidRequestError,
    RateLimitError,
)


# ── construction ──────────────────────────────────────────────────────

def test_missing_api_key_raises():
    with pytest.raises(AuthenticationError):
        Encrata("")


# ── status-code -> exception mapping ──────────────────────────────────

def test_401_maps_to_authentication_error(client, transport):
    transport.error(make_http_error(401, {"message": "Invalid key"}))

    with pytest.raises(AuthenticationError) as exc:
        client.validate("x@y.com")

    assert exc.value.status_code == 401
    assert "Invalid key" in str(exc.value)


def test_402_maps_to_insufficient_credits(client, transport):
    transport.error(make_http_error(402, {"message": "No credits"}))

    with pytest.raises(InsufficientCreditsError) as exc:
        client.lookup("x@y.com")

    assert exc.value.status_code == 402


def test_400_maps_to_invalid_request(client, transport):
    transport.error(make_http_error(400, {"error": "Bad email"}))

    with pytest.raises(InvalidRequestError) as exc:
        client.lookup("not-an-email")

    assert "Bad email" in str(exc.value)


def test_429_maps_to_rate_limit_when_not_retrying(transport):
    client = Encrata("enc_test_key", max_retries=0, transport=transport.httpx_transport)
    transport.error(make_http_error(429, {"m": "Slow down"}))

    with pytest.raises(RateLimitError):
        client.validate("x@y.com")


def test_unknown_status_maps_to_api_error(transport):
    client = Encrata("enc_test_key", max_retries=0, transport=transport.httpx_transport)
    transport.error(make_http_error(500, msg="Server Error"))

    with pytest.raises(APIError) as exc:
        client.validate("x@y.com")

    # Empty body -> falls back to the HTTP reason.
    assert "Server Error" in str(exc.value)


# ── retries / backoff ─────────────────────────────────────────────────

def test_retries_then_succeeds(client, transport, sleeps):
    transport.error(make_http_error(503)).respond(data.VALIDATION)

    result = client.validate("x@y.com")

    assert result.validity == "valid"
    assert transport.call_count == 2
    assert len(sleeps) == 1


def test_retries_exhausted_raises(client, transport):
    # max_retries=2 -> 3 total attempts.
    transport.error(make_http_error(500))
    transport.error(make_http_error(500))
    transport.error(make_http_error(500))

    with pytest.raises(APIError):
        client.validate("x@y.com")

    assert transport.call_count == 3


def test_connection_error_retries_then_raises(client, transport):
    transport.error(httpx.ConnectError("boom"))
    transport.error(httpx.ConnectError("boom"))
    transport.error(httpx.ConnectError("boom"))

    with pytest.raises(APIConnectionError):
        client.validate("x@y.com")

    assert transport.call_count == 3


def test_timeout_retries_then_succeeds(client, transport, sleeps):
    # A timeout is NOT a generic connection error; it must still be retried.
    transport.error(httpx.ReadTimeout("timed out")).respond(data.VALIDATION)

    result = client.validate("x@y.com")

    assert result.validity == "valid"
    assert transport.call_count == 2
    assert len(sleeps) == 1


def test_timeout_exhausted_raises_connection_error(client, transport):
    transport.error(httpx.ReadTimeout("timed out"))
    transport.error(httpx.ReadTimeout("timed out"))
    transport.error(httpx.ReadTimeout("timed out"))

    with pytest.raises(APIConnectionError):
        client.validate("x@y.com")

    assert transport.call_count == 3


def test_retry_after_header_is_respected(client, transport, sleeps):
    transport.error(make_http_error(429, headers={"Retry-After": "2"}))
    transport.respond(data.VALIDATION)

    client.validate("x@y.com")

    assert 2.0 in sleeps


def test_retry_after_accepts_fractional_seconds(client, transport, sleeps):
    transport.error(make_http_error(429, headers={"Retry-After": "1.5"}))
    transport.respond(data.VALIDATION)

    client.validate("x@y.com")

    assert 1.5 in sleeps


def test_retry_after_is_capped_at_max_backoff(client, transport, sleeps):
    # A hostile/buggy server must never be able to block us for hours.
    transport.error(make_http_error(429, headers={"Retry-After": "99999"}))
    transport.respond(data.VALIDATION)

    client.validate("x@y.com")

    assert sleeps == [30.0]  # MAX_BACKOFF


def test_full_jitter_stays_within_ceiling(client, transport, sleeps):
    # max_retries=2 -> two backoff sleeps before success.
    transport.error(make_http_error(503))
    transport.error(make_http_error(503))
    transport.respond(data.VALIDATION)

    client.validate("x@y.com")

    assert len(sleeps) == 2
    # attempt 0 ceiling = 1s, attempt 1 ceiling = 2s; full jitter -> [0, ceiling].
    assert 0.0 <= sleeps[0] <= 1.0
    assert 0.0 <= sleeps[1] <= 2.0


def test_success_with_non_json_body_raises_api_error(client, transport):
    transport.respond("temporary upstream response")

    with pytest.raises(APIError) as exc:
        client.validate("x@y.com")

    assert exc.value.status_code == 200
    assert "Invalid JSON response" in str(exc.value)
    assert "temporary upstream response" in str(exc.value)
