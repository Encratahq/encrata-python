"""Monitoring: create/list monitors, runs, results, with pagination."""

from __future__ import annotations

from typing import Any, AsyncIterator, Iterator, Sequence

from ..types import Monitor, MonitorRun, MonitorSnapshot


class MonitorsSyncMixin:
    def list_monitors(self) -> list[Monitor]:
        """List all monitors."""
        data = self._get("/api/agent/monitors")
        return [Monitor.from_dict(m) for m in data.get("monitors", [])]

    def create_monitor(
        self,
        name: str,
        *,
        emails: Sequence[str] | None = None,
        frequency: str = "monthly",
        change_detection: str = "diff_only",
        list_id: str | None = None,
    ) -> Monitor:
        """Create a new monitor.

        Args:
            name: Monitor name.
            emails: Email addresses to monitor.
            frequency: ``"weekly"``, ``"biweekly"``, ``"monthly"``, or ``"quarterly"``.
            change_detection: ``"diff_only"`` or ``"full_refresh"``.
            list_id: Optional contact list ID to use as the data source.
        """
        body: dict[str, Any] = {
            "name": name,
            "frequency": frequency,
            "change_detection": change_detection,
        }
        if list_id:
            body["data_source_type"] = "list"
            body["data_source_ref"] = list_id
        if emails:
            body["emails"] = list(emails)
        data = self._post("/api/agent/monitors", body)
        return Monitor.from_dict(data)

    def get_monitor(self, monitor_id: str) -> Monitor:
        """Get a monitor by ID."""
        data = self._get(f"/api/agent/monitors/{monitor_id}")
        return Monitor.from_dict(data)

    def trigger_run(self, monitor_id: str) -> dict[str, Any]:
        """Trigger an immediate monitoring run.

        Returns:
            A dict with ``run_id``, ``status``, and ``message``.
        """
        return self._post(f"/api/agent/monitors/{monitor_id}/run", {})

    def list_runs(
        self,
        monitor_id: str,
        *,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[MonitorRun], int]:
        """List runs for a specific monitor.

        Returns:
            A tuple of (runs, total_count).
        """
        data = self._get(
            f"/api/agent/monitors/{monitor_id}/runs",
            params={"limit": limit, "offset": offset},
        )
        runs = [MonitorRun.from_dict(r) for r in data.get("runs", [])]
        return runs, data.get("total", len(runs))

    def iter_runs(
        self,
        monitor_id: str,
        *,
        limit: int = 100,
        offset: int = 0,
    ) -> Iterator[MonitorRun]:
        """Yield all runs for a monitor, fetching additional pages as needed."""
        if limit <= 0:
            raise ValueError("limit must be greater than 0")

        while True:
            runs, total = self.list_runs(monitor_id, limit=limit, offset=offset)
            if not runs:
                return

            yield from runs

            offset += len(runs)
            if offset >= total:
                return

    def get_run_results(
        self,
        monitor_id: str,
        run_id: str,
        *,
        changes_only: bool = False,
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[list[MonitorSnapshot], int]:
        """Get results for a specific run.

        Returns:
            A tuple of (snapshots, total_count).
        """
        params: dict[str, Any] = {"limit": limit, "offset": offset}
        if changes_only:
            params["changes_only"] = "true"
        data = self._get(
            f"/api/agent/monitors/{monitor_id}/runs/{run_id}/results",
            params=params,
        )
        snapshots = [MonitorSnapshot.from_dict(s) for s in data.get("results", [])]
        return snapshots, data.get("total", len(snapshots))

    def iter_run_results(
        self,
        monitor_id: str,
        run_id: str,
        *,
        changes_only: bool = False,
        limit: int = 100,
        offset: int = 0,
    ) -> Iterator[MonitorSnapshot]:
        """Yield all results for a run, fetching additional pages as needed."""
        if limit <= 0:
            raise ValueError("limit must be greater than 0")

        while True:
            snapshots, total = self.get_run_results(
                monitor_id,
                run_id,
                changes_only=changes_only,
                limit=limit,
                offset=offset,
            )
            if not snapshots:
                return

            yield from snapshots

            offset += len(snapshots)
            if offset >= total:
                return

    def list_all_runs(
        self,
        *,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[MonitorRun], int]:
        """List all runs across all monitors.

        Returns:
            A tuple of (runs, total_count).
        """
        data = self._get(
            "/api/agent/monitoring/runs",
            params={"limit": limit, "offset": offset},
        )
        runs = [MonitorRun.from_dict(r) for r in data.get("runs", [])]
        return runs, data.get("total", len(runs))

    def iter_all_runs(
        self,
        *,
        limit: int = 100,
        offset: int = 0,
    ) -> Iterator[MonitorRun]:
        """Yield all runs across monitors, fetching additional pages as needed."""
        if limit <= 0:
            raise ValueError("limit must be greater than 0")

        while True:
            runs, total = self.list_all_runs(limit=limit, offset=offset)
            if not runs:
                return

            yield from runs

            offset += len(runs)
            if offset >= total:
                return

    def list_all_results(
        self,
        *,
        changes_only: bool = False,
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[list[MonitorSnapshot], int]:
        """List all enrichment results across all monitors.

        Returns:
            A tuple of (snapshots, total_count).
        """
        params: dict[str, Any] = {"limit": limit, "offset": offset}
        if changes_only:
            params["changes_only"] = "true"
        data = self._get("/api/agent/monitoring/results", params=params)
        snapshots = [MonitorSnapshot.from_dict(s) for s in data.get("results", [])]
        return snapshots, data.get("total", len(snapshots))

    def iter_all_results(
        self,
        *,
        changes_only: bool = False,
        limit: int = 100,
        offset: int = 0,
    ) -> Iterator[MonitorSnapshot]:
        """Yield all results across monitors, fetching additional pages as needed."""
        if limit <= 0:
            raise ValueError("limit must be greater than 0")

        while True:
            snapshots, total = self.list_all_results(
                changes_only=changes_only,
                limit=limit,
                offset=offset,
            )
            if not snapshots:
                return

            yield from snapshots

            offset += len(snapshots)
            if offset >= total:
                return


class MonitorsAsyncMixin:
    async def list_monitors(self) -> list[Monitor]:
        """List all monitors."""
        data = await self._get("/api/agent/monitors")
        return [Monitor.from_dict(m) for m in data.get("monitors", [])]

    async def create_monitor(
        self,
        name: str,
        *,
        emails: Sequence[str] | None = None,
        frequency: str = "monthly",
        change_detection: str = "diff_only",
        list_id: str | None = None,
    ) -> Monitor:
        """Create a new monitor."""
        body: dict[str, Any] = {
            "name": name,
            "frequency": frequency,
            "change_detection": change_detection,
        }
        if list_id:
            body["data_source_type"] = "list"
            body["data_source_ref"] = list_id
        if emails:
            body["emails"] = list(emails)
        data = await self._post("/api/agent/monitors", body)
        return Monitor.from_dict(data)

    async def get_monitor(self, monitor_id: str) -> Monitor:
        """Get a monitor by ID."""
        data = await self._get(f"/api/agent/monitors/{monitor_id}")
        return Monitor.from_dict(data)

    async def trigger_run(self, monitor_id: str) -> dict[str, Any]:
        """Trigger an immediate monitoring run."""
        return await self._post(f"/api/agent/monitors/{monitor_id}/run", {})

    async def list_runs(
        self,
        monitor_id: str,
        *,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[MonitorRun], int]:
        """List runs for a specific monitor. Returns (runs, total)."""
        data = await self._get(
            f"/api/agent/monitors/{monitor_id}/runs",
            params={"limit": limit, "offset": offset},
        )
        runs = [MonitorRun.from_dict(r) for r in data.get("runs", [])]
        return runs, data.get("total", len(runs))

    async def iter_runs(
        self,
        monitor_id: str,
        *,
        limit: int = 100,
        offset: int = 0,
    ) -> AsyncIterator[MonitorRun]:
        """Yield all runs for a monitor, fetching additional pages as needed."""
        if limit <= 0:
            raise ValueError("limit must be greater than 0")

        while True:
            runs, total = await self.list_runs(monitor_id, limit=limit, offset=offset)
            if not runs:
                return

            for run in runs:
                yield run

            offset += len(runs)
            if offset >= total:
                return

    async def get_run_results(
        self,
        monitor_id: str,
        run_id: str,
        *,
        changes_only: bool = False,
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[list[MonitorSnapshot], int]:
        """Get results for a specific run. Returns (snapshots, total)."""
        params: dict[str, Any] = {"limit": limit, "offset": offset}
        if changes_only:
            params["changes_only"] = "true"
        data = await self._get(
            f"/api/agent/monitors/{monitor_id}/runs/{run_id}/results",
            params=params,
        )
        snapshots = [MonitorSnapshot.from_dict(s) for s in data.get("results", [])]
        return snapshots, data.get("total", len(snapshots))

    async def iter_run_results(
        self,
        monitor_id: str,
        run_id: str,
        *,
        changes_only: bool = False,
        limit: int = 100,
        offset: int = 0,
    ) -> AsyncIterator[MonitorSnapshot]:
        """Yield all results for a run, fetching additional pages as needed."""
        if limit <= 0:
            raise ValueError("limit must be greater than 0")

        while True:
            snapshots, total = await self.get_run_results(
                monitor_id,
                run_id,
                changes_only=changes_only,
                limit=limit,
                offset=offset,
            )
            if not snapshots:
                return

            for snapshot in snapshots:
                yield snapshot

            offset += len(snapshots)
            if offset >= total:
                return

    async def list_all_runs(
        self,
        *,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[MonitorRun], int]:
        """List all runs across all monitors. Returns (runs, total)."""
        data = await self._get(
            "/api/agent/monitoring/runs",
            params={"limit": limit, "offset": offset},
        )
        runs = [MonitorRun.from_dict(r) for r in data.get("runs", [])]
        return runs, data.get("total", len(runs))

    async def iter_all_runs(
        self,
        *,
        limit: int = 100,
        offset: int = 0,
    ) -> AsyncIterator[MonitorRun]:
        """Yield all runs across monitors, fetching additional pages as needed."""
        if limit <= 0:
            raise ValueError("limit must be greater than 0")

        while True:
            runs, total = await self.list_all_runs(limit=limit, offset=offset)
            if not runs:
                return

            for run in runs:
                yield run

            offset += len(runs)
            if offset >= total:
                return

    async def list_all_results(
        self,
        *,
        changes_only: bool = False,
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[list[MonitorSnapshot], int]:
        """List all enrichment results across all monitors. Returns (snapshots, total)."""
        params: dict[str, Any] = {"limit": limit, "offset": offset}
        if changes_only:
            params["changes_only"] = "true"
        data = await self._get("/api/agent/monitoring/results", params=params)
        snapshots = [MonitorSnapshot.from_dict(s) for s in data.get("results", [])]
        return snapshots, data.get("total", len(snapshots))

    async def iter_all_results(
        self,
        *,
        changes_only: bool = False,
        limit: int = 100,
        offset: int = 0,
    ) -> AsyncIterator[MonitorSnapshot]:
        """Yield all results across monitors, fetching additional pages as needed."""
        if limit <= 0:
            raise ValueError("limit must be greater than 0")

        while True:
            snapshots, total = await self.list_all_results(
                changes_only=changes_only,
                limit=limit,
                offset=offset,
            )
            if not snapshots:
                return

            for snapshot in snapshots:
                yield snapshot

            offset += len(snapshots)
            if offset >= total:
                return
