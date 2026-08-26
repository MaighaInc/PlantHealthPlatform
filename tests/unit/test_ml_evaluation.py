"""Unit tests for ML evaluation pipeline (PHP-12)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_ML = Path(__file__).resolve().parents[2] / "ml"
sys.path.insert(0, str(_ML))

from plant_health_ml.evaluate import evaluate_baseline  # noqa: E402
from plant_health_ml.leakage import check_leakage  # noqa: E402
from plant_health_ml.metrics import compute_classification_metrics  # noqa: E402
from plant_health_ml.splits import plant_group_split  # noqa: E402
from plant_health_ml.synthetic import make_synthetic_records  # noqa: E402


def test_plant_group_split_no_overlap() -> None:
    records = make_synthetic_records(n_per_class=12, seed=3, unique_plants=True)
    train, test = plant_group_split(records, test_size=0.25, seed=3)
    train_ids = {r["plant_id"] for r in train}
    test_ids = {r["plant_id"] for r in test}
    assert train_ids.isdisjoint(test_ids)
    assert train and test


def test_leakage_detector_catches_duplicate_plant_split() -> None:
    """Acceptance: intentional plant overlap fails the gate."""
    records = make_synthetic_records(n_per_class=8, seed=1, unique_plants=True)
    train, test = plant_group_split(records, test_size=0.25, seed=1)
    # Poison: put one train plant into the test set
    poisoned_test = list(test) + [dict(train[0])]
    report = check_leakage(train, poisoned_test)
    assert report.ok is False
    assert any(f.kind == "plant_id_overlap" for f in report.findings)


def test_leakage_detector_catches_duplicate_features() -> None:
    records = make_synthetic_records(n_per_class=6, seed=2, unique_plants=True)
    train, test = plant_group_split(records, test_size=0.3, seed=2)
    clone = dict(train[0])
    clone["plant_id"] = "totally_new_plant"
    report = check_leakage(train, list(test) + [clone])
    assert report.ok is False
    assert any(f.kind == "duplicate_features" for f in report.findings)


def test_metrics_shape() -> None:
    y_true = ["healthy", "stressed", "unknown", "healthy"]
    y_pred = ["healthy", "stressed", "stressed", "healthy"]
    m = compute_classification_metrics(y_true, y_pred)
    assert 0.0 <= m["accuracy"] <= 1.0
    assert m["confusion_matrix"] and len(m["confusion_matrix"]) == 3
    assert m["n_samples"] == 4


def test_evaluate_writes_report_and_passes_gate(tmp_path: Path) -> None:
    records = make_synthetic_records(n_per_class=20, seed=5, unique_plants=True)
    result = evaluate_baseline(
        records,
        report_dir=tmp_path,
        test_size=0.25,
        seed=5,
        report_name="eval.json",
    )
    assert result.passed_gate is True
    assert result.report_path.is_file()
    report = json.loads(result.report_path.read_text(encoding="utf-8"))
    assert report["passed_gate"] is True
    assert report["leakage"]["ok"] is True
    assert "accuracy" in report["metrics"]
    assert "f1_macro" in report["metrics"]
    assert report["metrics"]["accuracy"] >= 0.7
