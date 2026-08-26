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

## 2026-08-25 — PHP-06

- Package `plant_health_cv`: HSV green segmentation pipeline + ROI/features/viz
- Publishes `/camera/image_processed` and `/plant/roi`
- Algorithm writeups in `docs/design/CV_ALGORITHMS.md`

## 2026-08-25 — PHP-07

- `ml/plant_health_data` DatasetLogger with manifests; no silent overwrite
- ROS package `plant_health_dataset` logs `/camera/image_raw` + latest sensors

## 2026-08-25 — PHP-08

- Acquisition-time sync windows (`SensorTimeBuffer`); delayed samples not silently joined
- Dataset logger records sync_status / missing / deltas in metadata

## 2026-08-25 — PHP-09

- Package `plant_health_health`: configurable rules → `/plant/health`
- Table-driven tests; dry+hot → water_stress; invalid → unknown; no GPIO

## 2026-08-25 — PHP-10

- Feature schema v1.0 + `feature_publisher` → `/plant/features`
- Golden fixture stability tests; vision + sensor keys documented

## 2026-08-25 — PHP-11

- Classical baseline RandomForest trainer + versioned joblib/meta under `ml/models/`
- Synthetic JSONL fixture path; preprocess + smoke-train tests

## 2026-08-25 — PHP-12

- Plant-group split, metrics (acc/P/R/F1/confusion), leakage gate
- Reports under `ml/evaluation/reports/`; CLI fails on intentional plant overlap

