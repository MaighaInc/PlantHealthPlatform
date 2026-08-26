# Machine Learning Pipeline

> ML lifecycle, versioning, evaluation, and inference architecture

## Complexity Progression

| Stage | Approach |
|-------|----------|
| 1 | Rule-based logic |
| 2 | Classical computer vision |
| 3 | Classical ML (Logistic Regression, Decision Trees, Random Forest, SVM, Gradient Boosting) |
| 4 | Deep learning (PyTorch, TensorFlow, ONNX, ONNX Runtime) |

Do not jump directly to deep learning. The intern must justify increased complexity.

## Dataset Structure

```text
dataset/
├── images/
├── labels/
├── metadata/
└── manifests/
```

Each record should support:

```text
image, timestamp, plant_id, sensor readings, camera metadata, environment, health label
```

Example:

```json
{
  "image": "images/plant_001_000123.jpg",
  "plant_id": "plant-001",
  "timestamp": "2026-08-25T18:30:00Z",
  "soil_moisture": 41.2,
  "temperature": 27.8,
  "humidity": 63.4,
  "light": 812,
  "label": "healthy"
}
```

## Data Quality Checks

Validate before training:

- Missing data, corrupted/blurry/over/under-exposed images
- Duplicate images, incorrect labels
- Sensor anomalies, timestamp mismatches

Invalid data must not silently enter the training pipeline.

## Leakage Prevention

Explicitly check:

- Duplicate images
- Same plant in train and test
- Temporal leakage
- Preprocessing leakage
- Label leakage
- Train/test contamination

## Model Versioning

Every inference must identify the model:

```json
{
  "model_name": "plant-health-classifier",
  "model_version": "1.2.0",
  "prediction": "stressed",
  "confidence": 0.91,
  "timestamp": "..."
}
```

Never use ambiguous filenames like `final_final_v2_really_final.pt`.

### Classical baseline (PHP-11)

- Train: `python ml/training/train_baseline.py --version 1.0.0`
- Artifacts: `ml/models/plant-health-classifier-<version>.joblib` + `.meta.json`
- Algorithm: `StandardScaler` + `RandomForestClassifier`
- Labels: `healthy` | `stressed` | `unknown`
- Features: schema v1.0 keys from [FEATURE_SCHEMA.md](./FEATURE_SCHEMA.md)

### Feature MLP + ONNX (PHP-13 / ADR-0002)

- Justification: [ADR-0002](../architecture/adr/0002-classical-before-feature-mlp-onnx.md) — RF stays preferred tabular baseline; MLP adds edge ONNX path
- Train: `python ml/training/train_dl.py --version 1.0.0`
- Artifacts: `plant-health-mlp-<version>.pt` + `.onnx` + `.meta.json`
- Registry: `ml/models/registry.json`
- Image CNNs deferred until real labeled images exist

## UNKNOWN State

If `confidence < threshold` → prediction = `UNKNOWN`.

Do not force a diagnosis when evidence is insufficient.

## Inference Node Responsibilities

1. Subscribe to feature vectors (`/plant/features`) — image subscribe optional later
2. Validate and preprocess
3. Run inference (mock / joblib; ONNX optional later)
4. Produce prediction + confidence
5. Record model version
6. Measure inference latency
7. Publish `/plant/disease_prediction`
8. Handle failures safely (`unknown` on low confidence)

Must **not** train models, manipulate GPIO, own DB schema, or control frontend.

### Online inference (PHP-14)

- Package: `plant_health_inference` / executable `inference_engine`
- SIMULATION default backend: `mock`
- Classical: `backend:=joblib` + `model_path` to `plant-health-classifier-*.joblib`
- Confidence gate: `confidence < threshold` → `unknown`

## Evaluation Metrics

Track: accuracy, precision, recall, F1, confusion matrix, inference latency, model size, CPU/memory.

When classes are imbalanced, accuracy alone is insufficient — use ROC-AUC / PR-AUC where appropriate.

### Evaluation pipeline (PHP-12)

- Split: **plant-group** (`plant_id` must not appear in both train and test)
- CLI: `python ml/evaluation/run_evaluation.py`
- Reports: `ml/evaluation/reports/*.json`
- Leakage gate fails on plant overlap or identical feature fingerprints across the split
- Metrics written: accuracy, macro precision/recall/F1, confusion matrix

## Related Docs

- [SYSTEM_BOUNDARIES.md](./SYSTEM_BOUNDARIES.md)
- [DATA_PIPELINE.md](./DATA_PIPELINE.md)
- [../plans/ROADMAP.md](../plans/ROADMAP.md) — PHP-11 through PHP-14
