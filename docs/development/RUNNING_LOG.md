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

## 2026-08-25 — PHP-13

- ADR-0002: classical RF remains tabular baseline; feature MLP + ONNX for Stage-4/edge
- Train/compare/export `plant-health-mlp-1.0.0`; registry.json; ONNX Runtime smoke load
- Image CNN deferred until labeled image volume justifies it

## 2026-08-25 — PHP-14

- Package `plant_health_inference`: features → prediction JSON on `/plant/disease_prediction`
- Mock + joblib backends; confidence gate → unknown; no GPIO/training
- Scenario 4 SIMULATION path covered by unit tests

## 2026-08-25 — PHP-15

- Package `plant_health_fusion`: rules + features + ML → `/plant/fused_health`
- Conflict healthy vs stressed → unknown; decision engine has one subscription interface

## 2026-08-25 — PHP-16

- ADR-0003: `/irrigation/intent` for proposals; `/irrigation/command` reserved for safety/GPIO
- Package `plant_health_decision`: fused health → intent; ML-only / unknown blocked; no GPIO imports

## 2026-08-25 — PHP-17

- `GPIOInterface` + `MockGPIO` (transition log) + `RaspberryPiGPIO`
- Factory forces MockGPIO for SIMULATION/DEVELOPMENT; irrigation node uses interface only

## 2026-08-26 — PHP-18

- Safety gate intent→command: e-stop, invalid sensor, max duration/daily, cooldown, wet-stop; startup/shutdown OFF

## 2026-08-26 — PHP-19

- ADR-0004 FastAPI/SQLAlchemy/PostgreSQL; backend models + repositories + migrate/seed; SQLite tests

## 2026-08-26 — PHP-20

- FastAPI app with plants/sensors/health/irrigation/models/status; OpenAPI /docs; TestClient tests

## 2026-08-26 — PHP-21

- Vite/React dashboard: Dashboard, Plant Detail, Irrigation, ML pages with typed API client

## 2026-08-26 — PHP-22

- ADR-0005 SSE; /api/stream/events; dashboard EventSource live seq
