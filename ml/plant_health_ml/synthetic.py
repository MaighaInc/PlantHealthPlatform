"""Synthetic labeled feature records for reproducible baseline smoke training."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

from plant_health_ml.preprocess import FEATURE_KEYS, LABELS


def make_synthetic_records(
    *,
    n_per_class: int = 40,
    seed: int = 42,
    unique_plants: bool = True,
) -> list[dict[str, Any]]:
    """
    Generate separable synthetic feature rows for healthy / stressed / unknown.

    Not a substitute for real plant data — used for CI and training smoke tests.
    When ``unique_plants`` is True (default), each row gets its own ``plant_id``
    so plant-group evaluation splits are valid.
    """
    rng = np.random.default_rng(seed)
    records: list[dict[str, Any]] = []

    def _base() -> dict[str, float]:
        return {k: 0.0 for k in FEATURE_KEYS}

    for i in range(n_per_class):
        healthy = _base()
        healthy.update(
            {
                "leaf_area": float(rng.uniform(800, 2000)),
                "green_pixel_ratio": float(rng.uniform(0.25, 0.55)),
                "mean_hue": float(rng.uniform(45, 75)),
                "mean_saturation": float(rng.uniform(80, 160)),
                "mean_value": float(rng.uniform(80, 180)),
                "contour_area": float(rng.uniform(700, 1800)),
                "bbox_w": float(rng.uniform(40, 120)),
                "bbox_h": float(rng.uniform(40, 120)),
                "centroid_x": float(rng.uniform(50, 150)),
                "centroid_y": float(rng.uniform(50, 150)),
                "soil_moisture": float(rng.uniform(40, 70)),
                "temperature": float(rng.uniform(18, 28)),
                "humidity": float(rng.uniform(40, 70)),
                "light": float(rng.uniform(400, 1200)),
                "co2": float(rng.uniform(380, 450)),
            }
        )
        pid_h = f"syn_h_{i}" if unique_plants else "syn_h"
        records.append({"features": healthy, "label": "healthy", "plant_id": pid_h})

        stressed = _base()
        stressed.update(
            {
                "leaf_area": float(rng.uniform(100, 600)),
                "green_pixel_ratio": float(rng.uniform(0.02, 0.15)),
                "mean_hue": float(rng.uniform(20, 40)),
                "mean_saturation": float(rng.uniform(40, 100)),
                "mean_value": float(rng.uniform(40, 120)),
                "contour_area": float(rng.uniform(80, 500)),
                "bbox_w": float(rng.uniform(10, 50)),
                "bbox_h": float(rng.uniform(10, 50)),
                "centroid_x": float(rng.uniform(50, 150)),
                "centroid_y": float(rng.uniform(50, 150)),
                "soil_moisture": float(rng.uniform(5, 25)),
                "temperature": float(rng.uniform(33, 42)),
                "humidity": float(rng.uniform(20, 45)),
                "light": float(rng.uniform(200, 800)),
                "co2": float(rng.uniform(400, 600)),
            }
        )
        pid_s = f"syn_s_{i}" if unique_plants else "syn_s"
        records.append({"features": stressed, "label": "stressed", "plant_id": pid_s})

        unknown = _base()
        # Near-zero / inconsistent features → unknown class cluster
        unknown.update(
            {
                "leaf_area": float(rng.uniform(0, 50)),
                "green_pixel_ratio": float(rng.uniform(0.0, 0.02)),
                "mean_hue": float(rng.uniform(0, 10)),
                "soil_moisture": float("nan") if False else float(rng.uniform(-1, 0)),
                "temperature": float(rng.uniform(-5, 0)),
            }
        )
        # Use fill later; store explicit weird but finite values for unknown
        unknown["soil_moisture"] = float(rng.uniform(0, 1))
        unknown["temperature"] = float(rng.uniform(0, 5))
        pid_u = f"syn_u_{i}" if unique_plants else "syn_u"
        records.append({"features": unknown, "label": "unknown", "plant_id": pid_u})

    assert set(LABELS) <= {r["label"] for r in records}
    return records


def write_synthetic_jsonl(path: Path, *, n_per_class: int = 40, seed: int = 42) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    records = make_synthetic_records(n_per_class=n_per_class, seed=seed)
    with path.open("w", encoding="utf-8") as handle:
        for rec in records:
            handle.write(json.dumps(rec, sort_keys=True) + "\n")
    return path


def load_jsonl_records(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records
