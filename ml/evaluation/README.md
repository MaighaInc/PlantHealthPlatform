# ML Evaluation (PHP-12)

Plant-group train/test split, classification metrics, and leakage gates.

## Run

```bash
export PYTHONPATH=ml
python ml/evaluation/run_evaluation.py
# → ml/evaluation/reports/latest_baseline_eval.json
# exit 0 if leakage gate passes; exit 2 if leakage detected
```

## Leakage gate

Fails when:

- Same `plant_id` appears in both train and test
- Identical feature fingerprints appear across the split

## Reports

JSON reports under `reports/` include split membership, leakage findings, accuracy,
macro precision/recall/F1, and confusion matrix.
