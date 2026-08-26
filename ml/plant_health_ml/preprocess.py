"""Feature matrix preprocessing for classical ML (PHP-11)."""

from __future__ import annotations

from typing import Any, Sequence

import numpy as np

# Keep aligned with docs/design/FEATURE_SCHEMA.md (schema v1.0)
FEATURE_KEYS: tuple[str, ...] = (
    "leaf_area",
    "green_pixel_ratio",
    "mean_hue",
    "mean_saturation",
    "mean_value",
    "contour_area",
    "bbox_x",
    "bbox_y",
    "bbox_w",
    "bbox_h",
    "centroid_x",
    "centroid_y",
    "soil_moisture",
    "temperature",
    "humidity",
    "light",
    "co2",
)

LABELS: tuple[str, ...] = ("healthy", "stressed", "unknown")


def records_to_matrix(
    records: Sequence[dict[str, Any]],
    *,
    feature_keys: Sequence[str] | None = None,
    fill_value: float = 0.0,
) -> tuple[np.ndarray, np.ndarray, list[str]]:
    """
    Convert list of {features: {...}, label: str} or flat feature dicts to X, y.

    Missing feature values become ``fill_value`` (documented imputation for baseline).
    """
    keys = list(feature_keys or FEATURE_KEYS)
    rows: list[list[float]] = []
    labels: list[str] = []
    for rec in records:
        if "label" not in rec or rec["label"] is None:
            raise ValueError("each training record requires a label")
        label = str(rec["label"]).strip().lower()
        if label not in LABELS:
            raise ValueError(f"label must be one of {LABELS}, got {label!r}")
        feats = rec.get("features") if isinstance(rec.get("features"), dict) else rec
        row: list[float] = []
        for key in keys:
            raw = feats.get(key) if isinstance(feats, dict) else None
            if raw is None:
                row.append(fill_value)
            else:
                row.append(float(raw))
        rows.append(row)
        labels.append(label)
    x = np.asarray(rows, dtype=np.float64)
    y = np.asarray(labels, dtype=object)
    return x, y, keys
