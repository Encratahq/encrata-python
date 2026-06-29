"""Contact lists: reusable email lists for monitors."""

from __future__ import annotations

from typing import Any, Sequence

from ..types import ContactList


class ContactsSyncMixin:
    def list_contact_lists(self, *, type: str | None = None) -> list[ContactList]:
        """List all contact lists, optionally filtered by ``type``.

        Args:
            type: ``"email"``, ``"phone"``, ``"domain"``, ``"ip"``, ``"company"``, or ``"darkweb"``.
        """
        params = {"type": type} if type else None
        data = self._get("/api/agent/lists", params=params)
        if isinstance(data, list):
            return [ContactList.from_dict(cl) for cl in data]
        return [ContactList.from_dict(cl) for cl in data.get("lists", data)]

    def create_contact_list(
        self,
        name: str,
        *,
        type: str | None = None,
        targets: Sequence[str] | None = None,
        emails: Sequence[str] | None = None,
    ) -> ContactList:
        """Create a new contact list.

        Args:
            name: List name.
            type: Target type (default ``"email"``): ``email``, ``phone``, ``domain``, ``ip``, ``company``, ``darkweb``.
            targets: Initial targets to add.
            emails: Initial targets (legacy alias for ``targets``, works for all types).
        """
        body: dict[str, Any] = {"name": name}
        if type:
            body["type"] = type
        if targets:
            body["targets"] = list(targets)
        if emails:
            body["emails"] = list(emails)
        data = self._post("/api/agent/lists", body)
        return ContactList.from_dict(data)

    def get_contact_list(self, list_id: str) -> ContactList:
        """Get a contact list by ID."""
        data = self._get(f"/api/agent/lists/{list_id}")
        return ContactList.from_dict(data)

    def delete_contact_list(self, list_id: str) -> None:
        """Delete a contact list."""
        self._delete(f"/api/agent/lists/{list_id}")

    def list_contact_list_emails(self, list_id: str) -> list[str]:
        """List all emails in a contact list."""
        data = self._get(f"/api/agent/lists/{list_id}/emails")
        if isinstance(data, list):
            return [e.get("email", e) if isinstance(e, dict) else e for e in data]
        return data.get("emails", [])

    def add_contact_list_emails(self, list_id: str, emails: Sequence[str]) -> int:
        """Add emails to a contact list. Returns count of emails added."""
        data = self._post(f"/api/agent/lists/{list_id}/emails", {"emails": list(emails)})
        return data.get("added", 0)

    def delete_contact_list_emails(self, list_id: str, emails: Sequence[str]) -> int:
        """Remove emails from a contact list. Returns count of emails removed."""
        data = self._request(
            "DELETE",
            f"/api/agent/lists/{list_id}/emails",
            body={"emails": list(emails)},
        )
        return data.get("deleted", 0)


class ContactsAsyncMixin:
    async def list_contact_lists(self, *, type: str | None = None) -> list[ContactList]:
        """List all contact lists, optionally filtered by ``type``."""
        params = {"type": type} if type else None
        data = await self._get("/api/agent/lists", params=params)
        if isinstance(data, list):
            return [ContactList.from_dict(cl) for cl in data]
        return [ContactList.from_dict(cl) for cl in data.get("lists", data)]

    async def create_contact_list(
        self,
        name: str,
        *,
        type: str | None = None,
        targets: Sequence[str] | None = None,
        emails: Sequence[str] | None = None,
    ) -> ContactList:
        """Create a new contact list."""
        body: dict[str, Any] = {"name": name}
        if type:
            body["type"] = type
        if targets:
            body["targets"] = list(targets)
        if emails:
            body["emails"] = list(emails)
        data = await self._post("/api/agent/lists", body)
        return ContactList.from_dict(data)

    async def get_contact_list(self, list_id: str) -> ContactList:
        """Get a contact list by ID."""
        data = await self._get(f"/api/agent/lists/{list_id}")
        return ContactList.from_dict(data)

    async def delete_contact_list(self, list_id: str) -> None:
        """Delete a contact list."""
        await self._request("DELETE", f"/api/agent/lists/{list_id}")

    async def list_contact_list_emails(self, list_id: str) -> list[str]:
        """List all emails in a contact list."""
        data = await self._get(f"/api/agent/lists/{list_id}/emails")
        if isinstance(data, list):
            return [e.get("email", e) if isinstance(e, dict) else e for e in data]
        return data.get("emails", [])

    async def add_contact_list_emails(
        self, list_id: str, emails: Sequence[str]
    ) -> int:
        """Add emails to a contact list. Returns count added."""
        data = await self._post(
            f"/api/agent/lists/{list_id}/emails", {"emails": list(emails)}
        )
        return data.get("added", 0)

    async def delete_contact_list_emails(
        self, list_id: str, emails: Sequence[str]
    ) -> int:
        """Remove emails from a contact list. Returns count removed."""
        data = await self._request(
            "DELETE",
            f"/api/agent/lists/{list_id}/emails",
            body={"emails": list(emails)},
        )
        return data.get("deleted", 0)
