"""Face search: match a probe image against your watchlist."""

from __future__ import annotations

from ..types import FaceSearch


class FaceSyncMixin:
    def face_search(self, image_url: str, *, threshold: float | None = None) -> FaceSearch:
        """Search a face against your watchlist by public image URL."""
        body: dict[str, object] = {"image_url": image_url}
        if threshold is not None:
            body["threshold"] = threshold
        data = self._post("/api/agent/face", body)
        return FaceSearch.from_dict(data)


class FaceAsyncMixin:
    async def face_search(self, image_url: str, *, threshold: float | None = None) -> FaceSearch:
        """Search a face against your watchlist by public image URL."""
        body: dict[str, object] = {"image_url": image_url}
        if threshold is not None:
            body["threshold"] = threshold
        data = await self._post("/api/agent/face", body)
        return FaceSearch.from_dict(data)
