"""Unit tests for irrigation decision engine (PHP-16)."""

from __future__ import annotations

import ast
import json
import sys
from pathlib import Path

import pytest

_PKG = Path(__file__).resolve().parents[2] / "ros2_ws" / "src" / "plant_health_decision"
sys.path.insert(0, str(_PKG))

from plant_health_decision.decide import decide_irrigation, parse_fused_health  # noqa: E402
from plant_health_decision.parameters import (  # noqa: E402
    DecisionNodeParams,
    DecisionParameterError,
)


def test_healthy_no_water_intent() -> None:
    fused = parse_fused_health(
        json.dumps(
            {
                "status": "healthy",
                "score": 1.0,
                "confidence": 1.0,
                "reason": "agree:nominal",
                "precedence": "agree",
                "sources": {"rules": {"status": "healthy"}, "ml": {"prediction": "healthy"}},
            }
        )
    )
    intent = decide_irrigation(fused)
    assert intent.water is False
    assert intent.reason == "healthy_no_water"
    assert intent.to_dict()["actuates"] is False


def test_stressed_dry_water_intent() -> None:
    fused = parse_fused_health(
        json.dumps(
            {
                "status": "stressed",
                "score": 0.35,
                "confidence": 0.9,
                "reason": "agree:water_stress",
                "precedence": "agree",
                "sources": {
                    "rules": {"status": "stressed", "reason": "water_stress"},
                    "ml": {"prediction": "stressed"},
                },
            }
        )
    )
    intent = decide_irrigation(fused)
    assert intent.water is True
    assert intent.reason == "stressed_needs_water"


def test_unknown_blocks_irrigation() -> None:
    fused = parse_fused_health(
        json.dumps(
            {
                "status": "unknown",
                "score": 0.0,
                "confidence": 1.0,
                "reason": "conflict:rules=healthy,ml=stressed",
                "precedence": "conflict_unknown",
                "sources": {},
            }
        )
    )
    intent = decide_irrigation(fused)
    assert intent.water is False
    assert intent.reason == "unknown_blocks_irrigation"


def test_ml_only_stressed_blocked() -> None:
    """UNKNOWN ML alone / ML-only path must not produce water intent."""
    fused = parse_fused_health(
        json.dumps(
            {
                "status": "stressed",
                "score": 0.4,
                "confidence": 0.7,
                "reason": "ml_only",
                "precedence": "single_source",
                "sources": {"ml": {"prediction": "stressed", "confidence": 0.7}},
            }
        )
    )
    intent = decide_irrigation(fused)
    assert intent.water is False
    assert intent.reason == "ml_only_blocked"


def test_ml_only_unknown_blocks() -> None:
    fused = parse_fused_health(
        json.dumps(
            {
                "status": "unknown",
                "score": 0.0,
                "confidence": 0.2,
                "reason": "ml_only",
                "precedence": "single_source",
                "sources": {"ml": {"prediction": "unknown"}},
            }
        )
    )
    intent = decide_irrigation(fused)
    assert intent.water is False


def test_params_forbid_command_topic() -> None:
    with pytest.raises(DecisionParameterError, match="irrigation/command"):
        DecisionNodeParams.from_raw(
            fused_topic="/plant/fused_health",
            intent_topic="/irrigation/command",
            publish_period_sec=1.0,
        )


def test_decision_package_never_imports_gpio() -> None:
    """Acceptance: decision never imports GPIO implementations."""
    root = _PKG / "plant_health_decision"
    forbidden = ("GPIO", "gpio", "RPi", "MockGPIO", "RaspberryPiGPIO")
    for path in root.rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert not any(f in alias.name for f in forbidden), path
            elif isinstance(node, ast.ImportFrom):
                mod = node.module or ""
                assert not any(f in mod for f in forbidden), path
                for alias in node.names:
                    assert not any(f in alias.name for f in forbidden), path
