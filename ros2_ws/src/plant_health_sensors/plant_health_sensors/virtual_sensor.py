"""Virtual sensor simulation — deterministic, configurable, no ROS required."""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from datetime import datetime, timezone

from plant_health_sensors.sensor_kinds import SensorKind


@dataclass(frozen=True)
class SensorReading:
    """One sample from a virtual (or later real) sensor."""

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


@dataclass(frozen=True)
class VirtualSensorConfig:
    kind: SensorKind
    sensor_id: str
    base_value: float
    min_value: float
    max_value: float
    noise_std: float = 0.5
    outlier_probability: float = 0.0
    outlier_delta: float = 15.0
    invalid_probability: float = 0.0
    seed: int | None = None

    def validate(self) -> None:
        if self.min_value > self.max_value:
            raise ValueError(
                f"min_value ({self.min_value}) > max_value ({self.max_value})"
            )
        if not (self.min_value <= self.base_value <= self.max_value):
            raise ValueError(
                f"base_value {self.base_value} outside "
                f"[{self.min_value}, {self.max_value}]"
            )
        if self.noise_std < 0:
            raise ValueError("noise_std must be >= 0")
        for name, prob in (
            ("outlier_probability", self.outlier_probability),
            ("invalid_probability", self.invalid_probability),
        ):
            if not 0.0 <= prob <= 1.0:
                raise ValueError(f"{name} must be in [0, 1], got {prob}")
        if not self.sensor_id.strip():
            raise ValueError("sensor_id must be non-empty")


class VirtualSensor:
    """
    Configurable virtual sensor with noise, outliers, and invalid injection.

    Use a fixed ``seed`` for reproducible tests.
    """

    def __init__(self, config: VirtualSensorConfig) -> None:
        config.validate()
        self._config = config
        self._rng = random.Random(config.seed)
        self._sequence = 0

    @property
    def config(self) -> VirtualSensorConfig:
        return self._config

    @property
    def sequence(self) -> int:
        return self._sequence

    def read(self) -> SensorReading:
        """Draw the next sample."""
        cfg = self._config
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        self._sequence += 1

        if self._rng.random() < cfg.invalid_probability:
            return SensorReading(
                kind=cfg.kind,
                value=None,
                timestamp_iso=ts,
                sensor_id=cfg.sensor_id,
                is_invalid=True,
            )

        is_outlier = self._rng.random() < cfg.outlier_probability
        noise = self._rng.gauss(0.0, cfg.noise_std) if cfg.noise_std > 0 else 0.0
        value = cfg.base_value + noise
        if is_outlier:
            sign = -1.0 if self._rng.random() < 0.5 else 1.0
            value += sign * cfg.outlier_delta

        value = min(cfg.max_value, max(cfg.min_value, value))
        return SensorReading(
            kind=cfg.kind,
            value=value,
            timestamp_iso=ts,
            sensor_id=cfg.sensor_id,
            is_outlier=is_outlier,
            is_invalid=False,
        )


def reading_to_float32(reading: SensorReading) -> float:
    """Map a reading to Float32 payload; invalid → NaN."""
    if not reading.is_valid or reading.value is None:
        return float("nan")
    return float(reading.value)


def is_invalid_float(value: float) -> bool:
    return math.isnan(value)
