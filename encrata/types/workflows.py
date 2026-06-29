"""Workflow types."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class WorkflowStep:
    """A single step in a workflow definition."""
    id: str = ""
    type: str = ""
    config: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> WorkflowStep:
        return cls(
            id=data.get("id", ""),
            type=data.get("type", ""),
            config=data.get("config") or {},
        )


@dataclass
class Workflow:
    """An automation workflow with a trigger and ordered steps."""
    id: str = ""
    name: str = ""
    description: str = ""
    status: str = ""
    trigger: dict[str, Any] = field(default_factory=dict)
    steps: list[WorkflowStep] = field(default_factory=list)
    version: int = 0
    webhook_url: str | None = None
    created_at: str = ""
    updated_at: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Workflow:
        return cls(
            id=data.get("id", ""),
            name=data.get("name", ""),
            description=data.get("description", ""),
            status=data.get("status", ""),
            trigger=data.get("trigger") or {},
            steps=[WorkflowStep.from_dict(s) for s in data.get("steps", [])],
            version=data.get("version", 0),
            webhook_url=data.get("webhook_url"),
            created_at=data.get("created_at", ""),
            updated_at=data.get("updated_at", ""),
        )


@dataclass
class WorkflowRunStep:
    """Per-step result within a workflow run."""
    id: str = ""
    type: str = ""
    status: str = ""
    output: dict[str, Any] = field(default_factory=dict)
    duration_ms: int = 0
    credits_used: int = 0

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> WorkflowRunStep:
        return cls(
            id=data.get("id", ""),
            type=data.get("type", ""),
            status=data.get("status", ""),
            output=data.get("output") or {},
            duration_ms=data.get("duration_ms", 0),
            credits_used=data.get("credits_used", 0),
        )


@dataclass
class WorkflowRun:
    """A workflow execution run with step-by-step results."""
    id: str = ""
    workflow_id: str = ""
    workflow_name: str = ""
    status: str = ""
    input: dict[str, Any] = field(default_factory=dict)
    steps: list[WorkflowRunStep] = field(default_factory=list)
    steps_total: int = 0
    steps_completed: int = 0
    credits_used: int = 0
    started_at: str | None = None
    completed_at: str | None = None
    duration_ms: int = 0

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> WorkflowRun:
        return cls(
            id=data.get("id", ""),
            workflow_id=data.get("workflow_id", ""),
            workflow_name=data.get("workflow_name", ""),
            status=data.get("status", ""),
            input=data.get("input") or {},
            steps=[WorkflowRunStep.from_dict(s) for s in data.get("steps", [])],
            steps_total=data.get("steps_total", 0),
            steps_completed=data.get("steps_completed", 0),
            credits_used=data.get("credits_used", 0),
            started_at=data.get("started_at"),
            completed_at=data.get("completed_at"),
            duration_ms=data.get("duration_ms", 0),
        )


@dataclass
class WorkflowTemplate:
    """A pre-built workflow template you can clone."""
    id: str = ""
    name: str = ""
    description: str = ""
    category: str = ""
    steps: list[WorkflowStep] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> WorkflowTemplate:
        return cls(
            id=data.get("id", ""),
            name=data.get("name", ""),
            description=data.get("description", ""),
            category=data.get("category", ""),
            steps=[WorkflowStep.from_dict(s) for s in data.get("steps", [])],
        )


@dataclass
class WorkflowSecret:
    """An encrypted workflow secret (name only — values are never exposed)."""
    name: str = ""
    created_at: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> WorkflowSecret:
        return cls(
            name=data.get("name", ""),
            created_at=data.get("created_at", ""),
        )
