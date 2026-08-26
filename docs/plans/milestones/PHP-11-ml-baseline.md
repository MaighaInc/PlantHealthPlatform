# PHP-11 — Classical ML Baseline

## Goal

Train a versioned classical classifier (`healthy` / `stressed` / `unknown`) offline from feature vectors — no GPIO, no deep learning yet.

## Prerequisites

- PHP-10 feature schema; PHP-07 dataset layout concepts

## Acceptance Criteria

- [x] Labels: healthy / stressed / unknown
- [x] Training under `ml/training/train_baseline.py`
- [x] Artifact `{model_name}-{version}.joblib` + `.meta.json` under `ml/models/`
- [x] Preprocess + smoke-train unit tests
- [x] Reproducible with fixed `random_state` / synthetic JSONL

## Train

```bash
export PYTHONPATH=ml
python ml/training/train_baseline.py --version 1.0.0
# writes ml/models/plant-health-classifier-1.0.0.joblib (+ meta.json)
```

## Algorithm

`StandardScaler` + `RandomForestClassifier` (scikit-learn) — Stage 3 classical ML before any CNN.
