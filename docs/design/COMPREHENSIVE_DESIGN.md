# PlantHealthPlatform — Comprehensive System Design

> **Authority:** Consolidated design specification synthesizing all concepts in `docs/`.  
> **Product:** PlantHealthPlatform (PHP) → Plant Health System (PHS)  
> **Last updated:** August 2026  
> **Companion:** [../plans/IMPLEMENTATION_PLAN.md](../plans/IMPLEMENTATION_PLAN.md)

This document is the **unified design reference**. Topic-specific deep-dives remain under `docs/design/` and are authoritative for their subsystem details. When this document and a deep-dive diverge, prefer the deep-dive for that subsystem and update this document to match.

---

## 1. Purpose and Scope

### 1.1 Mission

Build one modular **Plant Health Monitoring, Plant Intelligence, and Automated Irrigation Platform** that combines:

| Domain | Responsibility |
|--------|----------------|
| Robotics | ROS 2 orchestration, sensors, camera, GPIO, Raspberry Pi edge |
| Computer Vision | OpenCV acquisition, segmentation, features, quality gates |
| Machine Learning | Dataset → train → evaluate → version → infer (progressive complexity) |
| Application platform | PostgreSQL, REST API, React dashboard |
| Operations | Docker, CI/CD, logging, metrics, security, hardware-free tests |

### 1.2 Naming

| Term | Meaning |
|------|---------|
| **PlantHealthPlatform (PHP)** | Software platform and repository |
| **Plant Health System (PHS)** | Integrated running system |
| `plant_health_*` | ROS/Python package namespace |
| Do **not** use `php_*` | Conflicts with the PHP programming language |

### 1.3 Core Principle

There are **not** 30 independent projects. There is **one product** extended by ~30 milestones (`PHP-01` … `PHP-30`). Every change inspects, reuses, extends, integrates, tests, documents, and regresses.

Prefer:

```text
small implementation + clear architecture + tests + documentation + review
```

over large unexplained applications.

### 1.4 Capstone Outcome

```text
Sensors → Camera → ROS 2 → OpenCV → Features → ML → Health → Fusion
  → Decision → Safety → GPIO → Backend → PostgreSQL → Dashboard
```

Acceptance scenarios: [../plans/CAPSTONE_SCENARIOS.md](../plans/CAPSTONE_SCENARIOS.md).

---

## 2. System Architecture

### 2.1 Three Pillars → One System

```text
                         PLANTHEALTHPLATFORM (PHP)
                                    │
         ┌──────────────────────────┼──────────────────────────┐
         │                          │                          │
         ▼                          ▼                          ▼
      ROBOTICS                   AI / ML                   PLATFORM
      ROS 2                      OpenCV                    Backend
      Sensors                    Classical ML              PostgreSQL
      Camera                     Deep Learning             REST API
      GPIO / Edge                Inference                 React Dashboard
         │                          │                          │
         └──────────────────────────┼──────────────────────────┘
                                    ▼
                         PLANT HEALTH SYSTEM (PHS)
                                    │
                    ┌───────────────┴───────────────┐
                    ▼                               ▼
              EDGE DEVICE                      SERVER / CLOUD
           (Raspberry Pi)                   (API + Database)
                    │                               │
                    └───────────────┬───────────────┘
                                    ▼
                           Plant Dashboard
```

### 2.2 Module Boundaries

| Module | Owns | Must not own |
|--------|------|--------------|
| ROS | Communication / orchestration | Business persistence schema |
| Hardware | Physical device access via interfaces | Decision policy |
| CV | Image processing and features | Actuation, training |
| ML | Training / evaluation / inference | GPIO, frontend |
| Health Engine | Plant-health interpretation | Direct pump control |
| Decision Engine | Operational irrigation decisions | Raw GPIO registers |
| Safety Layer | Actuator protection rules | Model training |
| GPIO | Physical actuation | Health diagnosis |
| Backend | Persistence / API | ROS node internals |
| Frontend | Visualization / UX | Direct hardware access |

Do not collapse all functionality into one application.

### 2.3 Critical Separation: Prediction ≠ Decision ≠ Actuation

**Mandatory.**

| Layer | Example output |
|-------|----------------|
| ML (Prediction) | "Plant appears stressed." |
| Decision Engine | "Irrigation may be appropriate." |
| Safety Layer | "Conditions permit irrigation." |
| GPIO (Actuation) | "Activate pump." |

**Rules:**

- ML inference must **never** directly activate irrigation.
- Sensors must **not** secretly control unrelated components.
- Decision engine consumes **explicit** fused inputs (sensors, CV, ML, rules).

### 2.4 Deployment Topology

| Tier | Components |
|------|------------|
| **Edge** | ROS 2 nodes, sensors, camera, CV, inference, decision, safety, GPIO |
| **Server** | FastAPI (or Node) backend, PostgreSQL, auth, persistence bridge |
| **Client** | React dashboard (browser) |

ROS may run on the host when containerization blocks device access. Backend, frontend, and PostgreSQL are containerization candidates (PHP-23).

### 2.5 Technology Stack (summary)

| Area | Primary | Secondary / notes |
|------|---------|-------------------|
| Middleware | ROS 2 Humble or Iron | ADR when chosen |
| Language | Python 3.10+ (`rclpy`) | C++ / `rclcpp` only when justified |
| CV | OpenCV, NumPy, `cv_bridge` | — |
| ML | Rules → scikit-learn → PyTorch/TF → ONNX | Progressive |
| Backend | FastAPI + Pydantic + SQLAlchemy | Or Node/TS + Prisma |
| Frontend | React + TypeScript + Vite | TanStack Query |
| DB | PostgreSQL + migrations | — |
| Edge | Raspberry Pi | Mock/virtual for CI |
| Ops | Docker Compose, GitHub Actions | Prometheus/Grafana later |

Full detail: [../architecture/TECH_STACK.md](../architecture/TECH_STACK.md).

---

## 3. Repository and Package Design

### 3.1 Single Repository

```text
PlantHealthPlatform/
├── ros2_ws/src/
│   ├── plant_health_status/
│   ├── plant_health_sensors/
│   ├── plant_health_camera/
│   ├── plant_health_cv/
│   ├── plant_health_ml/           # messaging / shared ML types if needed
│   ├── plant_health_inference/
│   ├── plant_health_decision/
│   ├── plant_health_irrigation/
│   └── plant_health_bringup/
├── backend/
├── frontend/
├── ml/          # datasets, notebooks, training, evaluation, models, inference libs
├── edge/        # gpio, hardware adapters, edge deployment
├── shared/
├── tests/       # unit, integration, e2e
├── docs/
├── scripts/
├── docker/
├── deployment/
├── .github/workflows/
├── docker-compose.yml
└── .env.example
```

Create directories **when needed**, not to match the diagram early.

Detail: [../plans/REPOSITORY_STRUCTURE.md](../plans/REPOSITORY_STRUCTURE.md).

### 3.2 Bringup

```bash
ros2 launch plant_health_bringup plant_health.launch.py
```

Mode-dependent launch of: camera, sensors, CV, inference, health, decision, irrigation, diagnostics. Parameters remain configurable.

---

## 4. ROS 2 Design

### 4.1 Topic Architecture (canonical examples)

```text
/system/status
/environment/temperature
/environment/humidity
/environment/pressure
/environment/light
/soil/moisture
/camera/image_raw
/camera/image_processed
/plant/roi
/plant/features
/plant/health
/plant/disease_prediction
/irrigation/command
/irrigation/status
/diagnostics
```

Before adding a topic: inspect existing topics → reuse if possible → follow naming → document.

### 4.2 Message Design

Prefer standard messages (`std_msgs`, `sensor_msgs`, `geometry_msgs`, `example_interfaces`).

Custom messages only when justified. Example:

```text
PlantHealth.msg
  float32 health_score
  string health_status          # healthy | stressed | unknown | ...
  string disease                # optional / empty
  float32 confidence
  builtin_interfaces/Time timestamp
```

Before custom messages: document why standards fail, required fields, and compatibility impact.

### 4.3 Node Responsibilities

| Package / node | Responsibility |
|----------------|----------------|
| `plant_health_status` | System heartbeat / status |
| `plant_health_sensors` | Publish environment and soil readings via `SensorInterface` |
| `plant_health_camera` | Capture, validate frames, publish `image_raw` |
| `plant_health_cv` | Process images → ROI, features, visualization |
| `plant_health_inference` | Load versioned model; publish predictions |
| Health (rules or fusion) | Interpret sensors/features/ML into health state |
| `plant_health_decision` | Propose irrigation intent |
| `plant_health_irrigation` | Safety + GPIO command/status |
| `plant_health_bringup` | Unified launch |

### 4.4 Logging

ROS nodes use ROS logging — not scattered `print()` in production paths.

Detail: [ROS_ARCHITECTURE.md](./ROS_ARCHITECTURE.md).

---

## 5. Hardware Abstraction and Modes

### 5.1 Principle

Hardware must **not** dominate application architecture. Business and decision code talk to interfaces.

### 5.2 Sensor Interface

```text
SensorInterface
 ├── VirtualSensor       # SIMULATION — noise, outliers, invalid values
 ├── MockSensor           # deterministic unit/integration tests
 └── RealSensorAdapter   # BME280, DHT, soil probes, etc.
```

```python
reading = sensor.read()  # never raw I2C in decision/health logic
```

Virtual sensors (PHP-03) support: soil, temperature, humidity, light, CO₂; configurable rate, bounds, noise, invalid injection.

### 5.3 GPIO Interface

```text
GPIOInterface
 ├── MockGPIO
 └── RaspberryPiGPIO
```

### 5.4 Development Modes

| Mode | Sensors | Camera | GPIO | Auth |
|------|---------|--------|------|------|
| **SIMULATION** | virtual | sample images | MockGPIO | minimal / off |
| **DEVELOPMENT** | virtual/mock | USB | MockGPIO | minimal / off |
| **HARDWARE** | real | real | RaspberryPiGPIO | optional |
| **PRODUCTION** | real | real | hardened + auth | **required** |

CI must never require a physical Raspberry Pi.

Detail: [HARDWARE_ABSTRACTION.md](./HARDWARE_ABSTRACTION.md), [../development/DEVELOPMENT_MODES.md](../development/DEVELOPMENT_MODES.md).

---

## 6. Data Pipeline

### 6.1 End-to-End Flow

```text
Sensors ──► ROS 2 ──┬──► Database (persist)
                    │
Camera ──► OpenCV ──► Features ──► ML ──► Plant Health
                                              │
                                    Fusion / Decision / Safety
```

### 6.2 Timestamp Rules

- Timestamp at **acquisition**, not only at message arrival.
- Never assume `message arrival time == measurement time`.
- Synchronization (PHP-08) uses windows; handles missing/delayed data and clock skew.

### 6.3 Data Separation

```text
Raw Data → Validated → Processed → Features → Training Dataset → Model
```

Never silently overwrite raw data.

### 6.4 Dataset Management

```text
dataset/
├── images/
├── labels/
├── metadata/
└── manifests/
```

Reproducible, manifest-driven splits — not manual filenames.

### 6.5 Canonical Observation Record (evolving)

```json
{
  "image": "images/plant_001_000123.jpg",
  "plant_id": "plant-001",
  "timestamp": "2026-08-25T18:30:00Z",
  "soil_moisture": 41.2,
  "temperature": 27.8,
  "humidity": 63.4,
  "light": 812,
  "label": "healthy"
}
```

Schema may evolve; do not freeze prematurely.

### 6.6 Sensor Fusion Inputs

```text
soil moisture + temperature + humidity + light
  + camera features + ML prediction
  → unified health / decision representation
```

Detail: [DATA_PIPELINE.md](./DATA_PIPELINE.md).

---

## 7. Computer Vision Design

### 7.1 Pipeline Stages

```text
Raw Image → Validation → Resize → Noise Reduction → Color Conversion
  → Plant Segmentation → ROI Extraction → Feature Extraction → Visualization
```

### 7.2 Progressive Capabilities

Acquisition, validation, resize, color-space (HSV), thresholding, morphology, contours, leaf segmentation, background removal, ROI, features, normalization, augmentation, quality assessment.

### 7.3 Feature Candidates

```text
leaf_area, green_pixel_ratio, mean_hue, mean_saturation, mean_value,
contour_area, bounding_box, centroid
```

Plus sensor-derived features at fusion time (PHP-10 / PHP-15).

### 7.4 Camera Subsystem

- USB (and later Pi camera) acquisition via ROS
- Configurable resolution / FPS
- Failure, drop, and invalid-frame detection
- Correct resource release and practical reconnection
- `cv_bridge` for ROS image transport

### 7.5 Learning / Documentation Requirement

For each important CV algorithm document: Problem, Algorithm, Selection reason, Parameters, Sensitivity, Limitations, Alternatives, Tradeoffs. No unexplained `cv2.*` usage.

Detail: [CV_PIPELINE.md](./CV_PIPELINE.md).

---

## 8. Machine Learning Design

### 8.1 Complexity Progression

| Stage | Approach |
|-------|----------|
| 1 | Rule-based health logic |
| 2 | Classical CV features |
| 3 | Classical ML (Logistic Regression, Trees, RF, SVM, Gradient Boosting) |
| 4 | Deep learning (PyTorch / TensorFlow) + ONNX / ONNX Runtime |

Do **not** jump to deep learning without a working baseline and justification.

### 8.2 ML Lifecycle Separation

```text
Dataset → Training → Evaluation → Model Registry/Version → Inference → Prediction
```

Production inference nodes **must not** train models.

### 8.3 Data Quality Gate

Reject before training: missing data, corrupted/blurry/over/underexposed images, duplicates, bad labels, sensor anomalies, timestamp mismatches.

### 8.4 Leakage Prevention

Check: duplicate images, same plant in train and test, temporal leakage, preprocessing leakage, label leakage, train/test contamination. Splits must be scientifically defensible.

### 8.5 Model Versioning

Every inference identifies:

```json
{
  "model_name": "plant-health-classifier",
  "model_version": "1.2.0",
  "prediction": "stressed",
  "confidence": 0.91,
  "timestamp": "..."
}
```

No ambiguous filenames (`final_final_v2.pt`).

### 8.6 UNKNOWN State

If `confidence < threshold` → `UNKNOWN`. Do not force a diagnosis; do not drive automatic irrigation from ML alone when UNKNOWN.

### 8.7 Inference Node Contract

1. Subscribe to images (and/or features as designed)  
2. Validate → preprocess → infer  
3. Emit prediction, confidence, model version, latency  
4. Handle failures safely (no silent wrong actuation)  

Must **not**: train, manipulate GPIO, own DB schema, control frontend.

### 8.8 Evaluation Metrics

Accuracy, precision, recall, F1, confusion matrix, latency, model size, CPU/memory; ROC-AUC / PR-AUC when imbalanced.

Detail: [ML_PIPELINE.md](./ML_PIPELINE.md).

---

## 9. Health, Decision, and Irrigation Safety

### 9.1 Rule-Based Health (pre-ML)

Example:

```text
soil_moisture < threshold AND temperature > threshold → water_stress
```

Rules: configurable, testable, documented — not buried in ROS callbacks.

### 9.2 Control Flow

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

### 9.3 Safety Requirements

| Control | Behavior |
|---------|----------|
| Max watering duration | Hard cut-off |
| Max daily watering | Cap total water time/volume |
| Cooldown | Minimum interval between events |
| Min soil moisture | Do not water if already wet enough |
| Manual override | Authorized path only |
| Emergency stop | Immediate OFF |
| Invalid sensors | **FAIL SAFE** — block irrigation, alert |
| Relay state tracking | Known ON/OFF |
| Startup / shutdown | Safe default (OFF) |

Never water indefinitely.

### 9.4 Capstone Behaviors

| Scenario | Expected |
|----------|----------|
| Healthy plant | health=healthy, irrigation OFF |
| Dry soil | stressed / irrigation required (then safety) |
| Invalid sensor | INVALID, irrigation BLOCKED, alert |
| Low ML confidence | UNKNOWN; ML-only auto-irrigation BLOCKED |
| Manual irrigation | auth → safety → ON → log → max duration → OFF |

Detail: [IRRIGATION_SAFETY.md](./IRRIGATION_SAFETY.md).

---

## 10. Database Design

### 10.1 Policy

- PostgreSQL with migrations only (no manual production schema edits).
- Access via Repository layer — never Prisma/SQLAlchemy in HTTP handlers without service layer.
- Schema evolves with milestones; do not over-normalize early.

### 10.2 Planned Entities

```text
plants
plant_varieties
devices
sensors
sensor_readings
images
image_metadata
plant_observations
health_predictions
ml_models
inference_results
irrigation_events
alerts
users
system_events
```

### 10.3 Conceptual Relationships

```text
plant_varieties 1──* plants
plants 1──* images / plant_observations / health_predictions / irrigation_events
devices 1──* sensors
sensors 1──* sensor_readings
ml_models 1──* inference_results
users (auth) ──► authorized irrigation_events / system_events
alerts ← sensors | safety | system
```

### 10.4 Backend Layering

```text
API / Controller → Service → Repository → Database
```

Detail: [DATABASE.md](./DATABASE.md).

---

## 11. REST API Design

### 11.1 Planned Endpoints

```text
GET    /api/plants
GET    /api/plants/{id}
GET    /api/sensors
GET    /api/sensors/{id}/readings
GET    /api/plants/{id}/health
GET    /api/plants/{id}/images
GET    /api/irrigation/events
POST   /api/irrigation/manual
GET    /api/models
GET    /api/system/status
GET    /health                    # readiness / liveness (observability)
```

### 11.2 Cross-Cutting Requirements

- Request validation (Pydantic or equivalent)
- Meaningful status codes and structured errors
- Pagination and filtering
- Timestamps on time-series payloads
- Authentication / authorization (PHP-27), especially actuators

### 11.3 Stack Choice

**Preferred:** FastAPI + Pydantic + SQLAlchemy + PostgreSQL  
**Alternative:** Node.js + TypeScript + Express/Fastify + Prisma  

Record the choice as an ADR.

Detail: [API.md](./API.md).

---

## 12. Frontend Design

### 12.1 Stack and Structure

React + TypeScript + Vite; TanStack Query (or equivalent).

```text
components/  features/  hooks/  services/  pages/  types/  utils/
```

Avoid giant components and unjustified `any`. Explicit API contract types.

### 12.2 Pages

| Page | Content |
|------|---------|
| Dashboard | Plant counts, healthy/stressed, sensor/irrigation status, alerts |
| Plant Detail | Image, health score/status, ML prediction/confidence, sensors, charts |
| Irrigation | Relay state, events, manual controls, safety state |
| ML | Model version, inference stats, prediction history, confidence distribution |

### 12.3 Real-Time (PHP-22)

Evaluate before implementing: polling vs WebSockets vs SSE vs ROS bridge. Document tradeoffs in an ADR.

Detail: [FRONTEND.md](./FRONTEND.md).

---

## 13. Configuration

Never hard-code environment-specific values. Never commit secrets.

Sources: `.env` / `.env.example`, `config.yaml`, ROS parameters, launch args.

Example keys:

```text
DATABASE_URL
MODEL_PATH
CAMERA_INDEX, CAMERA_WIDTH, CAMERA_HEIGHT, CAMERA_FPS
SOIL_THRESHOLD
IRRIGATION_MAX_SECONDS
LOG_LEVEL
DEVELOPMENT_MODE          # SIMULATION | DEVELOPMENT | HARDWARE | PRODUCTION
```

Detail: [../development/CONFIGURATION.md](../development/CONFIGURATION.md).

---

## 14. Observability and Performance

### 14.1 Near-Term

Structured logs; diagnostic error messages; ROS logging in nodes.

### 14.2 Progressive (PHP-26)

Health endpoints, ROS `/diagnostics`, sensor freshness, inference/API latency, irrigation audit trail, error counters.

### 14.3 Future (justified later)

Prometheus, Grafana, Loki, Alertmanager.

### 14.4 Performance Baselines (measure before optimize)

Camera FPS, ROS rates, CV/ML latency, API/DB latency, memory, CPU, model size.

Detail: [../development/OBSERVABILITY.md](../development/OBSERVABILITY.md).

---

## 15. Security Design

| Concern | Requirement |
|---------|-------------|
| AuthN / AuthZ | Required in PRODUCTION; actuator paths always authorized |
| Input validation | All API and file uploads |
| Secrets | Env / secret manager only |
| CORS | Explicit allowlist in production |
| Models | Path/version validation; reject untrusted models |
| Images | Size/type limits; safe processing |
| Actuators | Never expose GPIO without auth |

Manual irrigation:

```text
authorization → safety validation → relay ON → event logged → max duration → relay OFF
```

Detail: [../development/SECURITY.md](../development/SECURITY.md).

---

## 16. Testing and Quality

### 16.1 Levels

| Level | Examples |
|-------|----------|
| Unit | Sensor conversion, CV, features, ML preprocess, decision/safety, services |
| Integration | ROS↔ROS, API↔DB, backend↔ML |
| E2E | Full pipeline with MockGPIO / VirtualSensor / sample images |

### 16.2 Hardware-Free CI

`MockGPIO` + `VirtualSensor` + simulated camera. Same interfaces as hardware.

### 16.3 Regression

`New tests + existing tests + integration` before milestone sign-off.

Detail: [../development/TESTING.md](../development/TESTING.md).

---

## 17. Engineering Process (design constraints)

| Concern | Design impact |
|---------|---------------|
| ADRs | Record irreversible / multi-subsystem choices under `docs/architecture/adr/` |
| Scope | No drive-by refactors; dependency justification required |
| Education | Each milestone teaches a concept; intern must explain build/why/integrate/fail/test/deploy |
| Progressive assistance | Concept → architecture → skeleton → hint → partial → reference |

Process docs: [../development/AGENT_WORKFLOW.md](../development/AGENT_WORKFLOW.md), [../development/CODING_STANDARDS.md](../development/CODING_STANDARDS.md), [../development/MILESTONE_COMPLETION.md](../development/MILESTONE_COMPLETION.md), [../prompt/MASTER_PROMPT.md](../prompt/MASTER_PROMPT.md).

---

## 18. Concept Coverage Map

| Concept | Primary design section | Deep-dive / plan |
|---------|------------------------|------------------|
| Product vision / one system | §1 | PRODUCT_VISION |
| Architecture / boundaries | §2 | SYSTEM_ARCHITECTURE, SYSTEM_BOUNDARIES |
| Tech stack | §2.5 | TECH_STACK |
| Repo / packages | §3 | REPOSITORY_STRUCTURE |
| ROS topics / messages / bringup | §4 | ROS_ARCHITECTURE |
| Hardware abstraction / modes | §5 | HARDWARE_ABSTRACTION, DEVELOPMENT_MODES |
| Data / timestamps / fusion | §6 | DATA_PIPELINE |
| CV / camera | §7 | CV_PIPELINE |
| ML lifecycle / leakage / UNKNOWN | §8 | ML_PIPELINE |
| Decision / safety / irrigation | §9 | IRRIGATION_SAFETY |
| Database | §10 | DATABASE |
| API | §11 | API |
| Frontend / real-time | §12 | FRONTEND |
| Configuration | §13 | CONFIGURATION |
| Observability / performance | §14 | OBSERVABILITY |
| Security | §15 | SECURITY |
| Testing / CI | §16 | TESTING |
| Capstone | §1.4, §9.4 | CAPSTONE_SCENARIOS |
| Milestone delivery | — | IMPLEMENTATION_PLAN, ROADMAP |

---

## 19. Related Documents

| Document | Role |
|----------|------|
| [PRODUCT_VISION.md](./PRODUCT_VISION.md) | Mission summary |
| [SYSTEM_ARCHITECTURE.md](./SYSTEM_ARCHITECTURE.md) | High-level diagrams |
| [SYSTEM_BOUNDARIES.md](./SYSTEM_BOUNDARIES.md) | Mandatory separations |
| [../plans/IMPLEMENTATION_PLAN.md](../plans/IMPLEMENTATION_PLAN.md) | How to build this design |
| [../plans/ROADMAP.md](../plans/ROADMAP.md) | Milestone index |
| [../prompt/MASTER_PROMPT.md](../prompt/MASTER_PROMPT.md) | Agent constitution |
| [../INDEX.md](../INDEX.md) | Documentation hub |
