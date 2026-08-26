"""Unit tests for inference engine (PHP-14) — no rclpy required."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[2]
_INF = _ROOT / "ros2_ws" / "src" / "plant_health_inference"
_ML = _ROOT / "ml"
sys.path.insert(0, str(_INF))
sys.path.insert(0, str(_ML))

from plant_health_inference.engine import (  # noqa: E402
    JoblibBackend,
    MockBackend,
    apply_confidence_gate,
    parse_features_message,
    run_inference,
)
from plant_health_inference.parameters import (  # noqa: E402
    InferenceNodeParams,
    InferenceParameterError,
)


def test_parse_features_message() -> None:
    raw = json.dumps(
        {
            "schema_version": "1.0",
            "features": {"leaf_area": 10.0, "soil_moisture": None},
        }
    )
    feats = parse_features_message(raw)
    assert feats["leaf_area"] == 10.0
    assert feats["soil_moisture"] is None


def test_confidence_gate_forces_unknown() -> None:
    label, reason = apply_confidence_gate("healthy", 0.4, threshold=0.55)
    assert label == "unknown"
    assert reason is not None


def test_mock_inference_scenario4_path() -> None:
    """Capstone Scenario 4 (SIMULATION): features → prediction with version + latency."""
    backend = MockBackend(label="stressed", confidence=0.91)
    result = run_inference(
        {"leaf_area": 100.0, "green_pixel_ratio": 0.05, "soil_moisture": 12.0},
        backend,
        confidence_threshold=0.55,
    )
    assert result.prediction == "stressed"
    assert result.confidence == pytest.approx(0.91)
    assert result.model_name == "mock-classifier"
    assert result.model_version == "0.0.0"
    assert result.latency_ms >= 0.0
    payload = json.loads(result.to_message_data())
    assert payload["prediction"] == "stressed"
    assert "latency_ms" in payload
    assert "model_version" in payload


def test_low_confidence_becomes_unknown() -> None:
    backend = MockBackend(label="healthy", confidence=0.2)
    result = run_inference({"leaf_area": 1.0}, backend, confidence_threshold=0.55)
    assert result.prediction == "unknown"
    assert result.unknown_reason is not None


def test_joblib_backend_smoke() -> None:
    model = _ROOT / "ml" / "models" / "plant-health-classifier-1.0.0.joblib"
    if not model.is_file():
        pytest.skip("classical model artifact not present")
    backend = JoblibBackend(model)
    result = run_inference(
        {
            "leaf_area": 1200.0,
            "green_pixel_ratio": 0.4,
            "mean_hue": 60.0,
            "mean_saturation": 100.0,
            "mean_value": 120.0,
            "contour_area": 1000.0,
            "bbox_x": 0.0,
            "bbox_y": 0.0,
            "bbox_w": 80.0,
            "bbox_h": 80.0,
            "centroid_x": 40.0,
            "centroid_y": 40.0,
            "soil_moisture": 50.0,
            "temperature": 22.0,
            "humidity": 55.0,
            "light": 800.0,
            "co2": 400.0,
        },
        backend,
        confidence_threshold=0.3,
    )
    assert result.prediction in {"healthy", "stressed", "unknown"}
    assert result.model_name == "plant-health-classifier"
    assert result.model_version == "1.0.0"


def test_params_reject_bad_backend() -> None:
    with pytest.raises(InferenceParameterError):
        InferenceNodeParams.from_raw(
            features_topic="/plant/features",
            prediction_topic="/plant/disease_prediction",
            backend="train",
            model_path="",
            confidence_threshold=0.5,
            mock_label="healthy",
            mock_confidence=0.9,
        )
