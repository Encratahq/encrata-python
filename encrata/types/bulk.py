"""Bulk search types."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class BulkSearchResponse:
    """Result set for a bulk search (google/company/domain/ip).

    Each item in ``results`` is the raw per-query record (keyed by ``query``
    plus a domain-specific payload) — left as a dict because shapes are deep
    and source-dependent.
    """
    results: list[dict[str, Any]] = field(default_factory=list)
    credits_used: int = 0

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> BulkSearchResponse:
        return cls(
            results=data.get("results", []),
            credits_used=data.get("credits_used", 0),
        )
