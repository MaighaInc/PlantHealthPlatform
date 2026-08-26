"""E2E smoke: fused → decision → safety → MockGPIO (PHP-24)."""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_ROOT / "ros2_ws" / "src" / "plant_health_fusion"))
sys.path.insert(0, str(_ROOT / "ros2_ws" / "src" / "plant_health_decision"))
sys.path.insert(0, str(_ROOT / "ros2_ws" / "src" / "plant_health_irrigation"))

from plant_health_decision.decide import decide_irrigation  # noqa: E402
from plant_health_fusion.fuse import fuse_health  # noqa: E402
from plant_health_irrigation.actuator import (  # noqa: E402
    apply_irrigation_command,
    parse_irrigation_command,
)
from plant_health_irrigation.interfaces import PinState  # noqa: E402
from plant_health_irrigation.mock_gpio import MockGPIO  # noqa: E402
from plant_health_irrigation.safety import (  # noqa: E402
    SafetyConfig,
    SafetyState,
    apply_safety_transition,
    build_command_message,
    evaluate_safety,
)


def test_e2e_dry_soil_path_to_mock_gpio() -> None:
    fused = fuse_health(
        rules={
            "status": "stressed",
            "score": 0.35,
            "confidence": 1.0,
            "reason": "dry_soil",
        },
        ml={"prediction": "stressed", "confidence": 0.9},
    )
    intent = decide_irrigation(fused.to_dict())
    assert intent.water is True

    state = SafetyState()
    decision = evaluate_safety(
        intent_water=True,
        soil_moisture=18.0,
        config=SafetyConfig(),
        state=state,
        now_mono=time.monotonic(),
    )
    apply_safety_transition(decision, state, now_mono=time.monotonic())
    assert decision.allow_water is True

    cmd = parse_irrigation_command(
        build_command_message(water=True, reason=decision.reason)
    )
    gpio = MockGPIO()
    gpio.setup_output(17, initial=PinState.LOW)
    status = apply_irrigation_command(gpio, cmd, relay_pin=17)
    assert status.water is True
    assert any(t.state is PinState.HIGH for t in gpio.transitions)
