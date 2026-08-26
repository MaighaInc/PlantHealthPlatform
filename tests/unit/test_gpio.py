"""Unit tests for GPIO abstraction (PHP-17)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_PKG = Path(__file__).resolve().parents[2] / "ros2_ws" / "src" / "plant_health_irrigation"
sys.path.insert(0, str(_PKG))

from plant_health_irrigation.actuator import (  # noqa: E402
    apply_irrigation_command,
    parse_irrigation_command,
)
from plant_health_irrigation.factory import (  # noqa: E402
    GPIOFactoryError,
    create_gpio,
)
from plant_health_irrigation.interfaces import PinState  # noqa: E402
from plant_health_irrigation.mock_gpio import MockGPIO  # noqa: E402


def test_mock_gpio_records_pin_transitions() -> None:
    gpio = MockGPIO()
    gpio.setup_output(17, initial=PinState.LOW)
    gpio.write(17, PinState.HIGH)
    gpio.write(17, PinState.LOW)
    states = [t.state for t in gpio.transitions]
    assert states == [PinState.LOW, PinState.HIGH, PinState.LOW]
    assert gpio.transitions[0].pin == 17
    assert gpio.read(17) is PinState.LOW


def test_apply_command_uses_interface_only() -> None:
    gpio = MockGPIO()
    gpio.setup_output(17, initial=PinState.LOW)
    cmd = parse_irrigation_command(
        json.dumps({"water": True, "reason": "stressed_needs_water"})
    )
    status = apply_irrigation_command(gpio, cmd, relay_pin=17, active_high=True)
    assert status.water is True
    assert status.pin_state == "high"
    assert any(t.state is PinState.HIGH for t in gpio.transitions)


def test_simulation_and_development_use_mock_exclusively() -> None:
    for mode in ("SIMULATION", "DEVELOPMENT"):
        gpio = create_gpio(mode=mode, backend="auto")
        assert isinstance(gpio, MockGPIO)
        with pytest.raises(GPIOFactoryError, match="MockGPIO exclusively"):
            create_gpio(mode=mode, backend="rpi")


def test_cleanup_forces_low() -> None:
    gpio = MockGPIO()
    gpio.setup_output(5, initial=PinState.LOW)
    gpio.write(5, PinState.HIGH)
    gpio.cleanup()
    assert gpio.transitions[-1].state is PinState.LOW
