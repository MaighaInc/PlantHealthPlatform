"""Unit tests for classical ML baseline (PHP-11)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_ML = Path(__file__).resolve().parents[2] / "ml"
sys.path.insert(0, str(_ML))

from plant_health_ml.baseline import (  # noqa: E402
    MODEL_NAME,
    load_baseline,
    predict_label,
    train_baseline,
)
from plant_health_ml.preprocess import FEATURE_KEYS, records_to_matrix  # noqa: E402
from plant_health_ml.synthetic import make_synthetic_records  # noqa: E402


def test_preprocess_rejects_bad_label() -> None:
    with pytest.raises(ValueError, match="label"):
        records_to_matrix([{"features": {k: 1.0 for k in FEATURE_KEYS}, "label": "dead"}])


def test_preprocess_fills_missing_features() -> None:
    rec = {"features": {"leaf_area": 10.0}, "label": "healthy"}
    x, y, keys = records_to_matrix([rec], fill_value=-1.0)
    assert y[0] == "healthy"
    assert x.shape == (1, len(keys))
    assert x[0, keys.index("leaf_area")] == 10.0
    assert x[0, keys.index("soil_moisture")] == -1.0


def test_smoke_train_writes_versioned_artifact(tmp_path: Path) -> None:
    records = make_synthetic_records(n_per_class=20, seed=7)
    trained = train_baseline(
        records, model_dir=tmp_path, model_version="1.0.0", random_state=7
    )
    assert trained.model_path.name == f"{MODEL_NAME}-1.0.0.joblib"
    assert trained.metadata_path.is_file()
    meta = json.loads(trained.metadata_path.read_text(encoding="utf-8"))
    assert meta["model_name"] == MODEL_NAME
    assert meta["model_version"] == "1.0.0"
    assert meta["n_samples"] == len(records)
    assert trained.train_accuracy >= 0.8

    payload = load_baseline(trained.model_path)
    healthy_feats = records[0]["features"]
    label = predict_label(payload, healthy_feats)
    assert label in {"healthy", "stressed", "unknown"}


def test_training_reproducible_with_seed(tmp_path: Path) -> None:
    records = make_synthetic_records(n_per_class=15, seed=1)
    a = train_baseline(records, model_dir=tmp_path / "a", model_version="1.0.0", random_state=1)
    b = train_baseline(records, model_dir=tmp_path / "b", model_version="1.0.0", random_state=1)
    assert a.train_accuracy == pytest.approx(b.train_accuracy)
