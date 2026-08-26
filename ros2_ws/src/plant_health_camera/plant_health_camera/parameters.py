"""Camera node parameter validation (no rclpy)."""

from __future__ import annotations

from dataclasses import dataclass

from plant_health_camera.factory import CameraFactoryError, normalize_mode


class CameraParameterError(ValueError):
    """Invalid camera ROS/runtime parameter."""


def validate_period_sec(period: float) -> float:
    try:
        value = float(period)
    except (TypeError, ValueError) as exc:
        raise CameraParameterError(f"publish_period_sec must be a number: {period!r}") from exc
    if value < 0.05 or value > 5.0:
        raise CameraParameterError(
            f"publish_period_sec must be in [0.05, 5.0], got {value}"
        )
    return value


def validate_positive_int(name: str, value: int, *, minimum: int = 0) -> int:
    try:
        iv = int(value)
    except (TypeError, ValueError) as exc:
        raise CameraParameterError(f"{name} must be an int") from exc
    if iv < minimum:
        raise CameraParameterError(f"{name} must be >= {minimum}, got {iv}")
    return iv


def validate_backend(backend: str) -> str:
    choice = backend.strip().lower()
    if choice not in {"auto", "simulated", "usb"}:
        raise CameraParameterError(
            f"camera_backend must be auto|simulated|usb, got {backend!r}"
        )
    return choice


@dataclass(frozen=True)
class CameraNodeParams:
    publish_period_sec: float
    development_mode: str
    camera_backend: str
    device_index: int
    width: int
    height: int
    fps: float
    topic: str = "/camera/image_raw"

    @classmethod
    def from_raw(
        cls,
        *,
        publish_period_sec: float,
        development_mode: str,
        camera_backend: str,
        device_index: int,
        width: int,
        height: int,
        fps: float,
        topic: str = "/camera/image_raw",
    ) -> CameraNodeParams:
        try:
            mode = normalize_mode(development_mode)
        except CameraFactoryError as exc:
            raise CameraParameterError(str(exc)) from exc
        topic = topic.strip()
        if not topic.startswith("/"):
            raise CameraParameterError(f"topic must be absolute, got {topic!r}")
        if float(fps) <= 0 or float(fps) > 60:
            raise CameraParameterError(f"fps must be in (0, 60], got {fps}")
        return cls(
            publish_period_sec=validate_period_sec(publish_period_sec),
            development_mode=mode,
            camera_backend=validate_backend(camera_backend),
            device_index=validate_positive_int("device_index", device_index, minimum=0),
            width=validate_positive_int("width", width, minimum=16),
            height=validate_positive_int("height", height, minimum=16),
            fps=float(fps),
            topic=topic,
        )
