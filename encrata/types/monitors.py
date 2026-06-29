"""Monitoring types."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Monitor:
    """A monitoring configuration."""
    id: str = ""
    name: str = ""
    status: str = ""
    frequency: str = ""
    change_detection: str = ""
    data_source_type: str = ""
    data_source_ref: str = ""
    email_count: int = 0
    tracked_fields: list[str] = field(default_factory=list)
    last_run_at: str | None = None
    next_run_at: str | None = None
    created_at: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Monitor:
        return cls(
            id=data.get("id", ""),
            name=data.get("name", ""),
            status=data.get("status", ""),
            frequency=data.get("frequency", ""),
            change_detection=data.get("change_detection", ""),
            data_source_type=data.get("data_source_type", ""),
            data_source_ref=data.get("data_source_ref", ""),
            email_count=data.get("email_count", 0),
            tracked_fields=data.get("tracked_fields") or [],
            last_run_at=data.get("last_run_at"),
            next_run_at=data.get("next_run_at"),
            created_at=data.get("created_at", ""),
        )


@dataclass
class MonitorRun:
    """A monitoring run."""
    id: str = ""
    monitor_id: str = ""
    monitor_name: str = ""
    status: str = ""
    total_records: int = 0
    changes_detected: int = 0
    credits_used: int = 0
    started_at: str | None = None
    completed_at: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> MonitorRun:
        return cls(
            id=data.get("id", ""),
            monitor_id=data.get("monitor_id", ""),
            monitor_name=data.get("monitor_name", ""),
            status=data.get("status", ""),
            total_records=data.get("total_records", 0),
            changes_detected=data.get("changes_detected", 0),
            credits_used=data.get("credits_used", 0),
            started_at=data.get("started_at"),
            completed_at=data.get("completed_at"),
        )


@dataclass
class MonitorSnapshot:
    """An enrichment result snapshot from a monitoring run."""
    id: str = ""
    email: str = ""
    has_changes: bool = False
    changes: Any = None
    data: Any = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> MonitorSnapshot:
        return cls(
            id=data.get("id", ""),
            email=data.get("email", ""),
            has_changes=data.get("has_changes", False),
            changes=data.get("changes"),
            data=data.get("data"),
        )


@dataclass
class ContactList:
    """A contact list."""
    id: str = ""
    name: str = ""
    list_type: str = ""
    email_count: int = 0
    created_at: str = ""
    updated_at: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ContactList:
        return cls(
            id=data.get("id", ""),
            name=data.get("name", ""),
            list_type=data.get("list_type", ""),
            email_count=data.get("email_count", 0),
            created_at=data.get("created_at", ""),
            updated_at=data.get("updated_at", ""),
        )
