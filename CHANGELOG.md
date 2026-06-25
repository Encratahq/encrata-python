# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0] - 2026-06-25

### Added
- Async client `AsyncEncrata` (powered by `httpx`) with a concurrent
  `lookup_many()` helper bounded by `max_concurrency`.
- Context-manager support for both clients (`with Encrata(...) as client:` /
  `async with AsyncEncrata(...) as client:`) plus `close()` / `aclose()` to
  release the connection pool.
- Configurable `max_retries`. Transient failures (429, 500, 502, 503, 504,
  timeouts, connection errors) are retried automatically with full-jitter
  exponential backoff.
- `Retry-After` header is honored for numeric and HTTP-date values and clamped
  to a 30-second ceiling.
- Optional `transport` argument for injecting a custom `httpx` transport.

### Changed
- The HTTP layer now uses `httpx` with connection pooling and keep-alive
  instead of `urllib`. `httpx` is now a required dependency.
- The `User-Agent` version is read from package metadata instead of being
  hard-coded.

### Fixed
- Read and connect timeouts are now retried and surfaced as
  `APIConnectionError` instead of escaping as an uncaught error.

## [0.2.0]

### Added
- Initial release: synchronous `Encrata` client covering email intelligence
  (`lookup`, `validate`, `breaches`), monitors, and contact lists.
- Typed dataclasses for all responses.
- Typed exception hierarchy (`AuthenticationError`, `InsufficientCreditsError`,
  `InvalidRequestError`, `RateLimitError`, `APIConnectionError`, `APIError`).

[0.3.0]: https://github.com/Encratahq/encrata-python/releases/tag/v0.3.0
[0.2.0]: https://github.com/Encratahq/encrata-python/releases/tag/v0.2.0
