"""Unit tests for sensor/ML fusion (PHP-15)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_INF = Path(__file__).resolve().parents[2] / "ros2_ws" / "src" / "plant_health_fusion"
sys.path.insert(0, str(_INF))

from plant_health_fusion.fuse import (  # noqa: E402
    fuse_health,
    parse_ml_prediction,
    parse_rules_health,
)


def test_conflict_healthy_vs_stressed_is_unknown() -> None:
    """Acceptance: conflicting inputs → UNKNOWN (documented precedence)."""
    rules = parse_rules_health(
        "status=healthy;score=1.000;reason=nominal;confidence=1.000;ts=t"
    )
    ml = parse_ml_prediction(
        json.dumps(
            {
                "prediction": "stressed",
                "confidence": 0.9,
                "model_name": "m",
                "model_version": "1.0.0",
                "latency_ms": 1.0,
            }
        )
    )
    fused = fuse_health(rules=rules, ml=ml)
    assert fused.status == "unknown"
    assert fused.precedence == "conflict_unknown"


def test_agree_stressed() -> None:
    rules = parse_rules_health(
        "status=stressed;score=0.350;reason=water_stress;confidence=1.000;ts=t"
    )
    ml = parse_ml_prediction(
        json.dumps({"prediction": "stressed", "confidence": 0.88, "model_name": "m"})
    )
    fused = fuse_health(rules=rules, ml=ml)
    assert fused.status == "stressed"
    assert fused.precedence == "agree"


def test_single_source_rules() -> None:
    rules = parse_rules_health(
        "status=healthy;score=1.000;reason=nominal;confidence=1.000;ts=t"
    )
    fused = fuse_health(rules=rules, ml=None)
    assert fused.status == "healthy"
    assert fused.precedence == "single_source"


def test_cv_escalate_when_rules_healthy_and_low_green() -> None:
    rules = parse_rules_health(
        "status=healthy;score=1.000;reason=nominal;confidence=1.000;ts=t"
    )
    fused = fuse_health(
        rules=rules,
        ml=None,
        features={"green_pixel_ratio": 0.02},
        green_stress_threshold=0.08,
    )
    assert fused.status == "stressed"
    assert fused.precedence == "cv_escalate"


def test_no_sources_unknown() -> None:
    fused = fuse_health()
    assert fused.status == "unknown"
    assert fused.precedence == "no_sources"
    payload = json.loads(fused.to_message_data())
    assert payload["status"] == "unknown"


def test_unknown_deferred_uses_rules() -> None:
    rules = parse_rules_health(
        "status=stressed;score=0.450;reason=dry_soil;confidence=1.000;ts=t"
    )
    ml = parse_ml_prediction(
        json.dumps({"prediction": "unknown", "confidence": 0.2, "model_name": "m"})
    )
    fused = fuse_health(rules=rules, ml=ml)
    assert fused.status == "stressed"
    assert fused.precedence == "unknown_deferred"
