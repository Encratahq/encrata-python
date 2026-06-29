"""API key types."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class ApiKey:
    """An API key. ``key`` is only populated on creation."""
    id: str = ""
    name: str = ""
    key_preview: str = ""
    key: str | None = None
    total_requests: int = 0
    credits_used: int = 0
    created_at: str = ""
    last_used: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ApiKey:
        return cls(
            id=data.get("id", ""),
            name=data.get("name", ""),
            key_preview=data.get("key_preview", ""),
            key=data.get("key"),
            total_requests=data.get("total_requests", 0),
            credits_used=data.get("credits_used", 0),
            created_at=data.get("created_at", ""),
            last_used=data.get("last_used"),
        )
