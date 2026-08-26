"""
Irrigation decision engine (PHP-16) — fused health → watering *intent*.

Rules (no GPIO, no ML training):

- ``healthy`` → water=False
- ``stressed`` from rules/agree/cv_escalate/unknown_deferred(rules) → water=True
- ``unknown`` → water=False (fail-safe; never irrigate on ambiguity)
- **ML-only** stressed (single_source with only ML) → water=False
  (``ml_only_blocked`` — ML alone must not drive auto-irrigation)
- UNKNOWN / ML-only unknown → water=False
"""

from __future__ import annotations

import json
from typing import Any

from plant_health_decision.intent import IrrigationIntent


def parse_fused_health(raw: str) -> dict[str, Any]:
    data = json.loads(raw)
    if not isinstance(data, dict):
        raise ValueError("fused health must be a JSON object")
    status = str(data.get("status", "")).strip().lower()
    if status not in {"healthy", "stressed", "unknown"}:
        raise ValueError(f"invalid fused status: {status!r}")
    return {
        "status": status,
        "score": float(data.get("score", 0.0)),
        "confidence": float(data.get("confidence", 0.0)),
        "reason": str(data.get("reason", "")),
        "precedence": str(data.get("precedence", "")),
        "sources": data.get("sources") if isinstance(data.get("sources"), dict) else {},
    }


def decide_irrigation(fused: dict[str, Any]) -> IrrigationIntent:
    """Map fused health to an irrigation intent proposal."""
    status = str(fused["status"]).lower()
    precedence = str(fused.get("precedence", ""))
    sources = fused.get("sources") or {}
    confidence = float(fused.get("confidence", 0.0))

    if status == "healthy":
        return IrrigationIntent(
            water=False,
            reason="healthy_no_water",
            fused_status=status,
            fused_precedence=precedence,
            confidence=confidence,
        )

    if status == "unknown":
        return IrrigationIntent(
            water=False,
            reason="unknown_blocks_irrigation",
            fused_status=status,
            fused_precedence=precedence,
            confidence=confidence,
        )

    if status == "stressed":
        # Block ML-only auto-irrigation (no rules corroboration)
        has_rules = "rules" in sources
        has_ml = "ml" in sources
        if precedence == "single_source" and has_ml and not has_rules:
            return IrrigationIntent(
                water=False,
                reason="ml_only_blocked",
                fused_status=status,
                fused_precedence=precedence,
                confidence=confidence,
            )
        return IrrigationIntent(
            water=True,
            reason="stressed_needs_water",
            fused_status=status,
            fused_precedence=precedence,
            confidence=confidence,
        )

    return IrrigationIntent(
        water=False,
        reason="unhandled_status_blocks",
        fused_status=status,
        fused_precedence=precedence,
        confidence=confidence,
    )
