# PHP-12 — ML Evaluation Pipeline

## Goal

Evaluate the classical baseline with a plant-group split, publish metrics, and fail known leakage cases.

## Prerequisites

- PHP-11 classical baseline trainer

## Acceptance Criteria

- [x] Plant-group train/test split (`plant_id` disjoint)
- [x] Metrics: accuracy, macro precision/recall/F1, confusion matrix
- [x] Leakage checks: plant overlap + duplicate feature fingerprints
- [x] JSON reports under `ml/evaluation/reports/`
- [x] Unit test: intentional duplicate-plant split fails the gate
- [x] CLI exits non-zero when leakage is detected

## Run

```bash
export PYTHONPATH=ml
python ml/evaluation/run_evaluation.py
# → ml/evaluation/reports/latest_baseline_eval.json
```

## Architecture Impact

Offline evaluation only — no ROS nodes, no GPIO, no inference publish path.
