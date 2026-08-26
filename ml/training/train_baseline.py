#!/usr/bin/env python3
"""CLI: train classical baseline from JSONL feature records."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_ML = Path(__file__).resolve().parents[1]
if str(_ML) not in sys.path:
    sys.path.insert(0, str(_ML))

from plant_health_ml.baseline import DEFAULT_VERSION, train_baseline  # noqa: E402
from plant_health_ml.synthetic import (  # noqa: E402
    load_jsonl_records,
    write_synthetic_jsonl,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Train plant-health classical baseline")
    parser.add_argument(
        "--data",
        type=Path,
        default=None,
        help="JSONL feature records (default: generate synthetic fixture)",
    )
    parser.add_argument(
        "--model-dir",
        type=Path,
        default=_ML / "models",
        help="Output directory for versioned joblib + meta.json",
    )
    parser.add_argument("--version", default=DEFAULT_VERSION)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    if args.data is None:
        fixture = _ML / "datasets" / "fixtures" / "baseline_features.jsonl"
        write_synthetic_jsonl(fixture, n_per_class=40, seed=args.seed)
        data_path = fixture
    else:
        data_path = args.data

    records = load_jsonl_records(data_path)
    result = train_baseline(
        records,
        model_dir=args.model_dir,
        model_version=args.version,
        random_state=args.seed,
    )
    print(
        f"Trained {result.model_name} v{result.model_version} "
        f"acc={result.train_accuracy:.3f} -> {result.model_path}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
