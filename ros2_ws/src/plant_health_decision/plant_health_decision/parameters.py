"""Validated parameters for decision node."""

from __future__ import annotations

from dataclasses import dataclass


class DecisionParameterError(ValueError):
    """Invalid ROS parameter for decision node."""


@dataclass(frozen=True)
class DecisionNodeParams:
    fused_topic: str
    intent_topic: str
    publish_period_sec: float

    @classmethod
    def from_raw(
        cls,
        *,
        fused_topic: str,
        intent_topic: str,
        publish_period_sec: float,
    ) -> DecisionNodeParams:
        if not fused_topic.startswith("/"):
            raise DecisionParameterError("fused_topic must be absolute")
        if not intent_topic.startswith("/"):
            raise DecisionParameterError("intent_topic must be absolute")
        if intent_topic == "/irrigation/command":
            raise DecisionParameterError(
                "intent must not publish to /irrigation/command (ADR-0003); "
                "use /irrigation/intent"
            )
        period = float(publish_period_sec)
        if period <= 0:
            raise DecisionParameterError("publish_period_sec must be > 0")
        return cls(
            fused_topic=fused_topic,
            intent_topic=intent_topic,
            publish_period_sec=period,
        )
