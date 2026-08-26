"""Golden / schema tests for PHP-10 feature vectors."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import cv2
import numpy as np
import pytest

_PKG = Path(__file__).resolve().parents[2] / "ros2_ws" / "src" / "plant_health_cv"
sys.path.insert(0, str(_PKG))

from plant_health_cv.features import (  # noqa: E402
    ALL_FEATURE_KEYS,
    SCHEMA_VERSION,
    FeatureVector,
    build_feature_vector,
)
from plant_health_cv.pipeline import run_pipeline  # noqa: E402


def _golden_plant(h: int = 120, w: int = 160) -> np.ndarray:
    """Deterministic synthetic plant used as golden fixture."""
    rng = np.random.default_rng(0)
    img = np.zeros((h, w, 3), dtype=np.uint8)
    img[:] = (40, 70, 90)
    cv2.ellipse(img, (w // 2, h // 2), (w // 5, h // 4), 0, 0, 360, (40, 180, 50), -1)
    # tiny deterministic noise that must not change segmentation materially
    noise = rng.integers(0, 3, size=img.shape, dtype=np.uint8)
    return cv2.add(img, noise)


def test_schema_contains_vision_and_sensor_keys() -> None:
    assert "leaf_area" in ALL_FEATURE_KEYS
    assert "green_pixel_ratio" in ALL_FEATURE_KEYS
    assert "soil_moisture" in ALL_FEATURE_KEYS
    assert "temperature" in ALL_FEATURE_KEYS


def test_golden_image_feature_ranges() -> None:
    result = run_pipeline(_golden_plant(), width=160, height=120, blur_ksize=3)
    vector = build_feature_vector(
        result.features,
        soil_moisture=41.2,
        temperature=27.8,
        humidity=63.4,
        light=812.0,
        co2=420.0,
        timestamp_iso="2026-08-25T18:30:00.000000Z",
    )
    feats = vector.features
    assert feats["leaf_area"] is not None and feats["leaf_area"] > 100
    assert feats["green_pixel_ratio"] is not None
    assert 0.05 < feats["green_pixel_ratio"] < 0.8
    assert feats["mean_hue"] is not None and 20 < feats["mean_hue"] < 100
    assert feats["contour_area"] is not None and feats["contour_area"] > 50
    assert feats["bbox_w"] is not None and feats["bbox_w"] > 0
    assert feats["centroid_x"] is not None
    assert feats["soil_moisture"] == 41.2
    assert feats["temperature"] == 27.8


def test_features_stable_across_runs() -> None:
    img = _golden_plant()
    a = run_pipeline(img, width=160, height=120, blur_ksize=3).features
    b = run_pipeline(img, width=160, height=120, blur_ksize=3).features
    for key in ("leaf_area", "green_pixel_ratio", "mean_hue", "contour_area"):
        assert a[key] == pytest.approx(b[key], rel=0, abs=1e-9)


def test_message_round_trip_preserves_schema() -> None:
    vector = build_feature_vector(
        {"leaf_area": 10.0, "green_pixel_ratio": 0.1},
        soil_moisture=None,
        timestamp_iso="2026-08-25T18:30:00.000000Z",
    )
    parsed = FeatureVector.from_message_data(vector.to_message_data())
    assert parsed.schema_version == SCHEMA_VERSION
    payload = json.loads(vector.to_message_data())
    assert set(payload["features"].keys()) == set(ALL_FEATURE_KEYS)
    assert parsed.features["leaf_area"] == 10.0
    assert parsed.features["soil_moisture"] is None
