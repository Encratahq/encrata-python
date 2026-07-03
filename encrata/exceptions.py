from __future__ import annotations

class EncrataError(Exception):
    """Base exception for the Encrata SDK."""

    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class AuthenticationError(EncrataError):
    """Raised when the API key is invalid or missing."""
    pass


class InsufficientCreditsError(EncrataError):
    """Raised when the account has no credits remaining."""
    pass


class InvalidRequestError(EncrataError):
    """Raised when the request is malformed."""
    pass


class RateLimitError(EncrataError):
    """Raised when the API rate limit is exceeded."""
    pass


class APIConnectionError(EncrataError):
    """Raised when the SDK cannot connect to the Encrata API."""
    pass


class APIError(EncrataError):
    """Raised when the API returns an unexpected error."""
    pass
