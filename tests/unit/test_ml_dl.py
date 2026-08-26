"""Unit tests for DL feature MLP + ONNX export (PHP-13)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_ML = Path(__file__).resolve().parents[2] / "ml"
sys.path.insert(0, str(_ML))

from plant_health_ml.dl_train import (  # noqa: E402
    MODEL_NAME,
    load_onnx_session,
    onnx_predict_labels,
    train_feature_mlp,
)
from plant_health_ml.preprocess import records_to_matrix  # noqa: E402
from plant_health_ml.registry import load_registry  # noqa: E402
from plant_health_ml.splits import plant_group_split  # noqa: E402
from plant_health_ml.synthetic import make_synthetic_records  # noqa: E402


def test_train_exports_onnx_and_compares_to_baseline(tmp_path: Path) -> None:
    pytest.importorskip("onnx")  # Windows store Python often lacks onnx (path-length); use .venv
    records = make_synthetic_records(n_per_class=24, seed=9, unique_plants=True)
    trained = train_feature_mlp(
        records,
        model_dir=tmp_path,
        model_version="1.0.0",
        seed=9,
        epochs=60,
    )
    assert trained.torch_path.is_file()
    assert trained.onnx_path.is_file()
    assert trained.onnx_path.name == f"{MODEL_NAME}-1.0.0.onnx"
    meta = json.loads(trained.metadata_path.read_text(encoding="utf-8"))
    assert "baseline_metrics" in meta
    assert "comparison" in meta
    assert meta["metrics"]["accuracy"] >= 0.5
    assert meta["baseline_metrics"]["accuracy"] >= 0.5

    registry = load_registry(tmp_path)
    formats = {(m["model_name"], m["format"]) for m in registry["models"]}
    assert (MODEL_NAME, "onnx") in formats
    assert ("plant-health-classifier", "joblib") in formats

    session = load_onnx_session(trained.onnx_path)
    _, test_records = plant_group_split(records, test_size=0.25, seed=9)
    x, _, _ = records_to_matrix(test_records)
    labels = onnx_predict_labels(
        session, x[:3], mean=meta["mean"], std=meta["std"]
    )
    assert len(labels) == 3
    assert all(lab in {"healthy", "stressed", "unknown"} for lab in labels)


def test_onnx_smoke_rejects_missing(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        load_onnx_session(tmp_path / "missing.onnx")
