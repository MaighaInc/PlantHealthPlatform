"""Observability helpers — structured logs + counters (PHP-26)."""

from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


def configure_structured_logging(level: int = logging.INFO) -> None:
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )


def log_event(logger: logging.Logger, event: str, **fields: Any) -> None:
    payload = {
        "event": event,
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        **fields,
    }
    logger.info(json.dumps(payload, sort_keys=True))


@dataclass
class MetricsRegistry:
    counters: dict[str, int] = field(default_factory=dict)
    gauges: dict[str, float] = field(default_factory=dict)
    last_sensor_mono: dict[str, float] = field(default_factory=dict)

    def incr(self, name: str, by: int = 1) -> None:
        self.counters[name] = self.counters.get(name, 0) + by

    def set_gauge(self, name: str, value: float) -> None:
        self.gauges[name] = float(value)

    def touch_sensor(self, kind: str, now: float | None = None) -> None:
        self.last_sensor_mono[kind] = now if now is not None else time.monotonic()

    def freshness_sec(self, kind: str, now: float | None = None) -> float | None:
        ts = self.last_sensor_mono.get(kind)
        if ts is None:
            return None
        return (now if now is not None else time.monotonic()) - ts

    def snapshot(self) -> dict[str, Any]:
        return {
            "counters": dict(self.counters),
            "gauges": dict(self.gauges),
            "sensor_keys": sorted(self.last_sensor_mono),
        }


METRICS = MetricsRegistry()
