# PHP-29 — End-to-End Integration

## Acceptance

- [x] `plant_health_bringup` unified launch
- [x] Prior unit suites remain green
- [x] Failure paths covered in safety/decision/fusion tests (invalid sensor, conflict unknown, ML-only block)

```bash
ros2 launch plant_health_bringup plant_health.launch.py
```
