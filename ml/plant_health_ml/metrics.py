"""Classification metrics for plant-health evaluation (PHP-12)."""

from __future__ import annotations

from typing import Any, Sequence

import numpy as np
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)

from plant_health_ml.preprocess import LABELS


def compute_classification_metrics(
    y_true: Sequence[str],
    y_pred: Sequence[str],
    *,
    labels: Sequence[str] | None = None,
) -> dict[str, Any]:
    """Accuracy, macro precision/recall/F1, and confusion matrix."""
    label_list = list(labels or LABELS)
    yt = np.asarray(list(y_true), dtype=object)
    yp = np.asarray(list(y_pred), dtype=object)
    if yt.shape != yp.shape:
        raise ValueError("y_true and y_pred must have the same length")
    if len(yt) == 0:
        raise ValueError("y_true/y_pred must be non-empty")

    cm = confusion_matrix(yt, yp, labels=label_list)
    return {
        "accuracy": float(accuracy_score(yt, yp)),
        "precision_macro": float(
            precision_score(yt, yp, labels=label_list, average="macro", zero_division=0)
        ),
        "recall_macro": float(
            recall_score(yt, yp, labels=label_list, average="macro", zero_division=0)
        ),
        "f1_macro": float(
            f1_score(yt, yp, labels=label_list, average="macro", zero_division=0)
        ),
        "labels": label_list,
        "confusion_matrix": cm.tolist(),
        "n_samples": int(len(yt)),
    }
