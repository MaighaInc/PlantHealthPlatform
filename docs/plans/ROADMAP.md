# 30-Milestone Development Roadmap

> **Important:** These are incremental milestones of **one** PlantHealthPlatform — not independent projects.

```text
PHP-01 → PHP-02 → … → PHP-30 → Plant Health System (PHS)
```

**Master delivery plan (phases, acceptance, dependencies, risks):** [IMPLEMENTATION_PLAN.md](./IMPLEMENTATION_PLAN.md)

**Unified design reference:** [../design/COMPREHENSIVE_DESIGN.md](../design/COMPREHENSIVE_DESIGN.md)

Per-milestone working plans: [`milestones/`](./milestones/) (generated as work progresses).

---

## Phase 1 — ROS Foundation & Sensors (PHP-01 – PHP-04)

| Milestone | Title | Deliverables |
|-----------|-------|--------------|
| **PHP-01** | ROS 2 Publisher/Subscriber Foundation | Publisher, subscriber, node lifecycle, logging, topic inspection |
| **PHP-02** | ROS Parameters and Runtime Configuration | Parameters, validation, runtime inspection |
| **PHP-03** | Virtual Sensor Framework | Virtual soil/temp/humidity/light/CO2 with noise, outliers, invalid values |
| **PHP-04** | Sensor Abstraction | `SensorInterface`, Virtual/Mock/Real adapters |

---

## Phase 2 — Vision & Data (PHP-05 – PHP-10)

| Milestone | Title | Deliverables |
|-----------|-------|--------------|
| **PHP-05** | Camera Integration | USB acquisition, ROS image pub, resolution/FPS, timestamps, failure detection |
| **PHP-06** | OpenCV Processing Pipeline | Validation → resize → color → segmentation → ROI → features |
| **PHP-07** | Image Dataset Logger | Images + timestamps + plant ID + sensor context + metadata |
| **PHP-08** | Metadata Synchronization | Image/sensor/timestamp sync; handle missing/delayed data |
| **PHP-09** | Rule-Based Plant Health Engine | Configurable deterministic health rules |
| **PHP-10** | Feature Extraction | leaf_area, green_ratio, hue, saturation, brightness, shape, sensor features |

---

## Phase 3 — Machine Learning (PHP-11 – PHP-15)

| Milestone | Title | Deliverables |
|-----------|-------|--------------|
| **PHP-11** | Classical ML Baseline | Classifier: healthy / stressed / unknown |
| **PHP-12** | ML Evaluation Pipeline | Split, validation, metrics, confusion matrix, leakage detection |
| **PHP-13** | Deep Learning Classifier | PyTorch/equivalent, training, evaluation, export |
| **PHP-14** | ROS AI Inference Node | Preprocess → model → prediction + confidence + version + latency |
| **PHP-15** | Sensor Fusion | Combine vision + sensors + ML into unified health representation |

---

## Phase 4 — Irrigation & Edge (PHP-16 – PHP-18)

| Milestone | Title | Deliverables |
|-----------|-------|--------------|
| **PHP-16** | Irrigation Decision Engine | Separate prediction, decision, and actuation |
| **PHP-17** | GPIO Abstraction | `GPIOInterface`, MockGPIO, RaspberryPiGPIO |
| **PHP-18** | Irrigation Safety System | Max runtime, cooldown, e-stop, fail-safe, startup/shutdown safe |

---

## Phase 5 — Full-Stack Platform (PHP-19 – PHP-22)

| Milestone | Title | Deliverables |
|-----------|-------|--------------|
| **PHP-19** | PostgreSQL Data Layer | Migrations, repositories, persistent storage |
| **PHP-20** | REST API | Plants, sensors, health, images, irrigation, models, status |
| **PHP-21** | React Dashboard | Overview, plant detail, sensors, health, irrigation, ML |
| **PHP-22** | Real-Time Monitoring | Evaluate and implement polling/WebSocket/SSE/ROS bridge |

---

## Phase 6 — Production Readiness (PHP-23 – PHP-28)

| Milestone | Title | Deliverables |
|-----------|-------|--------------|
| **PHP-23** | Dockerization | Containerize backend, frontend, PostgreSQL; docker-compose |
| **PHP-24** | Automated Testing | Expand unit/integration/E2E; hardware mocks |
| **PHP-25** | CI/CD | Lint, type check, unit/integration tests, ROS build, ML smoke |
| **PHP-26** | Observability | Health checks, structured logs, metrics, ROS diagnostics |
| **PHP-27** | Security Hardening | Auth, authorization, secrets, upload validation, actuator auth |
| **PHP-28** | Raspberry Pi / Edge Deployment | Sensors, camera, GPIO, inference, networking on edge hardware |

---

## Phase 7 — Integration & Capstone (PHP-29 – PHP-30)

| Milestone | Title | Deliverables |
|-----------|-------|--------------|
| **PHP-29** | End-to-End Integration | Full pipeline: edge → ROS → CV → ML → decision → safety → GPIO + API + dashboard |
| **PHP-30** | Final Plant Health System Capstone | Demonstrate complete **PHS** — see [CAPSTONE_SCENARIOS.md](./CAPSTONE_SCENARIOS.md) |

---

## Git Branch Convention

Work on **`main`** only. Do not open a new branch per milestone unless explicitly requested.

## Milestone Completion

A milestone is complete only when implementation works, tests pass, docs updated, regression verified, and acceptance criteria met. See [../development/MILESTONE_COMPLETION.md](../development/MILESTONE_COMPLETION.md).

## Related Docs

- [IMPLEMENTATION_PLAN.md](./IMPLEMENTATION_PLAN.md)
- [CAPSTONE_SCENARIOS.md](./CAPSTONE_SCENARIOS.md)
- [REPOSITORY_STRUCTURE.md](./REPOSITORY_STRUCTURE.md)
- [../design/COMPREHENSIVE_DESIGN.md](../design/COMPREHENSIVE_DESIGN.md)
- [../prompt/MASTER_PROMPT.md](../prompt/MASTER_PROMPT.md)
