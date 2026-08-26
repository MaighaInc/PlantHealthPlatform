"""Simulated camera — sample images for SIMULATION mode (no USB)."""

from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np

from plant_health_camera.frame import CameraFrame, utc_now_iso
from plant_health_camera.interfaces import CameraInterface


class SimulatedCamera(CameraInterface):
    """
    Cycles through sample images or generates a synthetic plant-like frame.

    Never requires physical hardware.
    """

    def __init__(
        self,
        *,
        width: int = 640,
        height: int = 480,
        sample_paths: list[Path] | None = None,
        source_id: str = "simulated",
    ) -> None:
        if width < 16 or height < 16:
            raise ValueError("width/height must be >= 16")
        self._width = width
        self._height = height
        self._sample_paths = list(sample_paths or [])
        self._source_id = source_id
        self._open = False
        self._frame_id = 0
        self._images: list[np.ndarray] = []

    @property
    def source_id(self) -> str:
        return self._source_id

    def open(self) -> None:
        self._images = []
        for path in self._sample_paths:
            if path.is_file():
                img = cv2.imread(str(path), cv2.IMREAD_COLOR)
                if img is not None:
                    resized = cv2.resize(img, (self._width, self._height))
                    self._images.append(resized)
        if not self._images:
            self._images.append(self._synthesize())
        self._open = True
        self._frame_id = 0

    def read(self) -> CameraFrame | None:
        if not self._open:
            return None
        img = self._images[self._frame_id % len(self._images)]
        frame = CameraFrame(
            image=img.copy(),
            timestamp_iso=utc_now_iso(),
            frame_id=self._frame_id,
            source=self._source_id,
            width=self._width,
            height=self._height,
        )
        self._frame_id += 1
        return frame

    def release(self) -> None:
        self._open = False
        self._images = []

    def is_open(self) -> bool:
        return self._open

    def _synthesize(self) -> np.ndarray:
        """Simple green 'leaf' blob on soil-colored background."""
        img = np.zeros((self._height, self._width, 3), dtype=np.uint8)
        img[:, :] = (40, 70, 90)  # BGR soil-ish
        center = (self._width // 2, self._height // 2)
        axes = (self._width // 5, self._height // 4)
        cv2.ellipse(img, center, axes, 0, 0, 360, (40, 160, 60), -1)
        return img
