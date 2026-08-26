"""End-to-end classical baseline evaluation with leakage gate (PHP-12)."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Sequence

from plant_health_ml.baseline import build_baseline_pipeline
from plant_health_ml.leakage import LeakageReport, check_leakage
from plant_health_ml.metrics import compute_classification_metrics
from plant_health_ml.preprocess import FEATURE_KEYS, LABELS, records_to_matrix
from plant_health_ml.splits import plant_group_split


@dataclass(frozen=True)
class EvaluationResult:
    passed_gate: bool
    report_path: Path
    metrics: dict[str, Any]
    leakage: LeakageReport
    n_train: int
    n_test: int


def evaluate_baseline(
    records: Sequence[dict[str, Any]],
    *,
    report_dir: Path,
    test_size: float = 0.25,
    seed: int = 42,
    report_name: str | None = None,
) -> EvaluationResult:
    """
    Plant-group split → leakage gate → train on train → metrics on test → JSON report.

    If leakage is detected, metrics are still computed only when the gate is
    bypassed by the caller; by default we still fit for diagnostics but mark
    ``passed_gate=False`` so CI / CLI can fail.
    """
    if not records:
        raise ValueError("records must be non-empty")

    train, test = plant_group_split(records, test_size=test_size, seed=seed)
    leakage = check_leakage(train, test, feature_keys=FEATURE_KEYS)

    x_train, y_train, keys = records_to_matrix(train)
    x_test, y_test, _ = records_to_matrix(test, feature_keys=keys)
    pipeline = build_baseline_pipeline(random_state=seed)
    pipeline.fit(x_train, y_train)
    y_pred = pipeline.predict(x_test)
    metrics = compute_classification_metrics(y_test, y_pred, labels=LABELS)

    report_dir = Path(report_dir)
    report_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    name = report_name or f"baseline_eval_{stamp}.json"
    report_path = report_dir / name

    report = {
        "generated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        "split": {
            "strategy": "plant_group",
            "test_size": test_size,
            "seed": seed,
            "n_train": len(train),
            "n_test": len(test),
            "train_plants": sorted(
                {str(r["plant_id"]) for r in train if r.get("plant_id") is not None}
            ),
            "test_plants": sorted(
                {str(r["plant_id"]) for r in test if r.get("plant_id") is not None}
            ),
        },
        "leakage": leakage.to_dict(),
        "passed_gate": leakage.ok,
        "metrics": metrics,
        "feature_keys": keys,
        "labels": list(LABELS),
        "algorithm": "StandardScaler+RandomForestClassifier",
    }
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    return EvaluationResult(
        passed_gate=leakage.ok,
        report_path=report_path,
        metrics=metrics,
        leakage=leakage,
        n_train=len(train),
        n_test=len(test),
    )
