# Development Running Log

> Session notes for PlantHealthPlatform. Append after meaningful work sessions.

---

## 2026-08-25 — PHP-01 start

- Created feature branch `feature/php-01-ros-foundation`
- Accepted ADR-0001: ROS 2 Humble
- Bootstrapped `.env.example`, `pyproject.toml`, `ros2_ws/`
- Implemented `plant_health_status` publisher + subscriber on `/system/status`
- Hardware-free unit tests for heartbeat format/parse
- Native ROS not available on Windows host — full launch smoke deferred to WSL/Ubuntu Humble
- Committed as `c7b46a0`

## 2026-08-25 — PHP-02

- Branch `feature/php-02-ros-parameters`
- Strict parameter validation (`parameters.py`); invalid values fail startup
- YAML + launch overrides (`publish_period_sec`, `params_file`)
- Shared `plant_health_common` for `DEVELOPMENT_MODE` / `.env` parsing
- Unit tests for params and runtime config
- Committed as `427c69b`

## 2026-08-25 — Branching policy

- Consolidated PHP-01…PHP-03 onto `main`; deleted local/remote `feature/php-*` branches
- Future milestones commit directly on `main`

## 2026-08-25 — PHP-04

- `SensorInterface` + VirtualSensor / MockSensor / RealSensorStub
- Factory mode selection; node samples via `sample_all()` only
- Unit tests prove consumer can swap backends without device imports

## 2026-08-25 — PHP-05

- Package `plant_health_camera`: CameraInterface, Simulated/USB/Mock
- Publishes `/camera/image_raw`; validation rejects blank/invalid; drops logged
- Sample plant image for SIMULATION; USB reconnect policy documented

