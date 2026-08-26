# Capstone Runbook (PHP-30)

## Demo script (SIMULATION)

1. `docker compose up --build` (API+DB+UI)
2. `ros2 launch plant_health_bringup plant_health.launch.py`
3. Open UI `:8080` — confirm live SSE seq and plants/API health

## Scenarios

| # | Scenario | Expected |
|---|----------|----------|
| 1 | Healthy plant | irrigation intent OFF |
| 2 | Dry soil | stressed → safety may allow command → MockGPIO HIGH |
| 3 | Invalid sensor | safety BLOCKED (`invalid_sensor`) |
| 4 | Low ML confidence / ML-only | UNKNOWN / `ml_only_blocked` — no auto water |
| 5 | Manual irrigation | PRODUCTION requires Bearer token; max duration forces OFF |

Unit coverage: `tests/unit/test_decision.py`, `test_safety.py`, `test_e2e_smoke.py`, `test_security.py`.

## Architecture walkthrough

Prediction ≠ Decision ≠ Actuation — see ADRs 0002–0006 and `docs/design/SYSTEM_BOUNDARIES.md`.

## Known limitations

- ROS not in Docker (ADR-0006)
- Real sensor drivers still stubs
- ONNX inference backend not yet wired into ROS node
- Manual irrigation API does not yet publish ROS intent (logs event only)

## Next improvements

- Wire API manual path → `/irrigation/intent`
- Stamped sensor messages
- Full Pi HARDWARE dry-run checklist sign-off
