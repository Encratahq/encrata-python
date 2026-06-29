"""API keys: list, create, and revoke/delete keys for the authenticated user."""

from __future__ import annotations

from typing import Any

from ..types import ApiKey


class KeysSyncMixin:
    def list_keys(self) -> list[ApiKey]:
        """List all API keys for the authenticated user."""
        data = self._get("/api/keys")
        return [ApiKey.from_dict(k) for k in data.get("keys") or []]

    def create_key(self, name: str) -> ApiKey:
        """Create a new API key. The full ``key`` is only returned once — store it."""
        data = self._post("/api/keys", {"name": name})
        return ApiKey.from_dict(data)

    def revoke_key(self, key_id: str, *, permanent: bool = False) -> dict[str, Any]:
        """Revoke an API key (soft disable), or permanently delete it with ``permanent=True``."""
        params: dict[str, Any] = {"id": key_id}
        if permanent:
            params["permanent"] = "true"
        return self._request("DELETE", "/api/keys", params=params)


class KeysAsyncMixin:
    async def list_keys(self) -> list[ApiKey]:
        """List all API keys for the authenticated user."""
        data = await self._get("/api/keys")
        return [ApiKey.from_dict(k) for k in data.get("keys") or []]

    async def create_key(self, name: str) -> ApiKey:
        """Create a new API key. The full ``key`` is only returned once — store it."""
        data = await self._post("/api/keys", {"name": name})
        return ApiKey.from_dict(data)

    async def revoke_key(self, key_id: str, *, permanent: bool = False) -> dict[str, Any]:
        """Revoke an API key (soft disable), or permanently delete it with ``permanent=True``."""
        params: dict[str, Any] = {"id": key_id}
        if permanent:
            params["permanent"] = "true"
        return await self._request("DELETE", "/api/keys", params=params)
