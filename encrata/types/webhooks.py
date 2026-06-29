"""Webhook types."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Webhook:
    """A webhook endpoint. ``secret`` is only populated on creation."""
    id: str = ""
    workspace_id: str = ""
    url: str = ""
    events: list[str] = field(default_factory=list)
    is_active: bool = True
    description: str = ""
    secret: str | None = None
    created_by: str = ""
    created_at: str = ""
    updated_at: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Webhook:
        return cls(
            id=data.get("id", ""),
            workspace_id=data.get("workspace_id", ""),
            url=data.get("url", ""),
            events=data.get("events") or [],
            is_active=data.get("is_active", True),
            description=data.get("description", ""),
            secret=data.get("secret"),
            created_by=data.get("created_by", ""),
            created_at=data.get("created_at", ""),
            updated_at=data.get("updated_at", ""),
        )


@dataclass
class WebhookDelivery:
    """A single webhook delivery attempt."""
    id: str = ""
    webhook_id: str = ""
    event_type: str = ""
    payload: dict[str, Any] = field(default_factory=dict)
    status: str = ""
    attempts: int = 0
    response_status: int = 0
    response_body: str = ""
    last_attempt_at: str | None = None
    created_at: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> WebhookDelivery:
        return cls(
            id=data.get("id", ""),
            webhook_id=data.get("webhook_id", ""),
            event_type=data.get("event_type", ""),
            payload=data.get("payload") or {},
            status=data.get("status", ""),
            attempts=data.get("attempts", 0),
            response_status=data.get("response_status", 0),
            response_body=data.get("response_body", ""),
            last_attempt_at=data.get("last_attempt_at"),
            created_at=data.get("created_at", ""),
        )
