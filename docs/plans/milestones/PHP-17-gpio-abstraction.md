# PHP-17 — GPIO Abstraction

## Goal

Introduce `GPIOInterface` with `MockGPIO` / `RaspberryPiGPIO` and drive the irrigation relay only through that interface.

## Prerequisites

- PHP-16 irrigation intent (decision never imports GPIO)

## Acceptance Criteria

- [x] `GPIOInterface`, `MockGPIO` (records pin transitions), `RaspberryPiGPIO`
- [x] Factory: SIMULATION/DEVELOPMENT → MockGPIO exclusively (refuses `backend=rpi`)
- [x] Irrigation node uses `GPIOInterface` only → `/irrigation/status`
- [x] Unit tests prove transition recording and mode exclusivity

## Launch

```bash
ros2 launch plant_health_irrigation irrigation.launch.py development_mode:=SIMULATION
```

## Notes

Safety limits (max duration, e-stop, etc.) arrive in PHP-18. This node applies already-authorized `/irrigation/command` messages to the relay pin.
