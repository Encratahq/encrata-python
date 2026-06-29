"""Face search types."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class FaceMatch:
    """A watchlist match with confidence and bounding box."""
    uuid: str = ""
    name: str = ""
    probability: float = 0.0
    left: int = 0
    top: int = 0
    right: int = 0
    bottom: int = 0

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> FaceMatch:
        return cls(
            uuid=data.get("uuid", ""),
            name=data.get("name", ""),
            probability=data.get("probability", 0.0),
            left=data.get("left", 0),
            top=data.get("top", 0),
            right=data.get("right", 0),
            bottom=data.get("bottom", 0),
        )


@dataclass
class FaceSearch:
    """Face search result: watchlist matches with confidence and bounding boxes."""
    image_url: str = ""
    matched: bool = False
    threshold: float = 0.0
    faces_detected: int = 0
    matches: list[FaceMatch] = field(default_factory=list)
    credits: float = 0.0
    latency_ms: int = 0

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> FaceSearch:
        return cls(
            image_url=data.get("image_url", ""),
            matched=data.get("matched", False),
            threshold=data.get("threshold", 0.0),
            faces_detected=data.get("faces_detected", 0),
            matches=[FaceMatch.from_dict(m) for m in data.get("matches", [])],
            credits=data.get("credits", 0.0),
            latency_ms=data.get("latency_ms", 0),
        )
