"""Unit tests for acquisition-time metadata sync (PHP-08)."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

_ML = Path(__file__).resolve().parents[2] / "ml"
sys.path.insert(0, str(_ML))

from plant_health_data.sync import (  # noqa: E402
    SensorTimeBuffer,
    SyncError,
    TimedSample,
    select_nearest_within_window,
)


def test_selects_nearest_within_window() -> None:
    samples = [
        TimedSample("temperature", 20.0, "2026-08-25T18:30:00.000000Z"),
        TimedSample("temperature", 21.0, "2026-08-25T18:30:00.400000Z"),
        TimedSample("temperature", 22.0, "2026-08-25T18:30:02.000000Z"),
    ]
    chosen, delta, stale = select_nearest_within_window(
        "2026-08-25T18:30:00.500000Z", samples, window_sec=1.0
    )
    assert chosen is not None
    assert chosen.value == 21.0
    assert delta is not None
    assert abs(delta + 0.1) < 1e-6 or abs(delta - (-0.1)) < 1e-3
    assert stale is False


def test_delayed_out_of_window_not_silently_joined() -> None:
    # Sensor delayed by 5s — must NOT join within 1s window
    samples = [
        TimedSample("soil_moisture", 10.0, "2026-08-25T18:30:05.000000Z"),
    ]
    chosen, delta, had_stale = select_nearest_within_window(
        "2026-08-25T18:30:00.000000Z", samples, window_sec=1.0
    )
    assert chosen is None
    assert delta is None
    assert had_stale is True


def test_missing_channel_flagged() -> None:
    buf = SensorTimeBuffer()
    buf.add(TimedSample("temperature", 25.0, "2026-08-25T18:30:00.100000Z"))
    result = buf.join(
        "2026-08-25T18:30:00.000000Z",
        ["temperature", "humidity"],
        window_sec=1.0,
    )
    assert result.values["temperature"] == 25.0
    assert result.values["humidity"] is None
    assert "humidity" in result.missing
    assert result.sync_status == "partial"


def test_complete_sync_when_all_channels_match() -> None:
    buf = SensorTimeBuffer()
    ts = "2026-08-25T18:30:00.050000Z"
    for name, value in (
        ("soil_moisture", 40.0),
        ("temperature", 24.0),
        ("humidity", 55.0),
    ):
        buf.add(TimedSample(name, value, ts))
    result = buf.join(
        "2026-08-25T18:30:00.000000Z",
        ["soil_moisture", "temperature", "humidity"],
        window_sec=0.2,
    )
    assert result.sync_status == "complete"
    assert result.missing == []
    meta = result.to_metadata()
    assert meta["sensor_sync"] == "acquisition_window_php08"


def test_rejects_bad_timestamp() -> None:
    with pytest.raises(SyncError):
        select_nearest_within_window("not-a-time", [], window_sec=1.0)
