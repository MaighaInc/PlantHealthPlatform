"""Apply irrigation commands through GPIOInterface only (no direct RPi calls)."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from plant_health_irrigation.interfaces import GPIOInterface, PinState


@dataclass(frozen=True)
class IrrigationCommand:
    water: bool
    reason: str = ""
    source: str = "command"


@dataclass(frozen=True)
class IrrigationStatus:
    water: bool
    pin: int
    pin_state: str
    reason: str
    timestamp_iso: str = ""

    def __post_init__(self) -> None:
        if not self.timestamp_iso:
            object.__setattr__(
                self,
                "timestamp_iso",
                datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            )

    def to_message_data(self) -> str:
        payload: dict[str, Any] = {
            "water": self.water,
            "pin": self.pin,
            "pin_state": self.pin_state,
            "reason": self.reason,
            "timestamp": self.timestamp_iso,
        }
        return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def parse_irrigation_command(raw: str) -> IrrigationCommand:
    """
    Accept `/irrigation/command` JSON or intent-shaped JSON (`water` bool).

    Safety gating is PHP-18; this layer only drives the configured pin.
    """
    data = json.loads(raw)
    if not isinstance(data, dict):
        raise ValueError("command must be a JSON object")
    if "water" not in data:
        raise ValueError("command missing 'water'")
    return IrrigationCommand(
        water=bool(data["water"]),
        reason=str(data.get("reason", "")),
        source=str(data.get("kind", data.get("source", "command"))),
    )


def apply_irrigation_command(
    gpio: GPIOInterface,
    command: IrrigationCommand,
    *,
    relay_pin: int,
    active_high: bool = True,
) -> IrrigationStatus:
    """Drive relay pin via GPIOInterface only."""
    on_state = PinState.HIGH if active_high else PinState.LOW
    off_state = PinState.LOW if active_high else PinState.HIGH
    state = on_state if command.water else off_state
    gpio.write(relay_pin, state)
    return IrrigationStatus(
        water=command.water,
        pin=relay_pin,
        pin_state=state.value,
        reason=command.reason or ("water_on" if command.water else "water_off"),
    )
