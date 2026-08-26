"""OpenCV pipeline result types."""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import numpy.typing as npt


@dataclass(frozen=True)
class BoundingBox:
    x: int
    y: int
    width: int
    height: int


@dataclass
class PipelineResult:
    """Outputs of one CV pipeline pass."""

    processed_bgr: npt.NDArray[np.uint8]
    mask: npt.NDArray[np.uint8]
    roi_bgr: npt.NDArray[np.uint8] | None
    viz_bgr: npt.NDArray[np.uint8]
    features: dict[str, float] = field(default_factory=dict)
    bbox: BoundingBox | None = None
