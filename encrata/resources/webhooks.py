"""Webhooks: register endpoints, manage subscriptions, test, and view deliveries."""

from __future__ import annotations

from typing import Any, Sequence

from ..types import Webhook, WebhookDelivery


class WebhooksSyncMixin:
    def list_webhooks(self) -> list[Webhook]:
        """List all webhooks for the current workspace."""
        data = self._get("/api/webhooks")
        items = data if isinstance(data, list) else data.get("webhooks") or []
        return [Webhook.from_dict(w) for w in items]

    def create_webhook(
        self,
        url: str,
        events: Sequence[str],
        *,
        description: str | None = None,
    ) -> Webhook:
        """Register a webhook. The signing ``secret`` is only returned once — store it."""
        body: dict[str, Any] = {"url": url, "events": list(events)}
        if description is not None:
            body["description"] = description
        data = self._post("/api/webhooks", body)
        return Webhook.from_dict(data)

    def update_webhook(
        self,
        webhook_id: str,
        url: str,
        *,
        events: Sequence[str] | None = None,
        description: str | None = None,
        is_active: bool | None = None,
    ) -> dict[str, Any]:
        """Update a webhook's URL, events, description, or active status."""
        body: dict[str, Any] = {"id": webhook_id, "url": url}
        if events is not None:
            body["events"] = list(events)
        if description is not None:
            body["description"] = description
        if is_active is not None:
            body["is_active"] = is_active
        return self._request("PUT", "/api/webhooks", body=body)

    def delete_webhook(self, webhook_id: str) -> dict[str, Any]:
        """Permanently remove a webhook and all its delivery history."""
        return self._request("DELETE", "/api/webhooks", body={"id": webhook_id})

    def test_webhook(self, webhook_id: str) -> dict[str, Any]:
        """Send a test event to a webhook to verify connectivity."""
        return self._post("/api/webhooks/test", {"id": webhook_id})

    def list_webhook_deliveries(self, webhook_id: str) -> list[WebhookDelivery]:
        """List up to 50 most recent delivery attempts for a webhook."""
        data = self._get("/api/webhooks/deliveries", params={"webhook_id": webhook_id})
        items = data if isinstance(data, list) else data.get("deliveries") or []
        return [WebhookDelivery.from_dict(d) for d in items]


class WebhooksAsyncMixin:
    async def list_webhooks(self) -> list[Webhook]:
        """List all webhooks for the current workspace."""
        data = await self._get("/api/webhooks")
        items = data if isinstance(data, list) else data.get("webhooks") or []
        return [Webhook.from_dict(w) for w in items]

    async def create_webhook(
        self,
        url: str,
        events: Sequence[str],
        *,
        description: str | None = None,
    ) -> Webhook:
        """Register a webhook. The signing ``secret`` is only returned once — store it."""
        body: dict[str, Any] = {"url": url, "events": list(events)}
        if description is not None:
            body["description"] = description
        data = await self._post("/api/webhooks", body)
        return Webhook.from_dict(data)

    async def update_webhook(
        self,
        webhook_id: str,
        url: str,
        *,
        events: Sequence[str] | None = None,
        description: str | None = None,
        is_active: bool | None = None,
    ) -> dict[str, Any]:
        """Update a webhook's URL, events, description, or active status."""
        body: dict[str, Any] = {"id": webhook_id, "url": url}
        if events is not None:
            body["events"] = list(events)
        if description is not None:
            body["description"] = description
        if is_active is not None:
            body["is_active"] = is_active
        return await self._request("PUT", "/api/webhooks", body=body)

    async def delete_webhook(self, webhook_id: str) -> dict[str, Any]:
        """Permanently remove a webhook and all its delivery history."""
        return await self._request("DELETE", "/api/webhooks", body={"id": webhook_id})

    async def test_webhook(self, webhook_id: str) -> dict[str, Any]:
        """Send a test event to a webhook to verify connectivity."""
        return await self._post("/api/webhooks/test", {"id": webhook_id})

    async def list_webhook_deliveries(self, webhook_id: str) -> list[WebhookDelivery]:
        """List up to 50 most recent delivery attempts for a webhook."""
        data = await self._get("/api/webhooks/deliveries", params={"webhook_id": webhook_id})
        items = data if isinstance(data, list) else data.get("deliveries") or []
        return [WebhookDelivery.from_dict(d) for d in items]
