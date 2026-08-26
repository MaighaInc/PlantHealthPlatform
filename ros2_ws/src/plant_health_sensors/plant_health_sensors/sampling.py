"""Sensor sampling helpers that depend only on SensorInterface."""

from __future__ import annotations

from collections.abc import Sequence

from plant_health_sensors.interfaces import SensorInterface
from plant_health_sensors.readings import SensorReading


def sample_all(sensors: Sequence[SensorInterface]) -> list[SensorReading]:
    """Read every sensor once — no knowledge of virtual/mock/real."""
    return [sensor.read() for sensor in sensors]
