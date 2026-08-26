"""Unified fused health representation for decision consumers (PHP-15)."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any


@dataclass(frozen=True)
class FusedHealth:
    status: str
    score: float
    confidence: float
    reason: str
    precedence: str
    sources: dict[str, Any]
    timestamp_iso: str = ""

    def __post_init__(self) -> None:
        if not self.timestamp_iso:
            object.__setattr__(
                self,
                "timestamp_iso",
                datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "score": round(float(self.score), 3),
            "confidence": round(float(self.confidence), 3),
            "reason": self.reason,
            "precedence": self.precedence,
            "sources": self.sources,
            "timestamp": self.timestamp_iso,
        }

    def to_message_data(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":"))
