"""Train/test leakage detection for plant-health ML (PHP-12)."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any, Sequence

from plant_health_ml.preprocess import FEATURE_KEYS


@dataclass(frozen=True)
class LeakageFinding:
    kind: str
    detail: str


@dataclass
class LeakageReport:
    """Result of leakage checks. ``ok`` is False when any finding is present."""

    ok: bool
    findings: list[LeakageFinding] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "findings": [{"kind": f.kind, "detail": f.detail} for f in self.findings],
        }


def _feature_fingerprint(rec: dict[str, Any], keys: Sequence[str]) -> str:
    feats = rec.get("features") if isinstance(rec.get("features"), dict) else rec
    payload = {k: feats.get(k) if isinstance(feats, dict) else None for k in keys}
    blob = json.dumps(payload, sort_keys=True, default=str)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def check_leakage(
    train: Sequence[dict[str, Any]],
    test: Sequence[dict[str, Any]],
    *,
    feature_keys: Sequence[str] | None = None,
) -> LeakageReport:
    """
    Fail the gate when:

    - Same ``plant_id`` appears in both train and test
    - Identical feature vectors appear in both splits (duplicate contamination)
    """
    keys = list(feature_keys or FEATURE_KEYS)
    findings: list[LeakageFinding] = []

    train_plants = {
        str(r["plant_id"])
        for r in train
        if r.get("plant_id") is not None and str(r["plant_id"]).strip() != ""
    }
    test_plants = {
        str(r["plant_id"])
        for r in test
        if r.get("plant_id") is not None and str(r["plant_id"]).strip() != ""
    }
    overlap = sorted(train_plants & test_plants)
    if overlap:
        findings.append(
            LeakageFinding(
                kind="plant_id_overlap",
                detail=f"plants in both splits: {overlap[:20]}"
                + ("..." if len(overlap) > 20 else ""),
            )
        )

    train_fps = {_feature_fingerprint(r, keys) for r in train}
    test_fps = {_feature_fingerprint(r, keys) for r in test}
    dup = train_fps & test_fps
    if dup:
        findings.append(
            LeakageFinding(
                kind="duplicate_features",
                detail=f"{len(dup)} identical feature fingerprint(s) across train/test",
            )
        )

    return LeakageReport(ok=len(findings) == 0, findings=findings)
