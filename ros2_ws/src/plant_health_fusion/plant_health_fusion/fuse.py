"""
Sensor + rules + ML fusion (PHP-15) — pure logic, no GPIO.

Precedence (documented — decision engine must rely on this):

1. If neither rules nor ML is available → ``unknown`` (``no_sources``).
2. If only one of rules/ML is available → use that source (``single_source``).
3. If either source is ``unknown`` and the other is definitive → use the
   definitive source at reduced confidence (``unknown_deferred``).
4. If both agree (healthy/healthy or stressed/stressed) → that status
   (``agree``).
5. If rules and ML conflict (healthy vs stressed) → ``unknown``
   (``conflict_unknown``). Safety: do not invent a winner for actuation.
6. Optional CV cue: ``green_pixel_ratio`` below ``green_stress_threshold``
   may escalate a sole ``healthy`` result toward ``stressed`` when rules
   alone are healthy and ML is missing (``cv_escalate``); never overrides
   an explicit conflict_unknown outcome.
"""

from __future__ import annotations

import json
from typing import Any

from plant_health_fusion.fused import FusedHealth

VALID = frozenset({"healthy", "stressed", "unknown"})


def parse_rules_health(raw: str) -> dict[str, Any]:
    """Parse `/plant/health` semicolon payload."""
    if not raw or ";" not in raw:
        raise ValueError(f"malformed health message: {raw!r}")
    parts: dict[str, str] = {}
    for token in raw.split(";"):
        if "=" not in token:
            raise ValueError(f"malformed token: {token!r}")
        key, value = token.split("=", 1)
        parts[key] = value
    required = {"status", "score", "reason", "confidence", "ts"}
    missing = required - set(parts)
    if missing:
        raise ValueError(f"health message missing keys: {sorted(missing)}")
    status = parts["status"].strip().lower()
    if status not in VALID:
        raise ValueError(f"invalid health status: {status!r}")
    return {
        "status": status,
        "score": float(parts["score"]),
        "reason": parts["reason"],
        "confidence": float(parts["confidence"]),
        "ts": parts["ts"],
    }


def parse_ml_prediction(raw: str) -> dict[str, Any]:
    """Parse `/plant/disease_prediction` JSON payload."""
    data = json.loads(raw)
    if not isinstance(data, dict):
        raise ValueError("prediction must be a JSON object")
    pred = str(data.get("prediction", "")).strip().lower()
    if pred not in VALID:
        raise ValueError(f"invalid prediction: {pred!r}")
    return {
        "prediction": pred,
        "confidence": float(data.get("confidence", 0.0)),
        "model_name": str(data.get("model_name", "")),
        "model_version": str(data.get("model_version", "")),
        "latency_ms": float(data.get("latency_ms", 0.0)),
    }


def parse_features_optional(raw: str | None) -> dict[str, float | None]:
    if not raw:
        return {}
    data = json.loads(raw)
    feats = data.get("features", data) if isinstance(data, dict) else {}
    if not isinstance(feats, dict):
        return {}
    out: dict[str, float | None] = {}
    for key in ("green_pixel_ratio", "leaf_area", "soil_moisture", "temperature"):
        if key in feats:
            val = feats[key]
            out[key] = None if val is None else float(val)
    return out


def fuse_health(
    *,
    rules: dict[str, Any] | None = None,
    ml: dict[str, Any] | None = None,
    features: dict[str, float | None] | None = None,
    green_stress_threshold: float = 0.08,
) -> FusedHealth:
    """Combine rules + ML (+ optional CV features) into one fused status."""
    features = features or {}
    sources: dict[str, Any] = {}
    if rules is not None:
        sources["rules"] = {
            "status": rules["status"],
            "confidence": rules["confidence"],
            "reason": rules.get("reason"),
            "score": rules.get("score"),
        }
    if ml is not None:
        sources["ml"] = {
            "prediction": ml["prediction"],
            "confidence": ml["confidence"],
            "model_name": ml.get("model_name"),
            "model_version": ml.get("model_version"),
        }
    if features:
        sources["features"] = {k: features.get(k) for k in features}

    if rules is None and ml is None:
        return FusedHealth(
            status="unknown",
            score=0.0,
            confidence=1.0,
            reason="no_sources",
            precedence="no_sources",
            sources=sources,
        )

    if rules is not None and ml is None:
        status = rules["status"]
        score = float(rules.get("score", 0.5))
        conf = float(rules["confidence"])
        reason = f"rules_only:{rules.get('reason', status)}"
        precedence = "single_source"
        status, score, conf, reason, precedence = _maybe_cv_escalate(
            status,
            score,
            conf,
            reason,
            precedence,
            features,
            green_stress_threshold,
        )
        return FusedHealth(
            status=status,
            score=score,
            confidence=conf,
            reason=reason,
            precedence=precedence,
            sources=sources,
        )

    if ml is not None and rules is None:
        status = ml["prediction"]
        conf = float(ml["confidence"])
        score = 1.0 if status == "healthy" else (0.4 if status == "stressed" else 0.0)
        return FusedHealth(
            status=status,
            score=score,
            confidence=conf,
            reason="ml_only",
            precedence="single_source",
            sources=sources,
        )

    assert rules is not None and ml is not None
    r_status = rules["status"]
    m_status = ml["prediction"]

    if r_status == "unknown" and m_status == "unknown":
        return FusedHealth(
            status="unknown",
            score=0.0,
            confidence=1.0,
            reason="both_unknown",
            precedence="unknown_deferred",
            sources=sources,
        )

    if r_status == "unknown" and m_status in {"healthy", "stressed"}:
        score = 1.0 if m_status == "healthy" else 0.4
        return FusedHealth(
            status=m_status,
            score=score,
            confidence=float(ml["confidence"]) * 0.8,
            reason="rules_unknown_use_ml",
            precedence="unknown_deferred",
            sources=sources,
        )

    if m_status == "unknown" and r_status in {"healthy", "stressed"}:
        return FusedHealth(
            status=r_status,
            score=float(rules.get("score", 0.5)),
            confidence=float(rules["confidence"]) * 0.8,
            reason=f"ml_unknown_use_rules:{rules.get('reason', r_status)}",
            precedence="unknown_deferred",
            sources=sources,
        )

    if r_status == m_status:
        conf = min(float(rules["confidence"]), float(ml["confidence"]))
        score = float(rules.get("score", 0.5))
        return FusedHealth(
            status=r_status,
            score=score,
            confidence=conf,
            reason=f"agree:{rules.get('reason', r_status)}",
            precedence="agree",
            sources=sources,
        )

    # Conflict: healthy vs stressed → UNKNOWN (do not pick a winner)
    return FusedHealth(
        status="unknown",
        score=0.0,
        confidence=1.0,
        reason=f"conflict:rules={r_status},ml={m_status}",
        precedence="conflict_unknown",
        sources=sources,
    )


def _maybe_cv_escalate(
    status: str,
    score: float,
    conf: float,
    reason: str,
    precedence: str,
    features: dict[str, float | None],
    green_stress_threshold: float,
) -> tuple[str, float, float, str, str]:
    if status != "healthy":
        return status, score, conf, reason, precedence
    ratio = features.get("green_pixel_ratio")
    if ratio is None:
        return status, score, conf, reason, precedence
    if float(ratio) < green_stress_threshold:
        return (
            "stressed",
            min(score, 0.45),
            conf * 0.7,
            f"{reason}+cv_low_green",
            "cv_escalate",
        )
    return status, score, conf, reason, precedence
