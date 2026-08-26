# PHP-04 — Sensor Abstraction

## Goal

Introduce `SensorInterface` with Virtual / Mock / Real adapters so publishers and future consumers never import device-specific code.

## Prerequisites

- PHP-03 complete

## Acceptance Criteria

- [x] `SensorInterface` ABC (`kind`, `sensor_id`, `read`)
- [x] `VirtualSensor` implements interface; `MockSensor`; `RealSensorStub`
- [x] Factory selects backend from `development_mode` / `sensor_backend`
- [x] ROS node + `sample_all()` use `SensorInterface` only
- [x] Unit tests: mock sequence, swap backends, hardware stub raises
- [x] Docs updated (HARDWARE_ABSTRACTION, milestone plan)

## Architecture Impact

```text
SensorInterface
 ├── VirtualSensor
 ├── MockSensor
 └── RealSensorStub
        ↑
   create_sensors(mode, backend)
        ↑
   sample_all() / VirtualSensorPublisherNode
```

## Tests

```bash
export PYTHONPATH=ros2_ws/src/plant_health_status:ros2_ws/src/plant_health_sensors:shared
python -m pytest tests/unit -q
```

## Intern Learning Outcomes

- What is dependency inversion?
- Why can the publisher log `type(sensor).__name__` for diagnostics but must not branch on concrete types for control flow?
