"""Unit tests for observability helpers (PHP-26)."""

from __future__ import annotations

import sys
from pathlib import Path

_SHARED = Path(__file__).resolve().parents[2] / "shared"
sys.path.insert(0, str(_SHARED))

from plant_health_common.observability import MetricsRegistry, log_event  # noqa: E402
import logging


def test_metrics_counters_and_freshness() -> None:
    m = MetricsRegistry()
    m.incr("inference_errors")
    m.incr("inference_errors")
    m.set_gauge("inference_latency_ms", 12.5)
    m.touch_sensor("soil_moisture", now=100.0)
    assert m.counters["inference_errors"] == 2
    assert m.gauges["inference_latency_ms"] == 12.5
    assert m.freshness_sec("soil_moisture", now=105.0) == 5.0
    assert "soil_moisture" in m.snapshot()["sensor_keys"]


def test_log_event_json(caplog) -> None:
    logger = logging.getLogger("test_obs")
    with caplog.at_level(logging.INFO):
        log_event(logger, "stale_sensor", kind="soil_moisture", age_sec=12)
    assert "stale_sensor" in caplog.text
