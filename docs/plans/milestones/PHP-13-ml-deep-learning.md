# PHP-13 — Deep Learning Classifier

## Goal

Introduce a Stage-4 feature MLP with ONNX export and registry entry, justified by ADR-0002 — without replacing the classical RandomForest baseline.

## Prerequisites

- PHP-11 classical baseline; PHP-12 evaluation / leakage gate
- [ADR-0002](../../architecture/adr/0002-classical-before-feature-mlp-onnx.md)

## Acceptance Criteria

- [x] ADR justifying DL vs classical (Accepted)
- [x] Train compact PyTorch `FeatureMLP` on schema v1.0 features
- [x] Evaluate and **compare metrics to classical baseline** on the same plant-group split
- [x] Export versioned ONNX; smoke-load with ONNX Runtime
- [x] Version registry entry in `ml/models/registry.json`
- [x] Image CNN deferred until real labeled images justify complexity

## Train

```bash
export PYTHONPATH=ml
python ml/training/train_dl.py --version 1.0.0
# → ml/models/plant-health-mlp-1.0.0.pt
# → ml/models/plant-health-mlp-1.0.0.onnx
# → ml/models/plant-health-mlp-1.0.0.meta.json
# → ml/models/registry.json
```

## Architecture Impact

Offline only. PHP-14 may load `.onnx` for edge inference; ML still never drives GPIO.
