"""Unit tests for camera acquisition — no ROS required."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

_PKG = Path(__file__).resolve().parents[2] / "ros2_ws" / "src" / "plant_health_camera"
sys.path.insert(0, str(_PKG))

from plant_health_camera.factory import create_camera  # noqa: E402
from plant_health_camera.interfaces import CameraInterface  # noqa: E402
from plant_health_camera.mock_camera import MockCamera  # noqa: E402
from plant_health_camera.parameters import CameraNodeParams, CameraParameterError  # noqa: E402
from plant_health_camera.simulated_camera import SimulatedCamera  # noqa: E402
from plant_health_camera.validation import FrameValidationError, validate_frame  # noqa: E402


def _bgr(h: int = 48, w: int = 64, value: int = 100) -> np.ndarray:
    return np.full((h, w, 3), value, dtype=np.uint8)


def test_validate_rejects_none() -> None:
    with pytest.raises(FrameValidationError, match="None"):
        validate_frame(None)


def test_validate_rejects_blank() -> None:
    cam = MockCamera([_bgr(value=0)])
    cam.open()
    frame = cam.read()
    with pytest.raises(FrameValidationError, match="blank"):
        validate_frame(frame, reject_blank=True)


def test_validate_accepts_normal_frame() -> None:
    cam = MockCamera([_bgr()])
    cam.open()
    frame = cam.read()
    assert frame is not None
    validated = validate_frame(frame)
    assert validated.width == 64


def test_mock_drop_returns_none() -> None:
    cam = MockCamera([_bgr(), None, _bgr()])
    cam.open()
    assert cam.read() is not None
    assert cam.read() is None
    assert cam.read() is not None


def test_mock_release_idempotent() -> None:
    cam = MockCamera([_bgr()])
    cam.open()
    cam.release()
    cam.release()
    assert not cam.is_open()
    assert cam.read() is None


def test_simulated_camera_produces_timestamped_frames() -> None:
    cam: CameraInterface = SimulatedCamera(width=64, height=48)
    cam.open()
    frame = cam.read()
    assert frame is not None
    assert frame.timestamp_iso.endswith("Z")
    assert frame.width == 64
    assert frame.height == 48
    validate_frame(frame)
    cam.release()
    assert not cam.is_open()


def test_factory_simulation_uses_simulated() -> None:
    cam = create_camera(mode="SIMULATION", backend="auto", width=32, height=32)
    assert isinstance(cam, SimulatedCamera)


def test_factory_development_auto_uses_usb_type() -> None:
    from plant_health_camera.usb_camera import UsbCamera

    cam = create_camera(mode="DEVELOPMENT", backend="auto")
    assert isinstance(cam, UsbCamera)


def test_params_reject_bad_period() -> None:
    with pytest.raises(CameraParameterError, match="publish_period_sec"):
        CameraNodeParams.from_raw(
            publish_period_sec=10.0,
            development_mode="SIMULATION",
            camera_backend="simulated",
            device_index=0,
            width=640,
            height=480,
            fps=15.0,
        )
