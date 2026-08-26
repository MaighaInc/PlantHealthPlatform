"""
Metadata synchronization — join image and sensor samples by acquisition time.

Clock assumptions (PHP-08)
--------------------------
1. Prefer **acquisition timestamps** carried with each sample (image header stamp,
   or an explicit sensor acquisition time). Never treat "message arrived now" as
   equal to "measurement happened now" without documenting it.
2. When a sensor topic has no stamp (e.g. bare ``std_msgs/Float32``), the ROS
   logger may tag ``stamp_source=receive_approx`` using the local ROS clock.
   That is an approximation for same-host SIMULATION only — not a substitute for
   true sensor acquisition times on distributed hardware.
3. Join rule: for each channel, pick the sample with minimum |Δt| to the image
   acquisition time **only if** |Δt| ≤ ``window_sec``. Otherwise the channel is
   **missing** (null) and listed in ``missing`` / ``stale`` — never silently
   filled with an out-of-window value.
"""

from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Deque


class SyncError(ValueError):
    """Invalid sync inputs."""


def parse_iso_to_epoch(timestamp_iso: str) -> float:
    """Parse ISO-8601 UTC (…Z or offset) to epoch seconds."""
    raw = timestamp_iso.strip()
    if not raw:
        raise SyncError("empty timestamp")
    if raw.endswith("Z"):
        raw = raw[:-1] + "+00:00"
    try:
        dt = datetime.fromisoformat(raw)
    except ValueError as exc:
        raise SyncError(f"unparseable timestamp: {timestamp_iso!r}") from exc
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.timestamp()


def epoch_to_iso(epoch: float) -> str:
    return datetime.fromtimestamp(epoch, tz=timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%S.%fZ"
    )


@dataclass(frozen=True)
class TimedSample:
    """One sensor measurement with its acquisition timestamp."""

    name: str
    value: float
    timestamp_iso: str
    stamp_source: str = "acquisition"
    """acquisition | receive_approx"""


@dataclass
class SyncResult:
    """Result of joining sensors to an image acquisition time."""

    image_timestamp_iso: str
    window_sec: float
    values: dict[str, float | None] = field(default_factory=dict)
    matched_timestamps: dict[str, str | None] = field(default_factory=dict)
    deltas_sec: dict[str, float | None] = field(default_factory=dict)
    missing: list[str] = field(default_factory=list)
    stale_candidates: list[str] = field(default_factory=list)
    stamp_sources: dict[str, str | None] = field(default_factory=dict)

    @property
    def sync_status(self) -> str:
        if not self.values:
            return "none"
        present = [v for v in self.values.values() if v is not None]
        if len(present) == len(self.values) and present:
            return "complete"
        if present:
            return "partial"
        return "none"

    def to_metadata(self) -> dict[str, object]:
        return {
            "sensor_sync": "acquisition_window_php08",
            "sync_status": self.sync_status,
            "sync_window_sec": self.window_sec,
            "image_timestamp_iso": self.image_timestamp_iso,
            "missing_sensors": list(self.missing),
            "stale_candidates": list(self.stale_candidates),
            "sensor_deltas_sec": dict(self.deltas_sec),
            "sensor_matched_timestamps": dict(self.matched_timestamps),
            "sensor_stamp_sources": dict(self.stamp_sources),
        }


def select_nearest_within_window(
    image_timestamp_iso: str,
    samples: list[TimedSample],
    *,
    window_sec: float,
) -> tuple[TimedSample | None, float | None, bool]:
    """
    Return (sample, delta_sec, had_stale_candidate).

    ``had_stale_candidate`` is True when samples existed but all were outside the window
    (so we must not silently pick the nearest out-of-window value).
    """
    if window_sec < 0:
        raise SyncError("window_sec must be >= 0")
    target = parse_iso_to_epoch(image_timestamp_iso)
    if not samples:
        return None, None, False

    best: TimedSample | None = None
    best_abs = float("inf")
    best_delta: float | None = None
    any_outside = False

    for sample in samples:
        delta = parse_iso_to_epoch(sample.timestamp_iso) - target
        ad = abs(delta)
        if ad <= window_sec:
            if ad < best_abs:
                best_abs = ad
                best = sample
                best_delta = delta
        else:
            any_outside = True

    if best is None:
        return None, None, any_outside
    return best, best_delta, False


class SensorTimeBuffer:
    """Ring buffers of TimedSample per channel, keyed by acquisition time."""

    def __init__(self, *, maxlen: int = 200) -> None:
        if maxlen < 1:
            raise SyncError("maxlen must be >= 1")
        self._maxlen = maxlen
        self._buffers: dict[str, Deque[TimedSample]] = defaultdict(
            lambda: deque(maxlen=self._maxlen)
        )

    def add(self, sample: TimedSample) -> None:
        # Validate timestamp early
        parse_iso_to_epoch(sample.timestamp_iso)
        self._buffers[sample.name].append(sample)

    def join(
        self,
        image_timestamp_iso: str,
        channels: list[str],
        *,
        window_sec: float = 1.0,
    ) -> SyncResult:
        parse_iso_to_epoch(image_timestamp_iso)
        result = SyncResult(
            image_timestamp_iso=image_timestamp_iso,
            window_sec=window_sec,
        )
        for name in channels:
            samples = list(self._buffers.get(name, ()))
            chosen, delta, had_stale = select_nearest_within_window(
                image_timestamp_iso, samples, window_sec=window_sec
            )
            if chosen is None:
                result.values[name] = None
                result.matched_timestamps[name] = None
                result.deltas_sec[name] = None
                result.stamp_sources[name] = None
                result.missing.append(name)
                if had_stale:
                    result.stale_candidates.append(name)
            else:
                result.values[name] = chosen.value
                result.matched_timestamps[name] = chosen.timestamp_iso
                result.deltas_sec[name] = delta
                result.stamp_sources[name] = chosen.stamp_source
        return result
