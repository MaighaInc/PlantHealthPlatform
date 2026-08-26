"""Validated parameters for fusion node."""

from __future__ import annotations

from dataclasses import dataclass


class FusionParameterError(ValueError):
    """Invalid ROS parameter for fusion node."""


@dataclass(frozen=True)
class FusionNodeParams:
    health_topic: str
    features_topic: str
    prediction_topic: str
    fused_topic: str
    publish_period_sec: float
    green_stress_threshold: float

    @classmethod
    def from_raw(
        cls,
        *,
        health_topic: str,
        features_topic: str,
        prediction_topic: str,
        fused_topic: str,
        publish_period_sec: float,
        green_stress_threshold: float,
    ) -> FusionNodeParams:
        for name, topic in (
            ("health_topic", health_topic),
            ("features_topic", features_topic),
            ("prediction_topic", prediction_topic),
            ("fused_topic", fused_topic),
        ):
            if not str(topic).startswith("/"):
                raise FusionParameterError(f"{name} must be absolute")
        period = float(publish_period_sec)
        if period <= 0:
            raise FusionParameterError("publish_period_sec must be > 0")
        thr = float(green_stress_threshold)
        if not 0.0 <= thr <= 1.0:
            raise FusionParameterError("green_stress_threshold must be in [0, 1]")
        return cls(
            health_topic=health_topic,
            features_topic=features_topic,
            prediction_topic=prediction_topic,
            fused_topic=fused_topic,
            publish_period_sec=period,
            green_stress_threshold=thr,
        )
