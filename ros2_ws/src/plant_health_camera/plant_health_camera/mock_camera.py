"""Deterministic mock camera for unit tests."""

from __future__ import annotations

import numpy as np

from plant_health_camera.frame import CameraFrame, utc_now_iso
from plant_health_camera.interfaces import CameraInterface


class MockCamera(CameraInterface):
    """
    Returns a fixed sequence of frames / None (drop).

    ``frames`` entries are BGR images or None for a dropped frame.
    """

    def __init__(
        self,
        frames: list[np.ndarray | None],
        *,
        source_id: str = "mock",
    ) -> None:
        if not frames:
            raise ValueError("frames must be non-empty")
        self._frames = list(frames)
        self._source_id = source_id
        self._open = False
        self._index = 0
        self._frame_id = 0

    @property
    def source_id(self) -> str:
        return self._source_id

    def open(self) -> None:
        self._open = True
        self._index = 0
        self._frame_id = 0

    def read(self) -> CameraFrame | None:
        if not self._open:
            return None
        raw = self._frames[self._index % len(self._frames)]
        self._index += 1
        if raw is None:
            return None
        h, w = raw.shape[:2]
        frame = CameraFrame(
            image=raw.copy(),
            timestamp_iso=utc_now_iso(),
            frame_id=self._frame_id,
            source=self._source_id,
            width=w,
            height=h,
        )
        self._frame_id += 1
        return frame

    def release(self) -> None:
        self._open = False

    def is_open(self) -> bool:
        return self._open
