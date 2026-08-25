"""Unit tests for heartbeat formatting — no ROS required."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Allow importing the package without sourcing a ROS workspace.
_PKG_ROOT = (
    Path(__file__).resolve().parents[2]
    / "ros2_ws"
    / "src"
    / "plant_health_status"
)
sys.path.insert(0, str(_PKG_ROOT))

from plant_health_status.heartbeat import (  # noqa: E402
    SYSTEM_STATUS_TOPIC,
    format_status_message,
    parse_status_message,
)


def test_system_status_topic_is_canonical() -> None:
    assert SYSTEM_STATUS_TOPIC == "/system/status"


def test_format_status_message_round_trip() -> None:
    raw = format_status_message(
        sequence=3,
        source="unit_test",
        state="ONLINE",
        timestamp_iso="2026-08-25T18:30:00.000000Z",
    )
    parsed = parse_status_message(raw)
    assert parsed["state"] == "ONLINE"
    assert parsed["seq"] == "3"
    assert parsed["source"] == "unit_test"
    assert parsed["ts"] == "2026-08-25T18:30:00.000000Z"


def test_format_rejects_negative_sequence() -> None:
    with pytest.raises(ValueError, match="sequence"):
        format_status_message(sequence=-1)


def test_parse_rejects_malformed_payload() -> None:
    with pytest.raises(ValueError, match="malformed"):
        parse_status_message("not-a-heartbeat")


def test_parse_rejects_missing_keys() -> None:
    with pytest.raises(ValueError, match="missing keys"):
        parse_status_message("state=ONLINE;seq=1;source=x")
