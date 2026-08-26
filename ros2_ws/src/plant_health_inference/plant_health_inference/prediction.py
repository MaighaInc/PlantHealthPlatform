"""Prediction result schema for /plant/disease_prediction (PHP-14)."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any


@dataclass(frozen=True)
class PredictionResult:
    prediction: str
    confidence: float
    model_name: str
    model_version: str
    latency_ms: float
    timestamp_iso: str = ""
    unknown_reason: str | None = None

    def __post_init__(self) -> None:
        if not self.timestamp_iso:
            object.__setattr__(
                self,
                "timestamp_iso",
                datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "prediction": self.prediction,
            "confidence": round(float(self.confidence), 6),
            "model_name": self.model_name,
            "model_version": self.model_version,
            "latency_ms": round(float(self.latency_ms), 3),
            "timestamp": self.timestamp_iso,
            "unknown_reason": self.unknown_reason,
        }

    def to_message_data(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":"))
