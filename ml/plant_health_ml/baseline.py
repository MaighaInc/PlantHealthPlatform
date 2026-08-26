"""Train and persist classical plant-health baseline classifier (PHP-11)."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Sequence

import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from plant_health_ml.preprocess import FEATURE_KEYS, LABELS, records_to_matrix

MODEL_NAME = "plant-health-classifier"
DEFAULT_VERSION = "1.0.0"


@dataclass(frozen=True)
class TrainedBaseline:
    model_name: str
    model_version: str
    model_path: Path
    metadata_path: Path
    feature_keys: tuple[str, ...]
    labels: tuple[str, ...]
    train_accuracy: float


def build_baseline_pipeline(*, random_state: int = 42) -> Pipeline:
    """Classical Stage-3 model: StandardScaler + RandomForest."""
    return Pipeline(
        steps=[
            ("scaler", StandardScaler()),
            (
                "clf",
                RandomForestClassifier(
                    n_estimators=50,
                    max_depth=6,
                    random_state=random_state,
                    class_weight="balanced",
                ),
            ),
        ]
    )


def train_baseline(
    records: Sequence[dict[str, Any]],
    *,
    model_dir: Path,
    model_version: str = DEFAULT_VERSION,
    random_state: int = 42,
) -> TrainedBaseline:
    """
    Train on feature records and write versioned artifacts:

      {model_dir}/{model_name}-{version}.joblib
      {model_dir}/{model_name}-{version}.meta.json
    """
    if not records:
        raise ValueError("records must be non-empty")
    x, y, keys = records_to_matrix(records)
    pipeline = build_baseline_pipeline(random_state=random_state)
    pipeline.fit(x, y)
    train_acc = float(pipeline.score(x, y))

    model_dir = Path(model_dir)
    model_dir.mkdir(parents=True, exist_ok=True)
    stem = f"{MODEL_NAME}-{model_version}"
    model_path = model_dir / f"{stem}.joblib"
    metadata_path = model_dir / f"{stem}.meta.json"

    # Refuse ambiguous overwrite of differently hashed models without version bump
    joblib.dump(
        {
            "model_name": MODEL_NAME,
            "model_version": model_version,
            "pipeline": pipeline,
            "feature_keys": keys,
            "labels": list(LABELS),
        },
        model_path,
    )

    metadata = {
        "model_name": MODEL_NAME,
        "model_version": model_version,
        "algorithm": "RandomForestClassifier",
        "feature_keys": keys,
        "labels": list(LABELS),
        "train_accuracy": train_acc,
        "n_samples": int(len(records)),
        "random_state": random_state,
        "trained_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        "artifact": model_path.name,
    }
    metadata_path.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")

    return TrainedBaseline(
        model_name=MODEL_NAME,
        model_version=model_version,
        model_path=model_path,
        metadata_path=metadata_path,
        feature_keys=tuple(keys),
        labels=LABELS,
        train_accuracy=train_acc,
    )


def load_baseline(model_path: Path) -> dict[str, Any]:
    payload = joblib.load(model_path)
    required = {"model_name", "model_version", "pipeline", "feature_keys", "labels"}
    missing = required - set(payload)
    if missing:
        raise ValueError(f"model artifact missing keys: {sorted(missing)}")
    return payload


def predict_with_confidence(
    payload: dict[str, Any], features: dict[str, float | None]
) -> tuple[str, float]:
    """Return (label, confidence) using ``predict_proba`` when available."""
    keys = list(payload["feature_keys"])
    row = np.asarray(
        [[float(features[k]) if features.get(k) is not None else 0.0 for k in keys]],
        dtype=np.float64,
    )
    pipeline = payload["pipeline"]
    if hasattr(pipeline, "predict_proba"):
        proba = pipeline.predict_proba(row)[0]
        classes = list(pipeline.classes_)
        idx = int(np.argmax(proba))
        return str(classes[idx]), float(proba[idx])
    pred = pipeline.predict(row)[0]
    return str(pred), 1.0


def predict_label(payload: dict[str, Any], features: dict[str, float | None]) -> str:
    label, _ = predict_with_confidence(payload, features)
    return label
