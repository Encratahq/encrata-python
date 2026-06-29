# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.5.0] - 2026-06-29

### Added
- OSINT endpoints on both clients: `ip()`, `phone_lookup()`, `domain_search()`,
  `company_search()`, `google_search()` (Google dork), and `darkweb_search()`
  with pagination.
- Web tooling: `scrape()`, `extract()` (selector and markdown modes), and
  screenshot capture, with auto-refund handling for failed scrapes.
- `face_search()` for reverse-image / face matching.
- Bulk operations including `bulk_lookup()` and `bulk_google_search()`.
- Contact list management (`list_contact_lists()`, `create_contact_list()`,
  `get_contact_list()`, and related helpers).
- Workflows: list, run, and inspect workflows, runs, templates, and secrets.
- API key management (`list_keys()` and related helpers).
- Webhook management (`list_webhooks()`, `create_webhook()`, and delivery
  inspection).
- New typed response dataclasses for all of the above.

### Changed
- The client is now composed from per-domain resource mixins and the response
  types are split into a `types` package, replacing the single monolithic
  client/types modules.

## [0.4.0] - 2026-06-27

### Added
- Synchronous `lookup_many()` helper that resolves many emails concurrently
  through a thread pool, with `return_exceptions` to collect failures inline
  and a configurable `max_workers`.
- Automatic pagination helpers that transparently fetch every page:
  `iter_runs()`, `iter_run_results()`, `iter_all_runs()`, and
  `iter_all_results()`, available on both the sync and async clients.
- `__version__` is now exported from the top-level `encrata` package.

### Changed
- The package version is single-sourced from `encrata/_version.py` and read at
  build time via Hatchling dynamic versioning, so package metadata and the
  runtime `User-Agent` can no longer drift.
- `lookup()` now builds query parameters through the request layer instead of
  manual query-string concatenation.

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

[0.5.0]: https://github.com/Encratahq/encrata-python/releases/tag/v0.5.0
[0.4.0]: https://github.com/Encratahq/encrata-python/releases/tag/v0.4.0
[0.3.0]: https://github.com/Encratahq/encrata-python/releases/tag/v0.3.0
[0.2.0]: https://github.com/Encratahq/encrata-python/releases/tag/v0.2.0
