"""Factory: build GPIOInterface from development mode (PHP-17)."""

from __future__ import annotations

from plant_health_irrigation.interfaces import GPIOInterface
from plant_health_irrigation.mock_gpio import MockGPIO
from plant_health_irrigation.rpi_gpio import RaspberryPiGPIO

_VALID_MODES = frozenset({"SIMULATION", "DEVELOPMENT", "HARDWARE", "PRODUCTION"})
_MOCK_MODES = frozenset({"SIMULATION", "DEVELOPMENT"})


class GPIOFactoryError(ValueError):
    """Invalid factory arguments."""


def normalize_mode(mode: str) -> str:
    value = mode.strip().upper()
    if value not in _VALID_MODES:
        raise GPIOFactoryError(
            f"development_mode must be one of {sorted(_VALID_MODES)}, got {mode!r}"
        )
    return value


def create_gpio(
    *,
    mode: str = "SIMULATION",
    backend: str = "auto",
) -> GPIOInterface:
    """
    Create a GPIO backend.

    ``backend``:
      - ``auto`` — SIMULATION/DEVELOPMENT → MockGPIO; HARDWARE/PRODUCTION → RaspberryPiGPIO
      - ``mock`` — force MockGPIO
      - ``rpi`` — force RaspberryPiGPIO
    """
    mode_n = normalize_mode(mode)
    resolved = _resolve_backend(mode=mode_n, backend=backend)
    if resolved == "mock":
        return MockGPIO()
    if resolved == "rpi":
        return RaspberryPiGPIO()
    raise GPIOFactoryError(f"unresolved backend: {resolved!r}")


def _resolve_backend(*, mode: str, backend: str) -> str:
    key = backend.strip().lower()
    if key == "auto":
        return "mock" if mode in _MOCK_MODES else "rpi"
    if key in {"mock", "rpi"}:
        # Acceptance: SIMULATION/DEVELOPMENT must use MockGPIO exclusively
        if mode in _MOCK_MODES and key == "rpi":
            raise GPIOFactoryError(
                f"{mode} must use MockGPIO exclusively (refusing backend=rpi)"
            )
        return key
    raise GPIOFactoryError("backend must be auto, mock, or rpi")
