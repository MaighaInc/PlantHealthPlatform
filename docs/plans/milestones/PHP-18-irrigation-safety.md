# PHP-18 — Irrigation Safety System

## Goal

Gate `/irrigation/intent` → `/irrigation/command` with fail-safe rules before GPIO.

## Acceptance

- [x] Max duration, max daily, cooldown, wet-stop, e-stop, invalid sensor fail-safe
- [x] Relay tracking + startup/shutdown OFF
- [x] Capstone scenarios 2, 3, 5 (safety portion) unit-tested with pure logic (+ MockGPIO path via PHP-17)

## Launch

```bash
ros2 launch plant_health_irrigation safety.launch.py
```
