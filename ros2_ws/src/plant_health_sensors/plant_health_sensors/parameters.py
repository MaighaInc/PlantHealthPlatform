"""Parameter validation for virtual sensor node (no rclpy)."""

from __future__ import annotations

from dataclasses import dataclass

from plant_health_sensors.sensor_kinds import SensorKind


class SensorParameterError(ValueError):
    """Invalid virtual-sensor ROS/runtime parameter."""


def validate_topic(topic: str) -> str:
    topic = topic.strip()
    if not topic.startswith("/"):
        raise SensorParameterError(
            f"topic must be absolute (start with '/'), got {topic!r}"
        )
    if "//" in topic or topic.endswith("/") or any(ch.isspace() for ch in topic):
        raise SensorParameterError(f"topic has invalid form: {topic!r}")
    return topic


def validate_period_sec(period: float) -> float:
    try:
        value = float(period)
    except (TypeError, ValueError) as exc:
        raise SensorParameterError(f"sample_period_sec must be a number: {period!r}") from exc
    if value < 0.05 or value > 60.0:
        raise SensorParameterError(
            f"sample_period_sec must be in [0.05, 60], got {value}"
        )
    return value


def validate_probability(name: str, value: float) -> float:
    try:
        prob = float(value)
    except (TypeError, ValueError) as exc:
        raise SensorParameterError(f"{name} must be a number") from exc
    if not 0.0 <= prob <= 1.0:
        raise SensorParameterError(f"{name} must be in [0, 1], got {prob}")
    return prob


def parse_sensor_kind(raw: str) -> SensorKind:
    try:
        return SensorKind(raw.strip().lower())
    except ValueError as exc:
        allowed = ", ".join(k.value for k in SensorKind)
        raise SensorParameterError(
            f"unknown sensor kind {raw!r}; expected one of: {allowed}"
        ) from exc


@dataclass(frozen=True)
class VirtualPublisherParams:
    sample_period_sec: float
    enabled_kinds: tuple[SensorKind, ...]
    seed: int
    noise_std: float
    outlier_probability: float
    invalid_probability: float

    @classmethod
    def from_raw(
        cls,
        *,
        sample_period_sec: float,
        enabled_kinds: str,
        seed: int,
        noise_std: float,
        outlier_probability: float,
        invalid_probability: float,
    ) -> VirtualPublisherParams:
        kinds_raw = [k.strip() for k in enabled_kinds.split(",") if k.strip()]
        if not kinds_raw:
            raise SensorParameterError("enabled_kinds must list at least one sensor")
        kinds = tuple(parse_sensor_kind(k) for k in kinds_raw)
        if float(noise_std) < 0:
            raise SensorParameterError("noise_std must be >= 0")
        return cls(
            sample_period_sec=validate_period_sec(sample_period_sec),
            enabled_kinds=kinds,
            seed=int(seed),
            noise_std=float(noise_std),
            outlier_probability=validate_probability(
                "outlier_probability", outlier_probability
            ),
            invalid_probability=validate_probability(
                "invalid_probability", invalid_probability
            ),
        )
