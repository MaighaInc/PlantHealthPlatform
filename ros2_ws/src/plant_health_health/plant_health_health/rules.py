"""Configurable rule-based plant health evaluation (no ROS, no GPIO)."""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum


class HealthStatus(str, Enum):
    HEALTHY = "healthy"
    STRESSED = "stressed"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class HealthRulesConfig:
    """Externalized thresholds — never bury these in ROS callbacks."""

    soil_dry_threshold: float = 30.0
    """Soil moisture (%) below this is considered dry."""

    temp_hot_threshold: float = 32.0
    """Temperature (°C) above this with dry soil → water stress."""

    soil_wet_floor: float = 0.0
    soil_wet_ceil: float = 100.0
    temp_min_plausible: float = -20.0
    temp_max_plausible: float = 60.0

    def validate(self) -> None:
        if self.soil_dry_threshold < self.soil_wet_floor:
            raise ValueError("soil_dry_threshold below soil_wet_floor")
        if self.temp_hot_threshold < self.temp_min_plausible:
            raise ValueError("temp_hot_threshold below temp_min_plausible")


@dataclass(frozen=True)
class HealthInputs:
    soil_moisture: float | None = None
    temperature: float | None = None
    humidity: float | None = None
    light: float | None = None


@dataclass(frozen=True)
class HealthAssessment:
    status: HealthStatus
    score: float
    """1.0 healthy … 0.0 unknown/failed."""

    reason: str
    confidence: float
    timestamp_iso: str
    rules_fired: tuple[str, ...] = ()

    def to_message_data(self) -> str:
        """Stable std_msgs/String payload for /plant/health."""
        return (
            f"status={self.status.value};score={self.score:.3f};"
            f"reason={self.reason};confidence={self.confidence:.3f};"
            f"ts={self.timestamp_iso}"
        )


def _is_invalid_number(value: float | None) -> bool:
    if value is None:
        return True
    try:
        return math.isnan(float(value)) or math.isinf(float(value))
    except (TypeError, ValueError):
        return True


def evaluate_health(
    inputs: HealthInputs,
    config: HealthRulesConfig | None = None,
    *,
    timestamp_iso: str | None = None,
) -> HealthAssessment:
    """
    Deterministic health rules (Stage 1 — pre-ML).

    Priority:
      1. Invalid / out-of-range sensors → UNKNOWN
      2. Dry soil AND hot temperature → stressed (water_stress)
      3. Dry soil alone → stressed (dry_soil)
      4. Otherwise → healthy
    """
    cfg = config or HealthRulesConfig()
    cfg.validate()
    ts = timestamp_iso or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    soil = inputs.soil_moisture
    temp = inputs.temperature

    if _is_invalid_number(soil) or _is_invalid_number(temp):
        return HealthAssessment(
            status=HealthStatus.UNKNOWN,
            score=0.0,
            reason="invalid_sensor",
            confidence=1.0,
            timestamp_iso=ts,
            rules_fired=("invalid_sensor",),
        )

    assert soil is not None and temp is not None
    soil_f = float(soil)
    temp_f = float(temp)

    if not (cfg.soil_wet_floor <= soil_f <= cfg.soil_wet_ceil):
        return HealthAssessment(
            status=HealthStatus.UNKNOWN,
            score=0.0,
            reason="soil_out_of_range",
            confidence=1.0,
            timestamp_iso=ts,
            rules_fired=("soil_out_of_range",),
        )
    if not (cfg.temp_min_plausible <= temp_f <= cfg.temp_max_plausible):
        return HealthAssessment(
            status=HealthStatus.UNKNOWN,
            score=0.0,
            reason="temperature_out_of_range",
            confidence=1.0,
            timestamp_iso=ts,
            rules_fired=("temperature_out_of_range",),
        )

    dry = soil_f < cfg.soil_dry_threshold
    hot = temp_f > cfg.temp_hot_threshold

    if dry and hot:
        return HealthAssessment(
            status=HealthStatus.STRESSED,
            score=0.35,
            reason="water_stress",
            confidence=1.0,
            timestamp_iso=ts,
            rules_fired=("dry_soil", "hot_temperature", "water_stress"),
        )
    if dry:
        return HealthAssessment(
            status=HealthStatus.STRESSED,
            score=0.45,
            reason="dry_soil",
            confidence=1.0,
            timestamp_iso=ts,
            rules_fired=("dry_soil",),
        )

    return HealthAssessment(
        status=HealthStatus.HEALTHY,
        score=1.0,
        reason="nominal",
        confidence=1.0,
        timestamp_iso=ts,
        rules_fired=("nominal",),
    )


def parse_health_message(data: str) -> dict[str, str]:
    if not data or ";" not in data:
        raise ValueError(f"malformed health message: {data!r}")
    parts: dict[str, str] = {}
    for token in data.split(";"):
        if "=" not in token:
            raise ValueError(f"malformed token: {token!r}")
        key, value = token.split("=", 1)
        parts[key] = value
    required = {"status", "score", "reason", "confidence", "ts"}
    missing = required - set(parts)
    if missing:
        raise ValueError(f"health message missing keys: {sorted(missing)}")
    return parts
