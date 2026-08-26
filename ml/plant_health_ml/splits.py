"""Train/test split strategies for plant-health evaluation (PHP-12)."""

from __future__ import annotations

from typing import Any, Sequence

import numpy as np


def plant_group_split(
    records: Sequence[dict[str, Any]],
    *,
    test_size: float = 0.25,
    seed: int = 42,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """
    Split by ``plant_id`` so the same plant never appears in both sets.

    Falls back to index-based split only when every record lacks ``plant_id``
    (caller should still run leakage checks).
    """
    if not records:
        raise ValueError("records must be non-empty")
    if not 0.0 < test_size < 1.0:
        raise ValueError("test_size must be in (0, 1)")

    by_plant: dict[str, list[dict[str, Any]]] = {}
    missing = 0
    for rec in records:
        pid = rec.get("plant_id")
        if pid is None or str(pid).strip() == "":
            missing += 1
            pid = f"__missing_{missing}"
        by_plant.setdefault(str(pid), []).append(rec)

    plants = sorted(by_plant.keys())
    if len(plants) < 2:
        raise ValueError("need at least two plant_id groups for a plant-group split")

    rng = np.random.default_rng(seed)
    order = list(plants)
    rng.shuffle(order)
    n_test = max(1, int(round(len(order) * test_size)))
    n_test = min(n_test, len(order) - 1)
    test_plants = set(order[:n_test])
    train_plants = set(order[n_test:])

    train = [r for p in sorted(train_plants) for r in by_plant[p]]
    test = [r for p in sorted(test_plants) for r in by_plant[p]]
    if not train or not test:
        raise ValueError("split produced an empty train or test set")
    return train, test
