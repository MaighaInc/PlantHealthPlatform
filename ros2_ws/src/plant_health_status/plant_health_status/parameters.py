"""Validated ROS parameter models for plant_health_status (no rclpy required)."""

from __future__ import annotations

from dataclasses import dataclass

from plant_health_status.heartbeat import (
    DEFAULT_PUBLISH_PERIOD_SEC,
    SYSTEM_STATUS_TOPIC,
)

# Practical bounds for heartbeat publishing
MIN_PUBLISH_PERIOD_SEC = 0.05
MAX_PUBLISH_PERIOD_SEC = 60.0


class ParameterValidationError(ValueError):
    """Raised when a ROS/runtime parameter is invalid."""


def validate_topic(topic: str) -> str:
    topic = topic.strip()
    if not topic.startswith("/"):
        raise ParameterValidationError(
            f"topic must be absolute (start with '/'), got {topic!r}"
        )
    if "//" in topic or topic.endswith("/"):
        raise ParameterValidationError(f"topic has invalid path form: {topic!r}")
    if any(ch.isspace() for ch in topic):
        raise ParameterValidationError(f"topic must not contain whitespace: {topic!r}")
    return topic


def validate_source(source: str) -> str:
    source = source.strip()
    if not source:
        raise ParameterValidationError("source must be non-empty")
    if any(ch.isspace() for ch in source):
        raise ParameterValidationError(f"source must not contain whitespace: {source!r}")
    return source


def validate_publish_period_sec(period: float) -> float:
    try:
        value = float(period)
    except (TypeError, ValueError) as exc:
        raise ParameterValidationError(
            f"publish_period_sec must be a number, got {period!r}"
        ) from exc
    if value < MIN_PUBLISH_PERIOD_SEC or value > MAX_PUBLISH_PERIOD_SEC:
        raise ParameterValidationError(
            f"publish_period_sec must be in "
            f"[{MIN_PUBLISH_PERIOD_SEC}, {MAX_PUBLISH_PERIOD_SEC}], got {value}"
        )
    return value


@dataclass(frozen=True)
class StatusPublisherParams:
    publish_period_sec: float = DEFAULT_PUBLISH_PERIOD_SEC
    topic: str = SYSTEM_STATUS_TOPIC
    source: str = "plant_health_status"

    @classmethod
    def from_raw(
        cls,
        *,
        publish_period_sec: float,
        topic: str,
        source: str,
    ) -> StatusPublisherParams:
        return cls(
            publish_period_sec=validate_publish_period_sec(publish_period_sec),
            topic=validate_topic(topic),
            source=validate_source(source),
        )


@dataclass(frozen=True)
class StatusSubscriberParams:
    topic: str = SYSTEM_STATUS_TOPIC

    @classmethod
    def from_raw(cls, *, topic: str) -> StatusSubscriberParams:
        return cls(topic=validate_topic(topic))
