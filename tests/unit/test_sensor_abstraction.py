"""PHP-04: SensorInterface abstraction — consumers must not import device types."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

_PKG = Path(__file__).resolve().parents[2] / "ros2_ws" / "src" / "plant_health_sensors"
sys.path.insert(0, str(_PKG))

from plant_health_sensors.factory import (  # noqa: E402
    SensorFactoryError,
    create_sensor,
    create_sensors,
)
from plant_health_sensors.interfaces import SensorInterface  # noqa: E402
from plant_health_sensors.mock_sensor import MockSensor  # noqa: E402
from plant_health_sensors.real_sensor import (  # noqa: E402
    RealSensorNotImplementedError,
    RealSensorStub,
)
from plant_health_sensors.sampling import sample_all  # noqa: E402
from plant_health_sensors.sensor_kinds import SensorKind  # noqa: E402
from plant_health_sensors.virtual_sensor import VirtualSensor  # noqa: E402


def _consume(sensors: list[SensorInterface]) -> list[float | None]:
    """Example consumer: only SensorInterface methods — no isinstance on backends."""
    return [r.value for r in sample_all(sensors)]


def test_mock_sensor_deterministic_sequence() -> None:
    mock: SensorInterface = MockSensor(
        kind=SensorKind.SOIL_MOISTURE,
        sensor_id="mock_soil",
        values=[10.0, 20.0, None],
    )
    assert mock.read().value == 10.0
    assert mock.read().value == 20.0
    assert mock.read().is_invalid


def test_consumer_works_with_mock_and_virtual() -> None:
    mock = MockSensor(
        kind=SensorKind.TEMPERATURE,
        sensor_id="mock_temp",
        values=[25.0],
    )
    virtual = create_sensor(
        SensorKind.TEMPERATURE,
        mode="SIMULATION",
        backend="virtual",
        seed=1,
        noise_std=0.0,
    )
    assert _consume([mock]) == [25.0]
    assert _consume([virtual])[0] is not None


def test_factory_auto_simulation_uses_virtual() -> None:
    sensor = create_sensor(SensorKind.HUMIDITY, mode="SIMULATION", backend="auto")
    assert isinstance(sensor, VirtualSensor)
    assert isinstance(sensor, SensorInterface)


def test_factory_auto_hardware_uses_real_stub() -> None:
    sensor = create_sensor(SensorKind.LIGHT, mode="HARDWARE", backend="auto")
    assert isinstance(sensor, RealSensorStub)
    with pytest.raises(RealSensorNotImplementedError):
        sensor.read()


def test_factory_force_mock() -> None:
    sensor = create_sensor(
        SensorKind.CO2,
        mode="HARDWARE",
        backend="mock",
        mock_values=[400.0],
    )
    assert isinstance(sensor, MockSensor)
    assert sensor.read().value == 400.0


def test_create_sensors_list() -> None:
    sensors = create_sensors(
        (SensorKind.SOIL_MOISTURE, SensorKind.TEMPERATURE),
        mode="DEVELOPMENT",
        backend="mock",
    )
    assert len(sensors) == 2
    assert all(isinstance(s, SensorInterface) for s in sensors)
    values = _consume(sensors)
    assert len(values) == 2


def test_factory_rejects_bad_mode() -> None:
    with pytest.raises(SensorFactoryError, match="development_mode"):
        create_sensor(SensorKind.LIGHT, mode="STAGING")
