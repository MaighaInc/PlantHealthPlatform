"""Factory: build SensorInterface implementations from development mode."""

from __future__ import annotations

from plant_health_sensors.interfaces import SensorInterface
from plant_health_sensors.mock_sensor import MockSensor
from plant_health_sensors.real_sensor import RealSensorStub
from plant_health_sensors.sensor_kinds import (
    DEFAULT_BASE_VALUES,
    DEFAULT_BOUNDS,
    SensorKind,
)
from plant_health_sensors.virtual_sensor import VirtualSensor, VirtualSensorConfig

_HARDWARE_MODES = frozenset({"HARDWARE", "PRODUCTION"})
_VALID_MODES = frozenset({"SIMULATION", "DEVELOPMENT", "HARDWARE", "PRODUCTION"})


class SensorFactoryError(ValueError):
    """Invalid factory arguments."""


def normalize_mode(mode: str) -> str:
    value = mode.strip().upper()
    if value not in _VALID_MODES:
        raise SensorFactoryError(
            f"development_mode must be one of {sorted(_VALID_MODES)}, got {mode!r}"
        )
    return value


def create_sensor(
    kind: SensorKind,
    *,
    mode: str = "SIMULATION",
    backend: str = "auto",
    seed: int = 0,
    noise_std: float = 0.5,
    outlier_probability: float = 0.0,
    invalid_probability: float = 0.0,
    mock_values: list[float | None] | None = None,
) -> SensorInterface:
    """
    Create one sensor for ``kind``.

    ``backend``:
      - ``auto`` — mode-based (SIMULATION/DEVELOPMENT → virtual; HARDWARE/PRODUCTION → real stub)
      - ``virtual`` — force VirtualSensor
      - ``mock`` — force MockSensor
      - ``real`` — force RealSensorStub
    """
    mode_n = normalize_mode(mode)
    resolved = _resolve_backend(mode=mode_n, backend=backend)

    if resolved == "mock":
        values = mock_values if mock_values is not None else [DEFAULT_BASE_VALUES[kind]]
        return MockSensor(
            kind=kind,
            sensor_id=f"mock_{kind.value}",
            values=values,
        )

    if resolved == "real":
        return RealSensorStub(kind=kind)

    if resolved == "virtual":
        lo, hi = DEFAULT_BOUNDS[kind]
        cfg = VirtualSensorConfig(
            kind=kind,
            sensor_id=f"virtual_{kind.value}",
            base_value=DEFAULT_BASE_VALUES[kind],
            min_value=lo,
            max_value=hi,
            noise_std=noise_std,
            outlier_probability=outlier_probability,
            invalid_probability=invalid_probability,
            seed=seed,
        )
        return VirtualSensor(cfg)

    raise SensorFactoryError(f"unknown resolved backend {resolved!r}")


def create_sensors(
    kinds: tuple[SensorKind, ...] | list[SensorKind],
    *,
    mode: str = "SIMULATION",
    backend: str = "auto",
    seed: int = 42,
    noise_std: float = 0.5,
    outlier_probability: float = 0.0,
    invalid_probability: float = 0.0,
) -> list[SensorInterface]:
    """Create a list of sensors — consumer should only see SensorInterface."""
    sensors: list[SensorInterface] = []
    for index, kind in enumerate(kinds):
        sensors.append(
            create_sensor(
                kind,
                mode=mode,
                backend=backend,
                seed=seed + index,
                noise_std=noise_std,
                outlier_probability=outlier_probability,
                invalid_probability=invalid_probability,
            )
        )
    return sensors


def _resolve_backend(*, mode: str, backend: str) -> str:
    choice = backend.strip().lower()
    if choice == "auto":
        if mode in _HARDWARE_MODES:
            return "real"
        return "virtual"
    if choice in {"virtual", "mock", "real"}:
        return choice
    raise SensorFactoryError(
        f"backend must be auto|virtual|mock|real, got {backend!r}"
    )
