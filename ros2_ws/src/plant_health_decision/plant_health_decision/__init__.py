"""Irrigation decision engine — intent only (PHP-16)."""

from plant_health_decision.decide import decide_irrigation, parse_fused_health
from plant_health_decision.intent import IrrigationIntent

__all__ = [
    "IrrigationIntent",
    "decide_irrigation",
    "parse_fused_health",
]
