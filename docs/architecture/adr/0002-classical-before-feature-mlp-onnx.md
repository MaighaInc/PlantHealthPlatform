# ADR 0002 — Classical ML Baseline Before Feature MLP + ONNX

**Status:** Accepted  
**Date:** 2026-08-25  
**Supersedes:** —

## Context

PlantHealthPlatform follows a staged ML progression (rules → classical CV → classical ML → deep learning). PHP-11 delivered a RandomForest baseline on schema v1.0 feature vectors; PHP-12 added plant-group evaluation and leakage gates. PHP-13 asks for a deep-learning classifier with ONNX export for edge inference (PHP-14).

Labeled **image** volume is still synthetic/fixture-scale. Jumping to a CNN would add GPU, data, and ops cost without evidence that classical models fail on the current feature schema.

## Decision

1. **Keep RandomForest as the primary classical baseline** for tabular feature vectors (Stage 3).
2. **Introduce a compact PyTorch MLP** on the same feature schema as a Stage-4 teaching and edge-export path — not because RF failed on synthetic data.
3. **Export ONNX** (`plant-health-mlp-<version>.onnx`) as the preferred edge artifact; register both classical and DL entries in `ml/models/registry.json`.
4. **Defer image CNNs** until a real labeled image dataset exists and classical/MLP metrics plateau on production-like data.
5. Every DL evaluation **must compare metrics to the classical baseline** on the same plant-group split.

## Alternatives Considered

| Option | Notes |
|--------|-------|
| Skip DL entirely until production images | Blocks ONNX/edge inference milestone learning |
| Jump to CNN on raw images now | Unjustified complexity; weak labels; heavier deps |
| Replace RF with MLP as sole model | Loses a simple, auditable baseline |
| TensorFlow / TFLite only | PyTorch + ONNX Runtime matches stack docs and edge path |

## Tradeoffs

**Pros:** Preserves Stage-3 baseline; adds reproducible ONNX path for PHP-14; forces explicit metric comparison; keeps CPU-friendly training.  
**Cons:** MLP on engineered features rarely beats RF on tiny synthetic sets; two model families to maintain; Windows hosts may lack the full `onnx` package (export via Torch, load via ONNX Runtime).

## Consequences

- PHP-13 trains/evaluates/exports the MLP and updates the model registry.
- PHP-14 may load either `.joblib` (classical) or `.onnx` (MLP) under SIMULATION.
- Production promotion of DL still requires beating or matching classical metrics on real data plus leakage-clean splits.
- ADR must be revisited before adopting CNN/segmentation networks.

## References

- [ML_PIPELINE.md](../../design/ML_PIPELINE.md)
- [../plans/IMPLEMENTATION_PLAN.md](../../plans/IMPLEMENTATION_PLAN.md) — PHP-11…PHP-14
- [MASTER_PROMPT.md](../../prompt/MASTER_PROMPT.md) — complexity progression
