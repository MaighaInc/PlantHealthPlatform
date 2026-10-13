# Manual Test Procedures — Plant Health System (PHS)

> Step-by-step manual verification for PlantHealthPlatform after PHP-01…PHP-30  
> **Audience:** developers, interns, QA  
> **Companion:** automated tests in `tests/unit/` · [TESTING.md](../development/TESTING.md) · [CAPSTONE_RUNBOOK.md](../plans/CAPSTONE_RUNBOOK.md)

---

## 1. Purpose

These procedures verify the **integrated Plant Health System** end-to-end where automation alone is insufficient:

- ROS topic behavior on a Humble host
- Operator dashboard + API over Docker
- Capstone scenarios 1–5 (safety, ML boundaries, auth)
- Regression smoke before demos or releases

Record results using the **Test Record** template in §10.

---

## 2. Environments

| Profile | Host | ROS | GPIO | DB/API/UI |
|---------|------|-----|------|-----------|
| **A — Local unit** | Windows or any OS | No | No | Optional SQLite API |
| **B — ROS SIMULATION** | Ubuntu 22.04 / WSL2 + Humble | Yes | MockGPIO | Optional |
| **C — Full stack** | Docker host | Yes (optional `ros` profile) | MockGPIO | `docker compose` |
| **D — PRODUCTION auth** | Same as C | Optional | MockGPIO | API with `DEVELOPMENT_MODE=PRODUCTION` |

**Rules**

- Native Windows cannot run `rclpy` nodes — use WSL2 or a Linux VM for profile B/C ROS steps.
- CI never requires a physical Raspberry Pi; HARDWARE GPIO steps are optional (§8).
- Never commit secrets; use `.env.example` patterns only.

---

## 3. Prerequisites

### 3.1 Repository

```bash
git clone https://github.com/MaighaInc/PlantHealthPlatform.git
cd PlantHealthPlatform   # or PHP/ if using monorepo submodule
```

### 3.2 Python (unit / ML / API)

```bash
python -m venv .venv
# Windows
.venv\Scripts\pip install -r backend/requirements.txt -r requirements-ml.txt pytest numpy scikit-learn joblib opencv-python-headless
# Linux/macOS
source .venv/bin/activate && pip install -r backend/requirements.txt -r requirements-ml.txt pytest ...
```

On Windows, prefer a **short-path** `.venv` if ONNX install fails (path-length limit).

### 3.3 ROS 2 Humble (profiles B/C)

```bash
source /opt/ros/humble/setup.bash
cd ros2_ws
colcon build --symlink-install
source install/setup.bash
```

### 3.4 Docker (profile C — ROS in container)

```bash
docker build -f ros2_ws/Dockerfile -t phs-ros2 .
docker run --rm -it phs-ros2
# or: docker compose --profile ros up --build ros
```

Use `docker exec` for topic inspection while the container runs (see README).

### 3.5 Docker full stack (API + UI + optional ROS)

```bash
docker compose up --build
# API http://localhost:8000  UI http://localhost:8080  Postgres :5432

docker compose --profile full up --build
# Adds ROS SIMULATION service alongside db/api/web
```

---

## 4. Profile A — Hardware-free (no ROS)

**Goal:** Confirm pure-Python logic and API without `rclpy`.

| ID | Step | Command / action | Expected result | Pass |
|----|------|------------------|-----------------|------|
| A-01 | Unit suite | `bash scripts/dev/run_unit_tests.sh` | All tests pass (121+); no errors | ☐ |
| A-02 | ML baseline train | `export PYTHONPATH=ml && python ml/training/train_baseline.py --version 1.0.0` | Writes `ml/models/plant-health-classifier-1.0.0.joblib` | ☐ |
| A-03 | ML evaluation | `python ml/evaluation/run_evaluation.py` | Report under `ml/evaluation/reports/`; exit 0 | ☐ |
| A-04 | Leakage gate | Intentionally poison split in unit test | `test_leakage_detector_catches_duplicate_plant_split` passes in CI | ☐ |
| A-05 | DL export (optional) | `python ml/training/train_dl.py --version 1.0.0` | `.onnx` + `.pt` under `ml/models/` | ☐ |
| A-06 | DB migrate + seed | `cd backend && export PYTHONPATH=. && export DATABASE_URL=sqlite+pysqlite:///./phs_test.db && python -m app.db.migrate upgrade && python -m app.db.seed` | `seeded plant id=…` printed | ☐ |
| A-07 | API smoke | `uvicorn app.main:app --port 8000` then open `http://localhost:8000/docs` | OpenAPI loads; `GET /health` → `{"ok":true}` | ☐ |
| A-08 | API plants CRUD | `POST /api/plants` then `GET /api/plants` via Swagger or curl | 201 then list contains plant | ☐ |

---

## 5. Profile B — ROS SIMULATION smoke

**Goal:** Verify each ROS layer publishes expected topics.

Start unified bringup (recommended):

```bash
source /opt/ros/humble/setup.bash
source ros2_ws/install/setup.bash
ros2 launch plant_health_bringup plant_health.launch.py
```

Or launch packages individually for isolated debugging (see README).

### 5.1 Topic presence

| ID | Step | Command | Expected | Pass |
|----|------|---------|----------|------|
| B-01 | Node list | `ros2 node list` | Includes `status_publisher`, `status_subscriber`, `virtual_sensor_publisher`, `camera_publisher`, `cv_pipeline`, `feature_publisher`, `health_engine`, `plant_health_inference`, `plant_health_fusion`, `plant_health_decision`, `plant_health_safety`, `plant_health_irrigation` (no `dataset_logger` in unified bringup) | ☐ |
| B-02 | Topic list | `ros2 topic list` | All topics in §5.2 exist | ☐ |

### 5.2 Topic functional checks

Run each echo/hz in a **separate terminal** while bringup is running.

| Topic | Check command | Expected payload / rate | Pass |
|-------|---------------|-------------------------|------|
| `/system/status` | `ros2 topic echo /system/status --once` | `state=…;seq=…;source=…;ts=…` | ☐ |
| `/soil/moisture` | `ros2 topic echo /soil/moisture --once` | Finite float (not NaN in normal SIMULATION) | ☐ |
| `/camera/image_raw` | `ros2 topic hz /camera/image_raw` | Non-zero rate in SIMULATION | ☐ |
| `/camera/image_processed` | `ros2 topic hz /camera/image_processed` | Non-zero rate | ☐ |
| `/plant/health` | `ros2 topic echo /plant/health --once` | `status=healthy\|stressed\|unknown;score=…` | ☐ |
| `/plant/features` | `ros2 topic echo /plant/features --once` | JSON with `"schema_version":"1.0"` and `features` object | ☐ |
| `/plant/disease_prediction` | `ros2 topic echo /plant/disease_prediction --once` | JSON with `prediction`, `confidence`, `model_name`, `latency_ms` | ☐ |
| `/plant/fused_health` | `ros2 topic echo /plant/fused_health --once` | JSON with `status`, `precedence`, `sources` | ☐ |
| `/irrigation/intent` | `ros2 topic echo /irrigation/intent --once` | JSON `"water": true\|false`, `"actuates": false` | ☐ |
| `/irrigation/command` | `ros2 topic echo /irrigation/command --once` | JSON from safety gate `"gated_by":"safety"` | ☐ |
| `/irrigation/status` | `ros2 topic echo /irrigation/status --once` | JSON relay `pin_state` low/high | ☐ |

### 5.3 Parameter override smoke

| ID | Step | Command | Expected | Pass |
|----|------|---------|----------|------|
| B-03 | Faster heartbeat | `ros2 launch plant_health_status status.launch.py publish_period_sec:=0.5` | `/system/status` updates ~2 Hz | ☐ |
| B-04 | Invalid sensors | `ros2 launch plant_health_sensors virtual_sensors.launch.py invalid_probability:=0.5` | Occasional NaN on `/soil/moisture`; health/safety eventually fail-safe | ☐ |
| B-05 | Inference mock | `ros2 launch plant_health_inference inference.launch.py backend:=mock` | Predictions on `/plant/disease_prediction` without model file | ☐ |
| B-06 | Inference joblib | `ros2 launch plant_health_inference inference.launch.py backend:=joblib model_path:=/abs/path/ml/models/plant-health-classifier-1.0.0.joblib` | Predictions include `plant-health-classifier` version | ☐ |

---

## 6. Profile C — Full stack (Docker + ROS)

**Goal:** Operator can see live system state in browser while ROS runs on host.

| ID | Step | Action | Expected | Pass |
|----|------|--------|----------|------|
| C-01 | Start server tier | `docker compose up --build` | `api`, `web`, `db` healthy | ☐ |
| C-02 | API health | `curl http://localhost:8000/health` | `{"ok":true}` | ☐ |
| C-03 | System status | `curl http://localhost:8000/api/system/status` | JSON `status`, `database`, `mode` | ☐ |
| C-04 | Create plant | `POST /api/plants` via Swagger `:8000/docs` | 201 + plant id | ☐ |
| C-05 | Dashboard | Open `http://localhost:8080` | Dashboard loads; plant list visible | ☐ |
| C-06 | SSE live | Watch dashboard header for `live #N` incrementing | Sequence increases every ~2s (ADR-0005) | ☐ |
| C-07 | Irrigation page | Navigate to **Irrigation** | Events list loads (may be empty) | ☐ |
| C-08 | ML page | Navigate to **ML** | Model registry entries visible after seed | ☐ |
| C-09 | ROS + UI together | Run bringup (§5) while Docker up | No port conflicts; UI still loads | ☐ |

**Note:** ROS→DB bridge is not fully wired; dashboard reflects **API/DB** state, not live ROS topics unless ingested separately.

---

## 7. Capstone scenarios (manual ROS + logic)

These map to [CAPSTONE_RUNBOOK.md](../plans/CAPSTONE_RUNBOOK.md). Use SIMULATION unless noted.

### Scenario 1 — Healthy plant → irrigation OFF

| Step | Action | Expected |
|------|--------|----------|
| 1 | Run bringup with nominal virtual sensors (default) | `/plant/health` → `status=healthy` |
| 2 | Observe `/plant/fused_health` | `"status":"healthy"` |
| 3 | Observe `/irrigation/intent` | `"water":false` |
| 4 | Observe `/irrigation/command` | `"water":false` |
| 5 | Observe `/irrigation/status` | `pin_state` = `low` (MockGPIO) |

**Pass:** ☐

### Scenario 2 — Dry soil → irrigation required (via safety)

| Step | Action | Expected |
|------|--------|----------|
| 1 | Launch sensors with dry bias or wait for low `/soil/moisture` (< 30) and warm temp | `/plant/health` → `stressed` / `water_stress` or `dry_soil` |
| 2 | Confirm fusion agrees (rules + ML or rules-only) | `/plant/fused_health` → `"status":"stressed"` |
| 3 | Confirm intent | `/irrigation/intent` → `"water":true` |
| 4 | Confirm safety allows (valid soil reading, not wet, not in cooldown) | `/irrigation/command` → `"water":true` |
| 5 | Confirm actuator | `/irrigation/status` → `pin_state` = `high` |

**Pass:** ☐

### Scenario 3 — Invalid sensor → BLOCKED

| Step | Action | Expected |
|------|--------|----------|
| 1 | `ros2 launch plant_health_sensors virtual_sensors.launch.py invalid_probability:=1.0` (or publish NaN manually) | `/soil/moisture` invalid |
| 2 | Observe safety output | `/irrigation/command` → `"water":false`, reason contains `invalid_sensor` |
| 3 | Confirm relay OFF | `/irrigation/status` → `low` |

**Pass:** ☐

### Scenario 4 — Low ML confidence / ML-only → no auto water

| Step | Action | Expected |
|------|--------|----------|
| 1 | `ros2 launch plant_health_inference inference.launch.py backend:=mock mock_label:=stressed mock_confidence:=0.2` | Low confidence predictions |
| 2 | Ensure rules say healthy (nominal sensors) | Fusion may be `unknown` (conflict) or stressed ML-only |
| 3 | Observe decision | `/irrigation/intent` → `"water":false` with reason `unknown_blocks_irrigation` or `ml_only_blocked` |
| 4 | Confirm no GPIO ON | `/irrigation/status` → `low` |

**Pass:** ☐

### Scenario 5 — Manual irrigation + max duration

| Step | Action | Expected |
|------|--------|----------|
| 1 | **API (DEVELOPMENT):** `POST /api/irrigation/manual` `{"water":true,"reason":"manual_test"}` | 201 event in DB; *does not yet publish ROS intent* (known limitation) |
| 2 | **ROS path:** Publish intent manually: `ros2 topic pub /irrigation/intent std_msgs/String "{data: '{\"water\":true,\"reason\":\"manual_test\"}'}" --once` | Safety evaluates |
| 3 | With valid dry soil, confirm command ON | `/irrigation/command` water true briefly |
| 4 | Wait > `max_duration_sec` (default 30s) | Safety forces OFF (`max_duration`) |
| 5 | **PRODUCTION auth:** Set `DEVELOPMENT_MODE=PRODUCTION` and `PHS_API_TOKEN=secret` on API | `POST /api/irrigation/manual` without Bearer → **401** |
| 6 | Retry with `Authorization: Bearer secret` | **201** |

**Pass:** ☐

---

## 8. Optional — HARDWARE (Raspberry Pi)

Only when Pi + sensors + relay are available. See [EDGE_DEPLOYMENT.md](../development/EDGE_DEPLOYMENT.md).

| ID | Step | Expected | Pass |
|----|------|----------|------|
| H-01 | `DEVELOPMENT_MODE=HARDWARE`, `gpio_backend:=rpi` | `RaspberryPiGPIO` used; **not** MockGPIO | ☐ |
| H-02 | Safety still blocks invalid sensor | No relay ON on NaN soil | ☐ |
| H-03 | E-stop param | `ros2 param set /plant_health_safety e_stop true` → command water false | ☐ |
| H-04 | Shutdown | Ctrl+C bringup | Relay commanded OFF on cleanup | ☐ |

---

## 9. Regression checklist (before release / demo)

| Check | Command / action | Pass |
|-------|------------------|------|
| Unit tests green | `bash scripts/dev/run_unit_tests.sh` | ☐ |
| GitHub Actions CI | Push to `main`; workflow **CI** green | ☐ |
| No GPIO in decision package | Grep / unit test `test_decision_package_never_imports_gpio` | ☐ |
| Prediction ≠ actuation | ML/inference nodes never import GPIO (architecture review) | ☐ |
| ADR index current | `docs/architecture/adr/README.md` lists 0001–0006 | ☐ |
| Milestone table | `docs/plans/milestones/README.md` PHP-01…30 Complete | ☐ |

---

## 10. Test record template

Copy for each session:

```text
Date:
Tester:
Environment: A / B / C / D / H
Git commit:
ROS distro: Humble (Y/N)
Docker: Y/N

Results:
  A-01 … A-08:
  B-01 … B-06:
  C-01 … C-09:
  Capstone 1–5:
  Regression:

Failures (steps, observed, expected, notes):

Sign-off: PASS / FAIL / PASS WITH KNOWN ISSUES
```

---

## 11. Known limitations (manual expectations)

Do **not** fail tests for these unless product requirements change:

| Item | Current behavior |
|------|------------------|
| ROS in Docker | Optional `phs-ros2` image / compose `--profile ros`; host/WSL still preferred for HARDWARE |
| API manual → ROS | Manual API logs DB event; does not publish `/irrigation/intent` |
| ONNX in ROS inference | Export exists; node uses `mock` or `joblib` only |
| Real sensor drivers | `RealSensorStub` on HARDWARE until drivers land |
| Stamped sensors | Float32 topics; no acquisition stamp in message |
| Live ROS on dashboard | SSE heartbeat only; plant health from API/DB |

---

## 12. Related documents

| Document | Use |
|----------|-----|
| [TESTING.md](../development/TESTING.md) | Automated test strategy |
| [CAPSTONE_RUNBOOK.md](../plans/CAPSTONE_RUNBOOK.md) | Demo script |
| [IRRIGATION_SAFETY.md](../design/IRRIGATION_SAFETY.md) | Safety rules reference |
| [ROS_ARCHITECTURE.md](../design/ROS_ARCHITECTURE.md) | Topic catalog |
| [API.md](../design/API.md) | REST endpoint list |
| [EDGE_DEPLOYMENT.md](../development/EDGE_DEPLOYMENT.md) | Pi bringup |
