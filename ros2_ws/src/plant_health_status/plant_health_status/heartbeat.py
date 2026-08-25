"""Pure-Python heartbeat helpers (testable without rclpy)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone


# Canonical topic for PHP-01 (see docs/design/ROS_ARCHITECTURE.md)
SYSTEM_STATUS_TOPIC = "/system/status"

DEFAULT_NODE_NAME_PUBLISHER = "status_publisher"
DEFAULT_NODE_NAME_SUBSCRIBER = "status_subscriber"
DEFAULT_PUBLISH_PERIOD_SEC = 1.0


@dataclass(frozen=True)
class HeartbeatPayload:
    """Structured status before serialization to std_msgs/String."""

    state: str
    sequence: int
    source: str
    timestamp_iso: str

    def to_message_data(self) -> str:
        """Serialize for std_msgs/String.data (stable, parse-friendly)."""
        return (
            f"state={self.state};seq={self.sequence};"
            f"source={self.source};ts={self.timestamp_iso}"
        )


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def format_status_message(
    *,
    sequence: int,
    source: str = "plant_health_status",
    state: str = "ONLINE",
    timestamp_iso: str | None = None,
) -> str:
    """
    Build the `/system/status` string payload.

    Using std_msgs/String keeps PHP-01 simple; a custom PlantHealth message
    can replace this later when fields grow beyond a heartbeat.
    """
    if sequence < 0:
        raise ValueError("sequence must be >= 0")
    if not state:
        raise ValueError("state must be non-empty")
    if not source:
        raise ValueError("source must be non-empty")

    payload = HeartbeatPayload(
        state=state,
        sequence=sequence,
        source=source,
        timestamp_iso=timestamp_iso or utc_now_iso(),
    )
    return payload.to_message_data()


def parse_status_message(data: str) -> dict[str, str]:
    """Parse heartbeat string into a dict; raises ValueError if malformed."""
    if not data or ";" not in data:
        raise ValueError(f"malformed status message: {data!r}")

    parts: dict[str, str] = {}
    for token in data.split(";"):
        if "=" not in token:
            raise ValueError(f"malformed token in status message: {token!r}")
        key, value = token.split("=", 1)
        parts[key] = value

    required = {"state", "seq", "source", "ts"}
    missing = required - set(parts)
    if missing:
        raise ValueError(f"status message missing keys: {sorted(missing)}")
    return parts
