"""
Irrigation safety gate (PHP-18) — intent → allowed command.

Fail-safe rules (each unit-tested):

1. Emergency stop → block all watering
2. Invalid / missing soil moisture → block (sensor fail-safe)
3. Soil already at/above wet_stop_threshold → block ON
4. Cooldown since last watering end → block new ON
5. Max daily watering seconds exceeded → block ON
6. Max single-shot duration → auto OFF after elapsed
7. Startup / shutdown → relay commanded OFF (node responsibility)
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any


@dataclass
class SafetyConfig:
    max_duration_sec: float = 30.0
    max_daily_sec: float = 300.0
    cooldown_sec: float = 60.0
    wet_stop_threshold: float = 70.0
    """Block new watering if soil moisture (%) is already at/above this."""


@dataclass
class SafetyState:
    e_stop: bool = False
    watering: bool = False
    water_started_mono: float | None = None
    daily_watered_sec: float = 0.0
    last_water_end_mono: float | None = None
    day_key: str = ""
    relay_on: bool = False
    last_block_reason: str = ""


@dataclass(frozen=True)
class SafetyDecision:
    allow_water: bool
    reason: str
    force_off: bool = False


def _utc_day(now: datetime | None = None) -> str:
    ts = now or datetime.now(timezone.utc)
    return ts.strftime("%Y-%m-%d")


def _invalid(value: float) -> bool:
    try:
        return math.isnan(float(value)) or math.isinf(float(value))
    except (TypeError, ValueError):
        return True


def evaluate_safety(
    *,
    intent_water: bool,
    soil_moisture: float | None,
    config: SafetyConfig,
    state: SafetyState,
    now_mono: float,
    now_utc: datetime | None = None,
) -> SafetyDecision:
    """Pure safety evaluation — prefer OFF on ambiguity."""
    day = _utc_day(now_utc)
    if state.day_key != day:
        state.day_key = day
        state.daily_watered_sec = 0.0

    if state.e_stop:
        state.last_block_reason = "e_stop"
        return SafetyDecision(allow_water=False, reason="e_stop", force_off=True)

    if soil_moisture is None or _invalid(soil_moisture):
        state.last_block_reason = "invalid_sensor"
        return SafetyDecision(allow_water=False, reason="invalid_sensor", force_off=True)

    if intent_water and float(soil_moisture) >= config.wet_stop_threshold:
        state.last_block_reason = "soil_already_wet"
        return SafetyDecision(allow_water=False, reason="soil_already_wet", force_off=True)

    if state.watering and state.water_started_mono is not None:
        elapsed = now_mono - state.water_started_mono
        if elapsed >= config.max_duration_sec:
            state.last_block_reason = "max_duration"
            return SafetyDecision(allow_water=False, reason="max_duration", force_off=True)

    if not intent_water:
        return SafetyDecision(allow_water=False, reason="intent_off", force_off=False)

    if state.daily_watered_sec >= config.max_daily_sec:
        state.last_block_reason = "max_daily"
        return SafetyDecision(allow_water=False, reason="max_daily", force_off=True)

    if state.last_water_end_mono is not None and not state.watering:
        since = now_mono - state.last_water_end_mono
        if since < config.cooldown_sec:
            state.last_block_reason = "cooldown"
            return SafetyDecision(allow_water=False, reason="cooldown", force_off=False)

    return SafetyDecision(allow_water=True, reason="safety_ok", force_off=False)


def apply_safety_transition(
    decision: SafetyDecision,
    state: SafetyState,
    *,
    now_mono: float,
) -> None:
    """Mutate relay tracking / daily totals from a decision."""
    if decision.allow_water:
        if not state.watering:
            state.watering = True
            state.water_started_mono = now_mono
        state.relay_on = True
        return

    if state.watering and state.water_started_mono is not None:
        elapsed = max(0.0, now_mono - state.water_started_mono)
        state.daily_watered_sec += elapsed
        state.last_water_end_mono = now_mono
    state.watering = False
    state.water_started_mono = None
    state.relay_on = False


def parse_intent_message(raw: str) -> dict[str, Any]:
    data = json.loads(raw)
    if not isinstance(data, dict) or "water" not in data:
        raise ValueError("intent missing water")
    return {"water": bool(data["water"]), "reason": str(data.get("reason", ""))}


def build_command_message(*, water: bool, reason: str) -> str:
    payload = {
        "water": water,
        "reason": reason,
        "kind": "command",
        "gated_by": "safety",
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
    }
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))
