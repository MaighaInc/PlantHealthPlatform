"""Deterministic mock sensor for unit/integration tests."""

from __future__ import annotations

from datetime import datetime, timezone

from plant_health_sensors.interfaces import SensorInterface
from plant_health_sensors.readings import SensorReading
from plant_health_sensors.sensor_kinds import SensorKind


class MockSensor(SensorInterface):
    """
    Returns a fixed sequence of values (cycles).

    Use in tests to prove consumers depend only on SensorInterface.
    """

    def __init__(
        self,
        *,
        kind: SensorKind,
        sensor_id: str,
        values: list[float | None],
    ) -> None:
        if not values:
            raise ValueError("values must be non-empty")
        if not sensor_id.strip():
            raise ValueError("sensor_id must be non-empty")
        self._kind = kind
        self._sensor_id = sensor_id
        self._values = list(values)
        self._index = 0

    @property
    def kind(self) -> SensorKind:
        return self._kind

    @property
    def sensor_id(self) -> str:
        return self._sensor_id

    def read(self) -> SensorReading:
        raw = self._values[self._index % len(self._values)]
        self._index += 1
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        if raw is None:
            return SensorReading(
                kind=self._kind,
                value=None,
                timestamp_iso=ts,
                sensor_id=self._sensor_id,
                is_invalid=True,
            )
        return SensorReading(
            kind=self._kind,
            value=float(raw),
            timestamp_iso=ts,
            sensor_id=self._sensor_id,
        )
