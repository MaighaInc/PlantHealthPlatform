"""Pure inference engine — no ROS, no GPIO, no training (PHP-14)."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Protocol

from plant_health_inference.prediction import PredictionResult

VALID_LABELS = frozenset({"healthy", "stressed", "unknown"})


class InferenceBackend(Protocol):
    @property
    def model_name(self) -> str: ...

    @property
    def model_version(self) -> str: ...

    def predict(self, features: dict[str, float | None]) -> tuple[str, float]:
        """Return (label, confidence in [0, 1])."""
        ...


class MockBackend:
    """Deterministic SIMULATION backend (no model file required)."""

    def __init__(
        self,
        *,
        label: str = "healthy",
        confidence: float = 0.95,
        model_name: str = "mock-classifier",
        model_version: str = "0.0.0",
    ) -> None:
        if label not in VALID_LABELS:
            raise ValueError(f"label must be one of {sorted(VALID_LABELS)}")
        self._label = label
        self._confidence = float(confidence)
        self._model_name = model_name
        self._model_version = model_version

    @property
    def model_name(self) -> str:
        return self._model_name

    @property
    def model_version(self) -> str:
        return self._model_version

    def predict(self, features: dict[str, float | None]) -> tuple[str, float]:
        _ = features
        return self._label, self._confidence


class JoblibBackend:
    """Load classical PHP-11 joblib artifact."""

    def __init__(self, model_path: Path) -> None:
        import joblib

        path = Path(model_path)
        if not path.is_file():
            raise FileNotFoundError(path)
        payload = joblib.load(path)
        required = {"model_name", "model_version", "pipeline", "feature_keys"}
        missing = required - set(payload)
        if missing:
            raise ValueError(f"model artifact missing keys: {sorted(missing)}")
        self._payload = payload

    @property
    def model_name(self) -> str:
        return str(self._payload["model_name"])

    @property
    def model_version(self) -> str:
        return str(self._payload["model_version"])

    def predict(self, features: dict[str, float | None]) -> tuple[str, float]:
        import numpy as np

        keys = list(self._payload["feature_keys"])
        row = np.asarray(
            [[float(features[k]) if features.get(k) is not None else 0.0 for k in keys]],
            dtype=np.float64,
        )
        pipeline = self._payload["pipeline"]
        if hasattr(pipeline, "predict_proba"):
            proba = pipeline.predict_proba(row)[0]
            classes = list(pipeline.classes_)
            idx = int(np.argmax(proba))
            return str(classes[idx]), float(proba[idx])
        pred = pipeline.predict(row)[0]
        return str(pred), 1.0


def parse_features_message(raw: str) -> dict[str, float | None]:
    """Parse `/plant/features` JSON String into a feature dict."""
    data = json.loads(raw)
    if not isinstance(data, dict):
        raise ValueError("features message must be a JSON object")
    feats = data.get("features", data)
    if not isinstance(feats, dict):
        raise ValueError("features payload missing 'features' object")
    out: dict[str, float | None] = {}
    for key, value in feats.items():
        if value is None:
            out[str(key)] = None
        else:
            out[str(key)] = float(value)
    if not out:
        raise ValueError("features object is empty")
    return out


def apply_confidence_gate(
    label: str,
    confidence: float,
    *,
    threshold: float,
) -> tuple[str, str | None]:
    """Map low-confidence predictions to unknown."""
    if confidence < threshold:
        return "unknown", f"confidence {confidence:.4f} < threshold {threshold:.4f}"
    normalized = str(label).strip().lower()
    if normalized not in VALID_LABELS:
        return "unknown", f"invalid label {label!r}"
    return normalized, None


def run_inference(
    features: dict[str, float | None],
    backend: InferenceBackend,
    *,
    confidence_threshold: float = 0.55,
) -> PredictionResult:
    """Validate → infer → confidence gate → timed PredictionResult."""
    if not isinstance(features, dict) or not features:
        raise ValueError("features must be a non-empty dict")
    if not 0.0 <= confidence_threshold <= 1.0:
        raise ValueError("confidence_threshold must be in [0, 1]")

    t0 = time.perf_counter()
    label, confidence = backend.predict(features)
    latency_ms = (time.perf_counter() - t0) * 1000.0
    gated, reason = apply_confidence_gate(
        label, float(confidence), threshold=confidence_threshold
    )
    return PredictionResult(
        prediction=gated,
        confidence=float(confidence),
        model_name=backend.model_name,
        model_version=backend.model_version,
        latency_ms=latency_ms,
        unknown_reason=reason,
    )


def create_backend(
    mode: str,
    *,
    model_path: str | Path | None = None,
    mock_label: str = "healthy",
    mock_confidence: float = 0.95,
) -> InferenceBackend:
    mode_n = mode.strip().lower()
    if mode_n == "mock":
        return MockBackend(label=mock_label, confidence=mock_confidence)
    if mode_n == "joblib":
        if model_path is None:
            raise ValueError("joblib backend requires model_path")
        return JoblibBackend(Path(model_path))
    raise ValueError(f"unsupported backend mode: {mode!r} (use mock|joblib)")
