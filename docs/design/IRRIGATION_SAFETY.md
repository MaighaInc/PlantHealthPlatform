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

## Decision Engine (PHP-16)

Package `plant_health_decision` subscribes to `/plant/fused_health` and publishes **`/irrigation/intent`** (ADR-0003).

| Fused status | Intent |
|--------------|--------|
| healthy | `water=false` |
| stressed (rules/agree/cv) | `water=true` |
| unknown | `water=false` |
| stressed **ML-only** | `water=false` (`ml_only_blocked`) |

Decision **never** imports GPIO and **never** publishes `/irrigation/command`.

## Safety Requirements

Implemented in `plant_health_health` (`evaluate_health` + `/plant/health`).

Example:

```text
soil moisture < soil_dry_threshold AND temperature > temp_hot_threshold → water_stress
soil moisture < soil_dry_threshold → dry_soil
invalid / out-of-range sensors → UNKNOWN
else → healthy
```

Rules are configurable via YAML/ROS params (`soil_dry_threshold`, `temp_hot_threshold`), unit-tested in a table, and **not** buried in ROS callbacks. This layer does **not** command GPIO.

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
 ├── MockGPIO          (CI, simulation, development)  ← PHP-17
 └── RaspberryPiGPIO   (hardware mode)                 ← PHP-17
```

Package `plant_health_irrigation` applies `/irrigation/command` through the interface and publishes `/irrigation/status`. Safety limits are PHP-18.

## Capstone Scenarios

See [../plans/CAPSTONE_SCENARIOS.md](../plans/CAPSTONE_SCENARIOS.md) for acceptance tests covering dry soil, invalid sensors, low ML confidence, and manual irrigation.

## Related Docs

- [SYSTEM_BOUNDARIES.md](./SYSTEM_BOUNDARIES.md)
- [HARDWARE_ABSTRACTION.md](./HARDWARE_ABSTRACTION.md)
- [../plans/ROADMAP.md](../plans/ROADMAP.md) — PHP-16, PHP-17, PHP-18
