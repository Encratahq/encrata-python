"""Workflows: create/list/get/update workflows, runs, templates, and secrets."""

from __future__ import annotations

from typing import Any, Sequence

from ..types import Workflow, WorkflowRun, WorkflowSecret, WorkflowTemplate


def _workflow_body(
    name: str | None,
    description: str | None,
    status: str | None,
    trigger: dict[str, Any] | None,
    steps: Sequence[dict[str, Any]] | None,
    template_id: str | None,
) -> dict[str, Any]:
    body: dict[str, Any] = {}
    if name is not None:
        body["name"] = name
    if description is not None:
        body["description"] = description
    if status is not None:
        body["status"] = status
    if trigger is not None:
        body["trigger"] = trigger
    if steps is not None:
        body["steps"] = list(steps)
    if template_id is not None:
        body["template_id"] = template_id
    return body


class WorkflowsSyncMixin:
    def list_workflows(
        self,
        *,
        page: int = 1,
        limit: int = 20,
        status: str | None = None,
    ) -> tuple[list[Workflow], int]:
        """List all workflows.

        Args:
            page: Page number (default 1).
            limit: Items per page (default 20, max 100).
            status: Filter by ``"active"``, ``"paused"``, or ``"draft"``.

        Returns:
            A ``(workflows, total)`` tuple.
        """
        params: dict[str, Any] = {"page": page, "limit": limit}
        if status:
            params["status"] = status
        data = self._get("/api/workflows", params=params)
        workflows = [Workflow.from_dict(w) for w in data.get("workflows") or []]
        return workflows, data.get("total", len(workflows))

    def create_workflow(
        self,
        name: str,
        *,
        description: str | None = None,
        trigger: dict[str, Any] | None = None,
        steps: Sequence[dict[str, Any]] | None = None,
        template_id: str | None = None,
    ) -> Workflow:
        """Create a new automation workflow, or clone one from ``template_id``."""
        body = _workflow_body(name, description, None, trigger, steps, template_id)
        data = self._post("/api/workflows", body)
        return Workflow.from_dict(data)

    def get_workflow(self, workflow_id: str) -> Workflow:
        """Get a single workflow by ID with its full definition."""
        data = self._get(f"/api/workflows/{workflow_id}")
        return Workflow.from_dict(data)

    def update_workflow(
        self,
        workflow_id: str,
        *,
        name: str | None = None,
        description: str | None = None,
        status: str | None = None,
        trigger: dict[str, Any] | None = None,
        steps: Sequence[dict[str, Any]] | None = None,
    ) -> Workflow:
        """Update a workflow's name, trigger, steps, or status (creates a new version)."""
        body = _workflow_body(name, description, status, trigger, steps, None)
        data = self._request("PUT", f"/api/workflows/{workflow_id}", body=body)
        if not data:
            return Workflow(id=workflow_id)
        return Workflow.from_dict(data)

    def list_workflow_runs(
        self,
        *,
        page: int = 1,
        limit: int = 20,
        workflow_id: str | None = None,
    ) -> tuple[list[WorkflowRun], int]:
        """List workflow execution runs. Returns a ``(runs, total)`` tuple."""
        params: dict[str, Any] = {"page": page, "limit": limit}
        if workflow_id:
            params["workflow_id"] = workflow_id
        data = self._get("/api/workflows/runs", params=params)
        runs = [WorkflowRun.from_dict(r) for r in data.get("runs") or []]
        return runs, data.get("total", len(runs))

    def get_workflow_run(self, run_id: str) -> WorkflowRun:
        """Get detailed run information including step-by-step results."""
        data = self._get(f"/api/workflows/runs/{run_id}")
        return WorkflowRun.from_dict(data)

    def list_workflow_templates(
        self, *, category: str | None = None
    ) -> list[WorkflowTemplate]:
        """List available pre-built workflow templates you can clone."""
        params = {"category": category} if category else None
        data = self._get("/api/workflows/templates", params=params)
        return [WorkflowTemplate.from_dict(t) for t in data.get("templates") or []]

    def list_workflow_secrets(self) -> list[WorkflowSecret]:
        """List workflow secret names (values are never exposed)."""
        data = self._get("/api/workflows/secrets")
        return [WorkflowSecret.from_dict(s) for s in data.get("secrets") or []]

    def create_workflow_secret(self, name: str, value: str) -> dict[str, Any]:
        """Create an encrypted secret usable in webhook steps as ``{{secrets.NAME}}``."""
        return self._post("/api/workflows/secrets", {"name": name, "value": value})

    def delete_workflow_secret(self, name: str) -> dict[str, Any]:
        """Delete a workflow secret by name."""
        return self._request("DELETE", "/api/workflows/secrets", body={"name": name})


class WorkflowsAsyncMixin:
    async def list_workflows(
        self,
        *,
        page: int = 1,
        limit: int = 20,
        status: str | None = None,
    ) -> tuple[list[Workflow], int]:
        """List all workflows.

        Args:
            page: Page number (default 1).
            limit: Items per page (default 20, max 100).
            status: Filter by ``"active"``, ``"paused"``, or ``"draft"``.

        Returns:
            A ``(workflows, total)`` tuple.
        """
        params: dict[str, Any] = {"page": page, "limit": limit}
        if status:
            params["status"] = status
        data = await self._get("/api/workflows", params=params)
        workflows = [Workflow.from_dict(w) for w in data.get("workflows") or []]
        return workflows, data.get("total", len(workflows))

    async def create_workflow(
        self,
        name: str,
        *,
        description: str | None = None,
        trigger: dict[str, Any] | None = None,
        steps: Sequence[dict[str, Any]] | None = None,
        template_id: str | None = None,
    ) -> Workflow:
        """Create a new automation workflow, or clone one from ``template_id``."""
        body = _workflow_body(name, description, None, trigger, steps, template_id)
        data = await self._post("/api/workflows", body)
        return Workflow.from_dict(data)

    async def get_workflow(self, workflow_id: str) -> Workflow:
        """Get a single workflow by ID with its full definition."""
        data = await self._get(f"/api/workflows/{workflow_id}")
        return Workflow.from_dict(data)

    async def update_workflow(
        self,
        workflow_id: str,
        *,
        name: str | None = None,
        description: str | None = None,
        status: str | None = None,
        trigger: dict[str, Any] | None = None,
        steps: Sequence[dict[str, Any]] | None = None,
    ) -> Workflow:
        """Update a workflow's name, trigger, steps, or status (creates a new version)."""
        body = _workflow_body(name, description, status, trigger, steps, None)
        data = await self._request("PUT", f"/api/workflows/{workflow_id}", body=body)
        if not data:
            return Workflow(id=workflow_id)
        return Workflow.from_dict(data)

    async def list_workflow_runs(
        self,
        *,
        page: int = 1,
        limit: int = 20,
        workflow_id: str | None = None,
    ) -> tuple[list[WorkflowRun], int]:
        """List workflow execution runs. Returns a ``(runs, total)`` tuple."""
        params: dict[str, Any] = {"page": page, "limit": limit}
        if workflow_id:
            params["workflow_id"] = workflow_id
        data = await self._get("/api/workflows/runs", params=params)
        runs = [WorkflowRun.from_dict(r) for r in data.get("runs") or []]
        return runs, data.get("total", len(runs))

    async def get_workflow_run(self, run_id: str) -> WorkflowRun:
        """Get detailed run information including step-by-step results."""
        data = await self._get(f"/api/workflows/runs/{run_id}")
        return WorkflowRun.from_dict(data)

    async def list_workflow_templates(
        self, *, category: str | None = None
    ) -> list[WorkflowTemplate]:
        """List available pre-built workflow templates you can clone."""
        params = {"category": category} if category else None
        data = await self._get("/api/workflows/templates", params=params)
        return [WorkflowTemplate.from_dict(t) for t in data.get("templates") or []]

    async def list_workflow_secrets(self) -> list[WorkflowSecret]:
        """List workflow secret names (values are never exposed)."""
        data = await self._get("/api/workflows/secrets")
        return [WorkflowSecret.from_dict(s) for s in data.get("secrets") or []]

    async def create_workflow_secret(self, name: str, value: str) -> dict[str, Any]:
        """Create an encrypted secret usable in webhook steps as ``{{secrets.NAME}}``."""
        return await self._post("/api/workflows/secrets", {"name": name, "value": value})

    async def delete_workflow_secret(self, name: str) -> dict[str, Any]:
        """Delete a workflow secret by name."""
        return await self._request("DELETE", "/api/workflows/secrets", body={"name": name})
