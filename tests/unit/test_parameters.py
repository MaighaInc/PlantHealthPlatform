"""Unit tests for ROS parameter validation (no rclpy required)."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

_PKG_ROOT = (
    Path(__file__).resolve().parents[2]
    / "ros2_ws"
    / "src"
    / "plant_health_status"
)
sys.path.insert(0, str(_PKG_ROOT))

from plant_health_status.parameters import (  # noqa: E402
    ParameterValidationError,
    StatusPublisherParams,
    StatusSubscriberParams,
    validate_publish_period_sec,
    validate_topic,
)


def test_valid_publisher_params_accepted() -> None:
    params = StatusPublisherParams.from_raw(
        publish_period_sec=0.5,
        topic="/system/status",
        source="plant_health_status",
    )
    assert params.publish_period_sec == 0.5
    assert params.topic == "/system/status"


def test_invalid_period_rejected() -> None:
    with pytest.raises(ParameterValidationError, match="publish_period_sec"):
        validate_publish_period_sec(0.0)
    with pytest.raises(ParameterValidationError, match="publish_period_sec"):
        validate_publish_period_sec(100.0)


def test_invalid_topic_rejected() -> None:
    with pytest.raises(ParameterValidationError, match="absolute"):
        validate_topic("system/status")
    with pytest.raises(ParameterValidationError, match="whitespace"):
        validate_topic("/system/ status")


def test_subscriber_params_from_raw() -> None:
    params = StatusSubscriberParams.from_raw(topic="/system/status")
    assert params.topic == "/system/status"


def test_empty_source_rejected() -> None:
    with pytest.raises(ParameterValidationError, match="source"):
        StatusPublisherParams.from_raw(
            publish_period_sec=1.0,
            topic="/system/status",
            source="  ",
        )
