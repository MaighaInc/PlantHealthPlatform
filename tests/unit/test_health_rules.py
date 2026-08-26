"""Table-driven tests for rule-based health engine (no ROS)."""

from __future__ import annotations

import math
import sys
from pathlib import Path

import pytest

_PKG = Path(__file__).resolve().parents[2] / "ros2_ws" / "src" / "plant_health_health"
sys.path.insert(0, str(_PKG))

from plant_health_health.rules import (  # noqa: E402
    HealthInputs,
    HealthRulesConfig,
    HealthStatus,
    evaluate_health,
    parse_health_message,
)


@pytest.mark.parametrize(
    ("soil", "temp", "expected_status", "expected_reason"),
    [
        (45.0, 25.0, HealthStatus.HEALTHY, "nominal"),
        (20.0, 25.0, HealthStatus.STRESSED, "dry_soil"),
        (20.0, 35.0, HealthStatus.STRESSED, "water_stress"),
        (None, 25.0, HealthStatus.UNKNOWN, "invalid_sensor"),
        (45.0, None, HealthStatus.UNKNOWN, "invalid_sensor"),
        (float("nan"), 25.0, HealthStatus.UNKNOWN, "invalid_sensor"),
        (45.0, float("nan"), HealthStatus.UNKNOWN, "invalid_sensor"),
        (-5.0, 25.0, HealthStatus.UNKNOWN, "soil_out_of_range"),
        (45.0, 80.0, HealthStatus.UNKNOWN, "temperature_out_of_range"),
    ],
)
def test_health_rules_table(
    soil: float | None,
    temp: float | None,
    expected_status: HealthStatus,
    expected_reason: str,
) -> None:
    result = evaluate_health(
        HealthInputs(soil_moisture=soil, temperature=temp),
        HealthRulesConfig(soil_dry_threshold=30.0, temp_hot_threshold=32.0),
        timestamp_iso="2026-08-25T18:30:00.000000Z",
    )
    assert result.status == expected_status
    assert result.reason == expected_reason
    if expected_status == HealthStatus.HEALTHY:
        assert result.score == 1.0
    if soil is not None and isinstance(soil, float) and math.isnan(soil):
        assert result.status == HealthStatus.UNKNOWN


def test_thresholds_externalized_change_outcome() -> None:
    inputs = HealthInputs(soil_moisture=28.0, temperature=30.0)
    strict = evaluate_health(
        inputs, HealthRulesConfig(soil_dry_threshold=30.0, temp_hot_threshold=32.0)
    )
    relaxed = evaluate_health(
        inputs, HealthRulesConfig(soil_dry_threshold=20.0, temp_hot_threshold=32.0)
    )
    assert strict.status == HealthStatus.STRESSED
    assert relaxed.status == HealthStatus.HEALTHY


def test_message_round_trip() -> None:
    result = evaluate_health(
        HealthInputs(soil_moisture=45.0, temperature=25.0),
        timestamp_iso="2026-08-25T18:30:00.000000Z",
    )
    parsed = parse_health_message(result.to_message_data())
    assert parsed["status"] == "healthy"
    assert parsed["reason"] == "nominal"
