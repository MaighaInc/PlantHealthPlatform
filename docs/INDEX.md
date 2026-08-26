# PlantHealthPlatform — Documentation Index

> **Product:** PlantHealthPlatform (PHP)  
> **Deployed system:** Plant Health System (PHS)  
> **Last updated:** August 2026  
> **Consolidated specs:** [design/COMPREHENSIVE_DESIGN.md](./design/COMPREHENSIVE_DESIGN.md) · [plans/IMPLEMENTATION_PLAN.md](./plans/IMPLEMENTATION_PLAN.md)

---

## Consolidated Specs (start here for design + delivery)

| Document | Scope |
|----------|-------|
| [design/COMPREHENSIVE_DESIGN.md](./design/COMPREHENSIVE_DESIGN.md) | **Unified design** — all product, architecture, ROS, CV, ML, data, API, safety, and ops concepts |
| [plans/IMPLEMENTATION_PLAN.md](./plans/IMPLEMENTATION_PLAN.md) | **Unified delivery plan** — phases PHP-01…PHP-30, acceptance, dependencies, risks, DoD |

---

## Read Order for Coding Agents

Every AI agent **must read these documents before writing code**, in this order:

| # | Document | Scope |
|---|----------|-------|
| 1 | [prompt/MASTER_PROMPT.md](./prompt/MASTER_PROMPT.md) | Full agent constitution — role, architecture, workflow |
| 2 | [design/COMPREHENSIVE_DESIGN.md](./design/COMPREHENSIVE_DESIGN.md) | Consolidated system design (all concepts) |
| 3 | [plans/IMPLEMENTATION_PLAN.md](./plans/IMPLEMENTATION_PLAN.md) | Consolidated implementation plan (all milestones) |
| 4 | [design/PRODUCT_VISION.md](./design/PRODUCT_VISION.md) | Mission, product direction, final architecture |
| 5 | [design/SYSTEM_BOUNDARIES.md](./design/SYSTEM_BOUNDARIES.md) | Prediction ≠ Decision ≠ Actuation; module boundaries |
| 6 | [architecture/TECH_STACK.md](./architecture/TECH_STACK.md) | ROS 2, Python, CV, ML, backend, frontend |
| 7 | [plans/REPOSITORY_STRUCTURE.md](./plans/REPOSITORY_STRUCTURE.md) | Monorepo layout and package naming |
| 8 | [plans/ROADMAP.md](./plans/ROADMAP.md) | 30 incremental milestones (PHP-01 … PHP-30) |
| 9 | [development/AGENT_WORKFLOW.md](./development/AGENT_WORKFLOW.md) | 10-step task workflow and response format |
| 10 | [development/CODING_STANDARDS.md](./development/CODING_STANDARDS.md) | Git, dependencies, error handling, logging |
| 11 | [development/TESTING.md](./development/TESTING.md) | Unit, integration, E2E, hardware-free CI |
| 12 | [development/MILESTONE_COMPLETION.md](./development/MILESTONE_COMPLETION.md) | Acceptance criteria and regression rules |

### Design (read when building relevant subsystem)

| Document | Scope |
|----------|-------|
| [design/COMPREHENSIVE_DESIGN.md](./design/COMPREHENSIVE_DESIGN.md) | **Master design synthesis** — concept coverage map to deep-dives |
| [design/SYSTEM_ARCHITECTURE.md](./design/SYSTEM_ARCHITECTURE.md) | High-level platform diagram and data flow |
| [design/ROS_ARCHITECTURE.md](./design/ROS_ARCHITECTURE.md) | Topics, messages, bringup, node boundaries |
| [design/CV_PIPELINE.md](./design/CV_PIPELINE.md) | OpenCV processing pipeline and learning requirements |
| [design/CV_ALGORITHMS.md](./design/CV_ALGORITHMS.md) | Per-algorithm Problem/Why/Tradeoffs (PHP-06) |
| [design/FEATURE_SCHEMA.md](./design/FEATURE_SCHEMA.md) | `/plant/features` schema v1.0 (PHP-10) |
| [design/ML_PIPELINE.md](./design/ML_PIPELINE.md) | ML lifecycle, versioning, leakage, inference |
| [design/SENSOR_FUSION.md](./design/SENSOR_FUSION.md) | Rules + CV + ML → `/plant/fused_health` (PHP-15) |
| [design/DATA_PIPELINE.md](./design/DATA_PIPELINE.md) | Sensors → ROS → DB; timestamps; datasets |
| [design/DATABASE.md](./design/DATABASE.md) | PostgreSQL entities and migration policy |
| [design/API.md](./design/API.md) | REST endpoints and backend layering |
| [design/FRONTEND.md](./design/FRONTEND.md) | React dashboard structure and pages |
| [design/IRRIGATION_SAFETY.md](./design/IRRIGATION_SAFETY.md) | Decision engine, safety layer, GPIO abstraction |
| [design/HARDWARE_ABSTRACTION.md](./design/HARDWARE_ABSTRACTION.md) | Sensor/GPIO interfaces and development modes |

### Plans

| Document | Scope |
|----------|-------|
| [plans/IMPLEMENTATION_PLAN.md](./plans/IMPLEMENTATION_PLAN.md) | **Master delivery plan** — phases, deps, risks, PHS DoD |
| [plans/ROADMAP.md](./plans/ROADMAP.md) | Milestone title index |
| [plans/CAPSTONE_SCENARIOS.md](./plans/CAPSTONE_SCENARIOS.md) | Final acceptance test scenarios |
| [plans/milestones/](./plans/milestones/) | Per-milestone plans (generated as work progresses) |

### Development

| Document | Scope |
|----------|-------|
| [development/CONFIGURATION.md](./development/CONFIGURATION.md) | `.env`, ROS parameters, secrets |
| [development/DEVELOPMENT_MODES.md](./development/DEVELOPMENT_MODES.md) | SIMULATION, DEVELOPMENT, HARDWARE, PRODUCTION |
| [development/OBSERVABILITY.md](./development/OBSERVABILITY.md) | Logging, metrics, diagnostics |
| [development/SECURITY.md](./development/SECURITY.md) | Auth, actuator authorization, validation |

### Architecture Decisions

| Document | Scope |
|----------|-------|
| [architecture/adr/README.md](./architecture/adr/README.md) | ADR index and template |

---

## Folder Layout

```text
docs/
├── INDEX.md                 ← you are here
├── prompt/
│   └── MASTER_PROMPT.md     ← authoritative agent instructions
├── design/                  ← system design specs
├── plans/                   ← roadmap and milestone plans
├── development/             ← engineering process and standards
└── architecture/            ← tech stack and ADRs
```

---

## Living Documents

As milestones are completed, update:

- Per-milestone plans under `plans/milestones/`
- ADRs under `architecture/adr/` for significant decisions
- [`development/RUNNING_LOG.md`](./development/RUNNING_LOG.md) after each session
