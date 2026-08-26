"""Camera port — application code depends on this interface."""

from __future__ import annotations

from abc import ABC, abstractmethod

from plant_health_camera.frame import CameraFrame


class CameraInterface(ABC):
    """Hardware-agnostic camera contract (PHP-05)."""

    @property
    @abstractmethod
    def source_id(self) -> str:
        """Stable id for logs (e.g. usb_0, simulated, mock)."""

    @abstractmethod
    def open(self) -> None:
        """Acquire device or prepare simulation."""

    @abstractmethod
    def read(self) -> CameraFrame | None:
        """
        Capture one frame.

        Returns None on soft failure (dropped/unavailable); callers log and continue.
        """

    @abstractmethod
    def release(self) -> None:
        """Release OS/device resources. Safe to call multiple times."""

    @abstractmethod
    def is_open(self) -> bool:
        """Whether the camera is ready to read."""
