#!/usr/bin/env python3
"""CLI: plant-group evaluate classical baseline; fail if leakage gate trips."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_ML = Path(__file__).resolve().parents[1]
if str(_ML) not in sys.path:
    sys.path.insert(0, str(_ML))

from plant_health_ml.evaluate import evaluate_baseline
from plant_health_ml.synthetic import load_jsonl_records, make_synthetic_records, write_synthetic_jsonl


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--data",
        type=Path,
        default=None,
        help="JSONL feature records (default: synthetic unique-plant fixture)",
    )
    parser.add_argument(
        "--report-dir",
        type=Path,
        default=_ML / "evaluation" / "reports",
        help="Directory for evaluation JSON reports",
    )
    parser.add_argument("--test-size", type=float, default=0.25)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--report-name",
        type=str,
        default="latest_baseline_eval.json",
        help="Report filename inside report-dir",
    )
    parser.add_argument(
        "--n-per-class",
        type=int,
        default=40,
        help="Synthetic size when --data is omitted",
    )
    args = parser.parse_args(argv)

    if args.data is None:
        fixture = _ML / "datasets" / "fixtures" / "eval_features.jsonl"
        if not fixture.is_file():
            write_synthetic_jsonl(fixture, n_per_class=args.n_per_class, seed=args.seed)
        records = load_jsonl_records(fixture)
        # Ensure plant-group splits work even if an old shared-id fixture exists
        if len({r.get("plant_id") for r in records}) < 4:
            records = make_synthetic_records(
                n_per_class=args.n_per_class, seed=args.seed, unique_plants=True
            )
    else:
        records = load_jsonl_records(args.data)

    result = evaluate_baseline(
        records,
        report_dir=args.report_dir,
        test_size=args.test_size,
        seed=args.seed,
        report_name=args.report_name,
    )
    print(
        f"report={result.report_path} "
        f"gate={'PASS' if result.passed_gate else 'FAIL'} "
        f"acc={result.metrics['accuracy']:.3f} "
        f"f1={result.metrics['f1_macro']:.3f} "
        f"n_train={result.n_train} n_test={result.n_test}"
    )
    if not result.passed_gate:
        for finding in result.leakage.findings:
            print(f"LEAKAGE [{finding.kind}]: {finding.detail}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
