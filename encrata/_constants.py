"""Shared constants used by both the sync and async clients."""

from __future__ import annotations

from email.utils import parsedate_to_datetime
from datetime import datetime, timezone

try:
    from importlib.metadata import PackageNotFoundError, version as _pkg_version
except ImportError:  # pragma: no cover - Python < 3.8
    PackageNotFoundError = Exception  # type: ignore[assignment,misc]

    def _pkg_version(_name: str) -> str:  # type: ignore[misc]
        raise PackageNotFoundError


try:
    __version__ = _pkg_version("encrata")
except PackageNotFoundError:  # pragma: no cover - running from a source checkout
    __version__ = "0.3.0"

DEFAULT_BASE_URL = "https://api.encrata.com"
USER_AGENT = f"encrata-python/{__version__}"


# Retry configuration
MAX_RETRIES = 3  # Maximum number of retries for failed requests
INITIAL_BACKOFF = 1.0  # Initial backoff time in seconds
BACKOFF_FACTOR = 2.0  # Backoff factor for exponential backoff
MAX_BACKOFF = 30.0  # Hard ceiling for any single backoff sleep (seconds)
RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}  # Retryable HTTP status codes


def parse_retry_after(value: str | None) -> float | None:
    """Parse a ``Retry-After`` header into seconds.

    Accepts both forms allowed by the HTTP spec:
      * a number of seconds (``"5"`` or ``"1.5"``)
      * an HTTP-date (``"Wed, 21 Oct 2026 07:28:00 GMT"``)

    Returns the delay in seconds (never negative), or ``None`` if the value is
    missing or unparseable. The caller is responsible for clamping to
    ``MAX_BACKOFF``.
    """
    if not value:
        return None

    value = value.strip()

    # Numeric form.
    try:
        return max(0.0, float(value))
    except ValueError:
        pass

    # HTTP-date form.
    try:
        when = parsedate_to_datetime(value)
    except (TypeError, ValueError):
        return None
    if when is None:
        return None
    if when.tzinfo is None:
        when = when.replace(tzinfo=timezone.utc)
    delta = (when - datetime.now(timezone.utc)).total_seconds()
    return max(0.0, delta)

