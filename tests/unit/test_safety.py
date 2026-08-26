"""Unit tests for irrigation safety (PHP-18) — capstone scenarios 2, 3, 5 portions."""

from __future__ import annotations

import sys
from pathlib import Path

_PKG = Path(__file__).resolve().parents[2] / "ros2_ws" / "src" / "plant_health_irrigation"
sys.path.insert(0, str(_PKG))

from plant_health_irrigation.safety import (  # noqa: E402
    SafetyConfig,
    SafetyState,
    apply_safety_transition,
    evaluate_safety,
)


def test_scenario2_dry_soil_allows_water() -> None:
    """Dry soil + intent ON + valid moisture → allow (then GPIO in PHP-17)."""
    cfg = SafetyConfig(wet_stop_threshold=70.0)
    state = SafetyState()
    d = evaluate_safety(
        intent_water=True,
        soil_moisture=20.0,
        config=cfg,
        state=state,
        now_mono=100.0,
    )
    assert d.allow_water is True
    assert d.reason == "safety_ok"


def test_scenario3_invalid_sensor_blocks() -> None:
    cfg = SafetyConfig()
    state = SafetyState()
    d = evaluate_safety(
        intent_water=True,
        soil_moisture=None,
        config=cfg,
        state=state,
        now_mono=1.0,
    )
    assert d.allow_water is False
    assert d.reason == "invalid_sensor"
    assert d.force_off is True


def test_e_stop_blocks() -> None:
    state = SafetyState(e_stop=True)
    d = evaluate_safety(
        intent_water=True,
        soil_moisture=20.0,
        config=SafetyConfig(),
        state=state,
        now_mono=1.0,
    )
    assert d.allow_water is False
    assert d.reason == "e_stop"


def test_max_duration_forces_off() -> None:
    cfg = SafetyConfig(max_duration_sec=10.0)
    state = SafetyState(watering=True, water_started_mono=0.0, relay_on=True)
    d = evaluate_safety(
        intent_water=True,
        soil_moisture=20.0,
        config=cfg,
        state=state,
        now_mono=11.0,
    )
    assert d.allow_water is False
    assert d.reason == "max_duration"


def test_cooldown_blocks_new_on() -> None:
    cfg = SafetyConfig(cooldown_sec=60.0)
    state = SafetyState(last_water_end_mono=100.0, watering=False)
    d = evaluate_safety(
        intent_water=True,
        soil_moisture=20.0,
        config=cfg,
        state=state,
        now_mono=130.0,
    )
    assert d.allow_water is False
    assert d.reason == "cooldown"


def test_scenario5_max_duration_then_off_transition() -> None:
    """Manual path portion: watering ends at max duration and tracks daily."""
    cfg = SafetyConfig(max_duration_sec=5.0)
    state = SafetyState()
    t0 = 0.0
    d1 = evaluate_safety(
        intent_water=True, soil_moisture=25.0, config=cfg, state=state, now_mono=t0
    )
    apply_safety_transition(d1, state, now_mono=t0)
    assert state.relay_on is True
    d2 = evaluate_safety(
        intent_water=True, soil_moisture=25.0, config=cfg, state=state, now_mono=6.0
    )
    apply_safety_transition(d2, state, now_mono=6.0)
    assert state.relay_on is False
    assert state.daily_watered_sec >= 5.0


def test_wet_soil_blocks() -> None:
    d = evaluate_safety(
        intent_water=True,
        soil_moisture=80.0,
        config=SafetyConfig(wet_stop_threshold=70.0),
        state=SafetyState(),
        now_mono=1.0,
    )
    assert d.allow_water is False
    assert d.reason == "soil_already_wet"
