"""Build CameraInterface from development mode."""

from __future__ import annotations

from pathlib import Path

from plant_health_camera.interfaces import CameraInterface
from plant_health_camera.simulated_camera import SimulatedCamera
from plant_health_camera.usb_camera import UsbCamera

_HARDWARE_USB_MODES = frozenset({"DEVELOPMENT", "HARDWARE", "PRODUCTION"})
_VALID_MODES = frozenset({"SIMULATION", "DEVELOPMENT", "HARDWARE", "PRODUCTION"})


class CameraFactoryError(ValueError):
    """Invalid camera factory arguments."""


def normalize_mode(mode: str) -> str:
    value = mode.strip().upper()
    if value not in _VALID_MODES:
        raise CameraFactoryError(
            f"development_mode must be one of {sorted(_VALID_MODES)}, got {mode!r}"
        )
    return value


def create_camera(
    *,
    mode: str = "SIMULATION",
    backend: str = "auto",
    device_index: int = 0,
    width: int = 640,
    height: int = 480,
    fps: float = 15.0,
    sample_dir: Path | None = None,
) -> CameraInterface:
    """
    ``backend``: auto | simulated | usb

    auto:
      - SIMULATION → SimulatedCamera
      - DEVELOPMENT/HARDWARE/PRODUCTION → UsbCamera
    """
    mode_n = normalize_mode(mode)
    choice = backend.strip().lower()
    if choice == "auto":
        choice = "usb" if mode_n in _HARDWARE_USB_MODES else "simulated"
    if choice == "simulated":
        samples: list[Path] = []
        if sample_dir is not None and sample_dir.is_dir():
            samples = sorted(sample_dir.glob("*.png")) + sorted(sample_dir.glob("*.jpg"))
        return SimulatedCamera(width=width, height=height, sample_paths=samples)
    if choice == "usb":
        return UsbCamera(
            device_index=device_index,
            width=width,
            height=height,
            fps=fps,
        )
    raise CameraFactoryError(f"backend must be auto|simulated|usb, got {backend!r}")
