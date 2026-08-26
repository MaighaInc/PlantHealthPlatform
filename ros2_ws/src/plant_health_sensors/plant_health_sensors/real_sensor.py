"""Stub for real hardware sensors (BME280, DHT, soil probes, …)."""

from __future__ import annotations

from plant_health_sensors.interfaces import SensorInterface
from plant_health_sensors.readings import SensorReading
from plant_health_sensors.sensor_kinds import SensorKind


class RealSensorNotImplementedError(NotImplementedError):
    """Raised until a concrete hardware driver is wired for this kind."""


class RealSensorStub(SensorInterface):
    """
    Placeholder real-sensor adapter for HARDWARE / PRODUCTION modes.

    ``read()`` raises until a driver is implemented (PHP-28 / hardware bring-up).
    """

    def __init__(self, *, kind: SensorKind, sensor_id: str | None = None) -> None:
        self._kind = kind
        self._sensor_id = sensor_id or f"real_{kind.value}"

    @property
    def kind(self) -> SensorKind:
        return self._kind

    @property
    def sensor_id(self) -> str:
        return self._sensor_id

    def read(self) -> SensorReading:
        raise RealSensorNotImplementedError(
            f"Real sensor driver not implemented for kind={self._kind.value} "
            f"id={self._sensor_id}. Use SIMULATION/DEVELOPMENT or implement adapter."
        )
