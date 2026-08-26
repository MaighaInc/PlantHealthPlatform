"""Frame validation — reject invalid captures before publish/downstream CV."""

from __future__ import annotations

import numpy as np

from plant_health_camera.frame import CameraFrame


class FrameValidationError(ValueError):
    """Frame failed validation."""


def validate_frame(
    frame: CameraFrame | None,
    *,
    expect_width: int | None = None,
    expect_height: int | None = None,
    reject_blank: bool = True,
) -> CameraFrame:
    if frame is None:
        raise FrameValidationError("frame is None (capture failed)")

    img = frame.image
    if not isinstance(img, np.ndarray):
        raise FrameValidationError("image must be a numpy ndarray")
    if img.size == 0:
        raise FrameValidationError("image is empty")
    if img.ndim not in (2, 3):
        raise FrameValidationError(f"image ndim must be 2 or 3, got {img.ndim}")
    if img.ndim == 3 and img.shape[2] not in (1, 3, 4):
        raise FrameValidationError(f"unsupported channel count: {img.shape[2]}")
    if img.dtype != np.uint8:
        raise FrameValidationError(f"image dtype must be uint8, got {img.dtype}")

    h, w = int(img.shape[0]), int(img.shape[1])
    if frame.height != h or frame.width != w:
        raise FrameValidationError(
            f"metadata size ({frame.width}x{frame.height}) != array ({w}x{h})"
        )
    if expect_width is not None and w != expect_width:
        raise FrameValidationError(f"expected width {expect_width}, got {w}")
    if expect_height is not None and h != expect_height:
        raise FrameValidationError(f"expected height {expect_height}, got {h}")

    if reject_blank and _is_blank(img):
        raise FrameValidationError("image appears blank (all zeros)")

    return frame


def _is_blank(img: np.ndarray) -> bool:
    return bool(np.max(img) == 0)
