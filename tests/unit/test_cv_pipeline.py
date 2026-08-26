"""Unit tests for OpenCV pipeline stages — no ROS required."""

from __future__ import annotations

import sys
from pathlib import Path

import cv2
import numpy as np
import pytest

_PKG = Path(__file__).resolve().parents[2] / "ros2_ws" / "src" / "plant_health_cv"
sys.path.insert(0, str(_PKG))

from plant_health_cv.parameters import CvNodeParams, CvParameterError  # noqa: E402
from plant_health_cv.pipeline import (  # noqa: E402
    run_pipeline,
    segment_green_hsv,
    validate_bgr,
)


def _synthetic_plant(h: int = 120, w: int = 160) -> np.ndarray:
    img = np.zeros((h, w, 3), dtype=np.uint8)
    img[:] = (40, 70, 90)
    cv2.ellipse(img, (w // 2, h // 2), (w // 5, h // 4), 0, 0, 360, (40, 180, 50), -1)
    return img


def test_validate_rejects_wrong_shape() -> None:
    with pytest.raises(ValueError, match="BGR"):
        validate_bgr(np.zeros((10, 10), dtype=np.uint8))


def test_pipeline_detects_green_leaf() -> None:
    result = run_pipeline(_synthetic_plant(), width=160, height=120, blur_ksize=3)
    assert result.features["leaf_area"] > 0
    assert result.features["green_pixel_ratio"] > 0.01
    assert result.roi_bgr is not None
    assert result.bbox is not None
    assert result.viz_bgr.shape[:2] == (120, 160)


def test_pipeline_on_soil_only_has_low_green() -> None:
    soil = np.full((80, 80, 3), (40, 70, 90), dtype=np.uint8)
    result = run_pipeline(soil, width=80, height=80, blur_ksize=3)
    assert result.features["green_pixel_ratio"] < 0.05


def test_hue_range_affects_mask() -> None:
    img = _synthetic_plant()
    from plant_health_cv.pipeline import bgr_to_hsv, resize_bgr

    hsv = bgr_to_hsv(resize_bgr(img, width=80, height=60))
    wide = segment_green_hsv(hsv, h_min=30, h_max=90, s_min=20, v_min=20)
    narrow = segment_green_hsv(hsv, h_min=70, h_max=75, s_min=20, v_min=20)
    assert int(np.count_nonzero(wide)) >= int(np.count_nonzero(narrow))


def test_cv_params_reject_even_blur() -> None:
    with pytest.raises(CvParameterError, match="blur_ksize"):
        CvNodeParams.from_raw(
            process_width=320,
            process_height=240,
            blur_ksize=4,
            h_min=35,
            h_max=85,
            s_min=40,
            v_min=40,
        )


def test_sample_plant_png_pipeline() -> None:
    sample = (
        Path(__file__).resolve().parents[2]
        / "ros2_ws"
        / "src"
        / "plant_health_camera"
        / "plant_health_camera"
        / "data"
        / "samples"
        / "sample_plant.png"
    )
    if not sample.is_file():
        pytest.skip("sample_plant.png missing")
    bgr = cv2.imread(str(sample), cv2.IMREAD_COLOR)
    assert bgr is not None
    result = run_pipeline(bgr, width=320, height=240)
    assert result.features["leaf_area"] > 100
