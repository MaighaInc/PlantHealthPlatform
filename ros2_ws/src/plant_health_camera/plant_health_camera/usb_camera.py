"""USB camera via OpenCV VideoCapture."""

from __future__ import annotations

import time

import cv2

from plant_health_camera.frame import CameraFrame, utc_now_iso
from plant_health_camera.interfaces import CameraInterface


class UsbCamera(CameraInterface):
    """
    OpenCV USB capture with optional reconnect.

    Reconnect policy: after ``max_consecutive_failures`` failed reads, release and
    reopen once after ``reconnect_delay_sec``. Failures are returned as None
    (logged by the node) — never silent success with stale data.
    """

    def __init__(
        self,
        *,
        device_index: int = 0,
        width: int = 640,
        height: int = 480,
        fps: float = 15.0,
        reconnect_delay_sec: float = 1.0,
        max_consecutive_failures: int = 5,
    ) -> None:
        self._index = device_index
        self._width = width
        self._height = height
        self._fps = fps
        self._reconnect_delay_sec = reconnect_delay_sec
        self._max_failures = max_consecutive_failures
        self._cap: cv2.VideoCapture | None = None
        self._frame_id = 0
        self._consecutive_failures = 0
        self._source_id = f"usb_{device_index}"

    @property
    def source_id(self) -> str:
        return self._source_id

    def open(self) -> None:
        self.release()
        cap = cv2.VideoCapture(self._index)
        if not cap.isOpened():
            raise RuntimeError(f"failed to open USB camera index={self._index}")
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, float(self._width))
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, float(self._height))
        cap.set(cv2.CAP_PROP_FPS, float(self._fps))
        self._cap = cap
        self._consecutive_failures = 0
        self._frame_id = 0

    def read(self) -> CameraFrame | None:
        if self._cap is None or not self._cap.isOpened():
            self._consecutive_failures += 1
            self._maybe_reconnect()
            return None

        ok, img = self._cap.read()
        ts = utc_now_iso()
        if not ok or img is None:
            self._consecutive_failures += 1
            self._maybe_reconnect()
            return None

        self._consecutive_failures = 0
        h, w = img.shape[:2]
        frame = CameraFrame(
            image=img,
            timestamp_iso=ts,
            frame_id=self._frame_id,
            source=self._source_id,
            width=w,
            height=h,
        )
        self._frame_id += 1
        return frame

    def release(self) -> None:
        if self._cap is not None:
            self._cap.release()
            self._cap = None

    def is_open(self) -> bool:
        return self._cap is not None and self._cap.isOpened()

    def _maybe_reconnect(self) -> None:
        if self._consecutive_failures < self._max_failures:
            return
        self.release()
        time.sleep(self._reconnect_delay_sec)
        try:
            self.open()
        except RuntimeError:
            self._consecutive_failures = 0
