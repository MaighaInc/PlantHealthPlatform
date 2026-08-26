"""Sensor port — application code depends on this, not device drivers."""

from __future__ import annotations

from abc import ABC, abstractmethod

from plant_health_sensors.readings import SensorReading
from plant_health_sensors.sensor_kinds import SensorKind


class SensorInterface(ABC):
    """Hardware-agnostic sensor contract (PHP-04)."""

    @property
    @abstractmethod
    def kind(self) -> SensorKind:
        """Sensor measurement kind."""

    @property
    @abstractmethod
    def sensor_id(self) -> str:
        """Stable identifier for logging and datasets."""

    @abstractmethod
    def read(self) -> SensorReading:
        """Acquire one sample (may be invalid)."""
