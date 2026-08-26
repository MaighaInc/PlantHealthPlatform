"""Shared sensor reading types (no ROS, no hardware)."""

from __future__ import annotations

import math
from dataclasses import dataclass

from plant_health_sensors.sensor_kinds import SensorKind


@dataclass(frozen=True)
class SensorReading:
    """One sample from any sensor backend."""

    kind: SensorKind
    value: float | None
    """Numeric reading, or None when the sample is invalid."""

    timestamp_iso: str
    sensor_id: str
    is_outlier: bool = False
    is_invalid: bool = False

    @property
    def is_valid(self) -> bool:
        return self.value is not None and not self.is_invalid


def reading_to_float32(reading: SensorReading) -> float:
    """Map a reading to Float32 payload; invalid → NaN."""
    if not reading.is_valid or reading.value is None:
        return float("nan")
    return float(reading.value)


def is_invalid_float(value: float) -> bool:
    return math.isnan(value)
