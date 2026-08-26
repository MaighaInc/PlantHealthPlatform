"""Irrigation intent proposal (PHP-16) — never GPIO."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any


@dataclass(frozen=True)
class IrrigationIntent:
    water: bool
    reason: str
    fused_status: str
    fused_precedence: str
    confidence: float
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
            "water": bool(self.water),
            "reason": self.reason,
            "fused_status": self.fused_status,
            "fused_precedence": self.fused_precedence,
            "confidence": round(float(self.confidence), 3),
            "timestamp": self.timestamp_iso,
            "kind": "intent",
            "actuates": False,
        }

    def to_message_data(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":"))
