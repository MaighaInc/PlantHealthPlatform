"""Camera frame types — acquisition timestamp distinct from publish time."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

import numpy as np
import numpy.typing as npt


@dataclass(frozen=True)
class CameraFrame:
    """One captured image with acquisition metadata."""

    image: npt.NDArray[np.uint8]
    """BGR uint8 array shaped (H, W, 3) or grayscale (H, W)."""

    timestamp_iso: str
    frame_id: int
    source: str
    width: int
    height: int

    @property
    def channels(self) -> int:
        if self.image.ndim == 2:
            return 1
        return int(self.image.shape[2])


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
