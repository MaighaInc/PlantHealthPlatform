#!/usr/bin/env python3
"""CLI: train feature MLP, compare to classical baseline, export ONNX."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_ML = Path(__file__).resolve().parents[1]
if str(_ML) not in sys.path:
    sys.path.insert(0, str(_ML))

from plant_health_ml.dl_train import DEFAULT_VERSION, train_feature_mlp
from plant_health_ml.synthetic import load_jsonl_records, make_synthetic_records, write_synthetic_jsonl


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=None)
    parser.add_argument("--model-dir", type=Path, default=_ML / "models")
    parser.add_argument("--version", default=DEFAULT_VERSION)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--epochs", type=int, default=80)
    args = parser.parse_args()

    if args.data is None:
        fixture = _ML / "datasets" / "fixtures" / "eval_features.jsonl"
        if not fixture.is_file():
            write_synthetic_jsonl(fixture, n_per_class=40, seed=args.seed)
        records = load_jsonl_records(fixture)
        if len({r.get("plant_id") for r in records}) < 4:
            records = make_synthetic_records(n_per_class=40, seed=args.seed, unique_plants=True)
    else:
        records = load_jsonl_records(args.data)

    result = train_feature_mlp(
        records,
        model_dir=args.model_dir,
        model_version=args.version,
        seed=args.seed,
        epochs=args.epochs,
    )
    print(
        f"Trained {result.model_name} v{result.model_version} "
        f"mlp_acc={result.metrics['accuracy']:.3f} "
        f"rf_acc={result.baseline_metrics['accuracy']:.3f} "
        f"onnx={result.onnx_path}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
