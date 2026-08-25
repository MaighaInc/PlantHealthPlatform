# Irrigation & Safety Architecture

> Decision engine, safety layer, and actuator control

## Control Flow

```text
Sensors + CV + ML
        ↓
Decision Engine
        ↓
Safety Layer
        ↓
Irrigation Command
        ↓
GPIO
```

**ML inference must never directly activate physical irrigation.**

## Rule-Based Health (pre-ML)

Example:

```text
soil moisture < threshold AND temperature > threshold → water stress
```

Rules must be configurable, testable, and documented — not buried in ROS callbacks.

## Safety Requirements

- Maximum watering duration
- Maximum daily watering
- Cooldown period
- Minimum soil moisture threshold
- Manual override (with authorization)
- Emergency stop
- Invalid sensor handling → **FAIL SAFE**
- Relay state tracking
- Startup-safe and shutdown-safe states

If sensor data is invalid: block irrigation, generate alert, never water indefinitely.

## GPIO Abstraction

```text
GPIOInterface
 ├── MockGPIO          (CI, simulation, development)
 └── RaspberryPiGPIO   (hardware mode)
```

## Capstone Scenarios

See [../plans/CAPSTONE_SCENARIOS.md](../plans/CAPSTONE_SCENARIOS.md) for acceptance tests covering dry soil, invalid sensors, low ML confidence, and manual irrigation.

## Related Docs

- [SYSTEM_BOUNDARIES.md](./SYSTEM_BOUNDARIES.md)
- [HARDWARE_ABSTRACTION.md](./HARDWARE_ABSTRACTION.md)
- [../plans/ROADMAP.md](../plans/ROADMAP.md) — PHP-16, PHP-17, PHP-18
