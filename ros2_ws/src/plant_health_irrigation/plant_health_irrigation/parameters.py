"""Validated parameters for irrigation GPIO node."""

from __future__ import annotations

from dataclasses import dataclass


class IrrigationParameterError(ValueError):
    """Invalid ROS parameter for irrigation node."""


@dataclass(frozen=True)
class IrrigationNodeParams:
    command_topic: str
    status_topic: str
    development_mode: str
    gpio_backend: str
    relay_pin: int
    active_high: bool

    @classmethod
    def from_raw(
        cls,
        *,
        command_topic: str,
        status_topic: str,
        development_mode: str,
        gpio_backend: str,
        relay_pin: int,
        active_high: bool,
    ) -> IrrigationNodeParams:
        if not command_topic.startswith("/"):
            raise IrrigationParameterError("command_topic must be absolute")
        if not status_topic.startswith("/"):
            raise IrrigationParameterError("status_topic must be absolute")
        pin = int(relay_pin)
        if pin < 0:
            raise IrrigationParameterError("relay_pin must be >= 0")
        return cls(
            command_topic=command_topic,
            status_topic=status_topic,
            development_mode=str(development_mode),
            gpio_backend=str(gpio_backend),
            relay_pin=pin,
            active_high=bool(active_high),
        )
