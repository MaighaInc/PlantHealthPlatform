"""Unit tests for virtual sensors — deterministic, no ROS."""

from __future__ import annotations

import math
import sys
from pathlib import Path

import pytest

_PKG = Path(__file__).resolve().parents[2] / "ros2_ws" / "src" / "plant_health_sensors"
sys.path.insert(0, str(_PKG))

from plant_health_sensors.parameters import (  # noqa: E402
    SensorParameterError,
    VirtualPublisherParams,
)
from plant_health_sensors.sensor_kinds import SensorKind  # noqa: E402
from plant_health_sensors.virtual_sensor import (  # noqa: E402
    VirtualSensor,
    VirtualSensorConfig,
    is_invalid_float,
    reading_to_float32,
)


def _cfg(**overrides: object) -> VirtualSensorConfig:
    base = dict(
        kind=SensorKind.SOIL_MOISTURE,
        sensor_id="virtual_soil",
        base_value=40.0,
        min_value=0.0,
        max_value=100.0,
        noise_std=0.0,
        outlier_probability=0.0,
        invalid_probability=0.0,
        seed=123,
    )
    base.update(overrides)
    return VirtualSensorConfig(**base)  # type: ignore[arg-type]


def test_deterministic_seed_reproducible() -> None:
    a = VirtualSensor(_cfg(noise_std=1.0, seed=7))
    b = VirtualSensor(_cfg(noise_std=1.0, seed=7))
    vals_a = [a.read().value for _ in range(5)]
    vals_b = [b.read().value for _ in range(5)]
    assert vals_a == vals_b


def test_values_clamped_to_bounds() -> None:
    sensor = VirtualSensor(
        _cfg(base_value=99.0, noise_std=0.0, outlier_probability=1.0, outlier_delta=50.0)
    )
    for _ in range(20):
        reading = sensor.read()
        assert reading.value is not None
        assert 0.0 <= reading.value <= 100.0


def test_invalid_injection() -> None:
    sensor = VirtualSensor(_cfg(invalid_probability=1.0))
    reading = sensor.read()
    assert reading.is_invalid
    assert reading.value is None
    assert math.isnan(reading_to_float32(reading))
    assert is_invalid_float(reading_to_float32(reading))


def test_outlier_flag() -> None:
    sensor = VirtualSensor(
        _cfg(outlier_probability=1.0, outlier_delta=10.0, noise_std=0.0)
    )
    reading = sensor.read()
    assert reading.is_outlier
    assert reading.is_valid


def test_config_rejects_bad_bounds() -> None:
    with pytest.raises(ValueError, match="min_value"):
        _cfg(min_value=50.0, max_value=10.0).validate()


def test_publisher_params_parse_kinds() -> None:
    params = VirtualPublisherParams.from_raw(
        sample_period_sec=1.0,
        enabled_kinds="temperature,humidity",
        seed=1,
        noise_std=0.2,
        outlier_probability=0.0,
        invalid_probability=0.0,
    )
    assert params.enabled_kinds == (SensorKind.TEMPERATURE, SensorKind.HUMIDITY)


def test_publisher_params_reject_bad_period() -> None:
    with pytest.raises(SensorParameterError, match="sample_period_sec"):
        VirtualPublisherParams.from_raw(
            sample_period_sec=0.0,
            enabled_kinds="light",
            seed=1,
            noise_std=0.0,
            outlier_probability=0.0,
            invalid_probability=0.0,
        )


def test_publisher_params_reject_unknown_kind() -> None:
    with pytest.raises(SensorParameterError, match="unknown sensor kind"):
        VirtualPublisherParams.from_raw(
            sample_period_sec=1.0,
            enabled_kinds="soil_moisture,magic",
            seed=1,
            noise_std=0.0,
            outlier_probability=0.0,
            invalid_probability=0.0,
        )
