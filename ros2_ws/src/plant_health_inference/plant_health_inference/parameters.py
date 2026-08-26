"""Validated parameters for the inference node."""

from __future__ import annotations

from dataclasses import dataclass


class InferenceParameterError(ValueError):
    """Invalid ROS parameter for inference node."""


@dataclass(frozen=True)
class InferenceNodeParams:
    features_topic: str
    prediction_topic: str
    backend: str
    model_path: str
    confidence_threshold: float
    mock_label: str
    mock_confidence: float

    @classmethod
    def from_raw(
        cls,
        *,
        features_topic: str,
        prediction_topic: str,
        backend: str,
        model_path: str,
        confidence_threshold: float,
        mock_label: str,
        mock_confidence: float,
    ) -> InferenceNodeParams:
        if not features_topic.startswith("/"):
            raise InferenceParameterError("features_topic must be absolute")
        if not prediction_topic.startswith("/"):
            raise InferenceParameterError("prediction_topic must be absolute")
        backend_n = backend.strip().lower()
        if backend_n not in {"mock", "joblib"}:
            raise InferenceParameterError("backend must be mock or joblib")
        if not 0.0 <= float(confidence_threshold) <= 1.0:
            raise InferenceParameterError("confidence_threshold must be in [0, 1]")
        if not 0.0 <= float(mock_confidence) <= 1.0:
            raise InferenceParameterError("mock_confidence must be in [0, 1]")
        label = mock_label.strip().lower()
        if label not in {"healthy", "stressed", "unknown"}:
            raise InferenceParameterError("mock_label invalid")
        return cls(
            features_topic=features_topic,
            prediction_topic=prediction_topic,
            backend=backend_n,
            model_path=str(model_path),
            confidence_threshold=float(confidence_threshold),
            mock_label=label,
            mock_confidence=float(mock_confidence),
        )
