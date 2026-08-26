"""Parameter validation for health engine node."""

from __future__ import annotations

from dataclasses import dataclass

from plant_health_health.rules import HealthRulesConfig


class HealthParameterError(ValueError):
    """Invalid health node parameter."""


@dataclass(frozen=True)
class HealthNodeParams:
    soil_dry_threshold: float
    temp_hot_threshold: float
    publish_period_sec: float
    health_topic: str = "/plant/health"

    def to_rules_config(self) -> HealthRulesConfig:
        cfg = HealthRulesConfig(
            soil_dry_threshold=self.soil_dry_threshold,
            temp_hot_threshold=self.temp_hot_threshold,
        )
        cfg.validate()
        return cfg

    @classmethod
    def from_raw(
        cls,
        *,
        soil_dry_threshold: float,
        temp_hot_threshold: float,
        publish_period_sec: float,
        health_topic: str = "/plant/health",
    ) -> HealthNodeParams:
        period = float(publish_period_sec)
        if period < 0.05 or period > 60.0:
            raise HealthParameterError(
                f"publish_period_sec must be in [0.05, 60], got {period}"
            )
        topic = str(health_topic).strip()
        if not topic.startswith("/"):
            raise HealthParameterError(f"health_topic must be absolute, got {topic!r}")
        try:
            cfg = HealthRulesConfig(
                soil_dry_threshold=float(soil_dry_threshold),
                temp_hot_threshold=float(temp_hot_threshold),
            )
            cfg.validate()
        except ValueError as exc:
            raise HealthParameterError(str(exc)) from exc
        return cls(
            soil_dry_threshold=float(soil_dry_threshold),
            temp_hot_threshold=float(temp_hot_threshold),
            publish_period_sec=period,
            health_topic=topic,
        )
