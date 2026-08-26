"""
Plant feature vector schema (PHP-10) — vision + sensor features for ML.

Schema version 1.0. Keys are stable; consumers should tolerate missing optional
sensor keys (null) but not invent values.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

SCHEMA_VERSION = "1.0"

# Ordered canonical keys for documentation and golden tests
VISION_FEATURE_KEYS: tuple[str, ...] = (
    "leaf_area",
    "green_pixel_ratio",
    "mean_hue",
    "mean_saturation",
    "mean_value",
    "contour_area",
    "bbox_x",
    "bbox_y",
    "bbox_w",
    "bbox_h",
    "centroid_x",
    "centroid_y",
)

SENSOR_FEATURE_KEYS: tuple[str, ...] = (
    "soil_moisture",
    "temperature",
    "humidity",
    "light",
    "co2",
)

ALL_FEATURE_KEYS: tuple[str, ...] = VISION_FEATURE_KEYS + SENSOR_FEATURE_KEYS


@dataclass
class FeatureVector:
    """Unified feature vector ready for logging / ML / ROS publish."""

    features: dict[str, float | None] = field(default_factory=dict)
    timestamp_iso: str = ""
    schema_version: str = SCHEMA_VERSION
    source: str = "plant_health_cv"

    def __post_init__(self) -> None:
        if not self.timestamp_iso:
            self.timestamp_iso = datetime.now(timezone.utc).strftime(
                "%Y-%m-%dT%H:%M:%S.%fZ"
            )

    def with_defaults(self) -> FeatureVector:
        """Ensure all schema keys exist (missing → None)."""
        merged = {key: None for key in ALL_FEATURE_KEYS}
        merged.update(self.features)
        return FeatureVector(
            features=merged,
            timestamp_iso=self.timestamp_iso,
            schema_version=self.schema_version,
            source=self.source,
        )

    def to_dict(self) -> dict[str, Any]:
        vec = self.with_defaults()
        return {
            "schema_version": vec.schema_version,
            "timestamp_iso": vec.timestamp_iso,
            "source": vec.source,
            "features": {k: vec.features.get(k) for k in ALL_FEATURE_KEYS},
        }

    def to_message_data(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":"))

    @classmethod
    def from_message_data(cls, data: str) -> FeatureVector:
        payload = json.loads(data)
        if "features" not in payload:
            raise ValueError("feature message missing 'features'")
        return cls(
            features=dict(payload["features"]),
            timestamp_iso=str(payload.get("timestamp_iso") or ""),
            schema_version=str(payload.get("schema_version") or SCHEMA_VERSION),
            source=str(payload.get("source") or "unknown"),
        ).with_defaults()


def build_feature_vector(
    vision: dict[str, float],
    *,
    soil_moisture: float | None = None,
    temperature: float | None = None,
    humidity: float | None = None,
    light: float | None = None,
    co2: float | None = None,
    timestamp_iso: str | None = None,
) -> FeatureVector:
    """Merge CV pipeline features with optional sensor readings."""
    features: dict[str, float | None] = {k: None for k in ALL_FEATURE_KEYS}
    for key in VISION_FEATURE_KEYS:
        if key in vision:
            features[key] = float(vision[key])
    features["soil_moisture"] = soil_moisture
    features["temperature"] = temperature
    features["humidity"] = humidity
    features["light"] = light
    features["co2"] = co2
    return FeatureVector(
        features=features,
        timestamp_iso=timestamp_iso
        or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
    ).with_defaults()
