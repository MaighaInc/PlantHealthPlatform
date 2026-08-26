# PlantHealthPlatform — Comprehensive Implementation Plan

> **Authority:** End-to-end delivery plan covering all concepts in `docs/` and all milestones PHP-01 … PHP-30.  
> **Product:** PlantHealthPlatform (PHP) → Plant Health System (PHS)  
> **Last updated:** August 2026  
> **Design companion:** [../design/COMPREHENSIVE_DESIGN.md](../design/COMPREHENSIVE_DESIGN.md)  
> **Roadmap index:** [ROADMAP.md](./ROADMAP.md)

This plan tells **how** to build the system designed in COMPREHENSIVE_DESIGN. Per-milestone working plans under [`milestones/`](./milestones/) are created when a milestone starts; this document remains the master schedule and acceptance framework.

---

## 1. Delivery Principles

1. **One product** — each milestone extends the same repo; never greenfield demos.
2. **Inspect first** — read existing code, topics, APIs, and schema before writing.
3. **Smallest useful increment** — architecture clarity over code volume.
4. **Interfaces before devices** — `SensorInterface` / `GPIOInterface` enable hardware-free CI.
5. **Prediction ≠ Decision ≠ Actuation** — enforced from first irrigation-related code.
6. **Tests + docs + regression** — required for milestone completion.
7. **ADRs for irreversible choices** — ROS distro, backend stack, real-time mechanism, etc.
8. **Educational outcomes** — intern can explain what/why/integrate/fail/test/deploy/improve.

### Completion gate (every milestone)

See [../development/MILESTONE_COMPLETION.md](../development/MILESTONE_COMPLETION.md):

- Implementation works; regression intact
- Tests exist and pass
- Docs and config reproducible
- Errors handled; scope focused; no unjustified dependencies
- Intern can answer the educational checklist

### Agent workflow

Follow [../development/AGENT_WORKFLOW.md](../development/AGENT_WORKFLOW.md) (Understand → Inspect → Architect → Plan → Implement → Test → Diagnose → Review → Document → Summarize).

### Branching

**Single-branch workflow:** commit milestone work directly on `main`. Do not create `feature/php-NN-*` branches unless the user explicitly requests a separate branch.

Commits: `feat|fix|test|docs(scope): message` — see [../development/CODING_STANDARDS.md](../development/CODING_STANDARDS.md).

---

## 2. Phase Overview

```text
Phase 1  PHP-01–04   ROS foundation & sensors
Phase 2  PHP-05–10   Vision & data
Phase 3  PHP-11–15   Machine learning
Phase 4  PHP-16–18   Irrigation & edge actuation
Phase 5  PHP-19–22   Full-stack platform
Phase 6  PHP-23–28   Production readiness
Phase 7  PHP-29–30   Integration & capstone
         ↓
    Plant Health System (PHS)
```

| Phase | Outcome | Design anchors |
|-------|---------|----------------|
| 1 | Runnable ROS workspace, virtual sensors, abstractions | ROS, HARDWARE_ABSTRACTION |
| 2 | Camera → CV → features → rules → dataset sync | CV, DATA_PIPELINE |
| 3 | Classical ML → DL → inference node → fusion | ML_PIPELINE |
| 4 | Decision + GPIO + safety (fail-safe) | IRRIGATION_SAFETY |
| 5 | PostgreSQL + API + React + real-time choice | DATABASE, API, FRONTEND |
| 6 | Docker, tests, CI, observability, security, Pi deploy | ops docs |
| 7 | Full E2E + capstone scenarios | CAPSTONE_SCENARIOS |

---

## 3. Cross-Cutting Workstreams

These run **alongside** milestones — not as one-off spikes.

| Workstream | When it starts | Continuous activities |
|------------|----------------|------------------------|
| **Docs** | PHP-01 | Update README + design deep-dives; milestone plan file |
| **Config** | PHP-02 | `.env.example`, ROS params, mode flags |
| **Testing** | PHP-01 | Unit → integration → E2E (PHP-24 expands) |
| **ADRs** | As needed | Distro, backend, CV approach, real-time, Docker scope |
| **CI** | Skeleton early; full PHP-25 | Lint, typecheck, pytest, ROS build, ML smoke |
| **Security** | Mindset early; harden PHP-27 | No secrets; actuator auth in production |
| **Observability** | Logging early; metrics PHP-26 | Structured logs → health → metrics |

---

## 4. Phase 1 — ROS Foundation & Sensors (PHP-01 – PHP-04)

**Goal:** A maintainable ROS 2 workspace with configurable nodes and swappable sensors — no hardware required.

### PHP-01 — ROS 2 Publisher/Subscriber Foundation

| Item | Detail |
|------|--------|
| **Prerequisites** | ROS 2 install (Humble or Iron — record ADR), repo skeleton |
| **Deliverables** | Minimal `plant_health_*` package(s); publisher + subscriber; lifecycle; ROS logging; topic inspection notes |
| **Architecture** | Establish `ros2_ws/src/` and naming `plant_health_*` |
| **Tests** | Launch smoke; message round-trip in SIMULATION |
| **Docs** | README Overview/Running; start ROS_ARCHITECTURE topic list |
| **Acceptance** | Two nodes communicate on a documented topic; logs visible; build reproducible |

**Learning focus:** ROS node lifecycle, topics, logging.

---

### PHP-02 — ROS Parameters and Runtime Configuration

| Item | Detail |
|------|--------|
| **Prerequisites** | PHP-01 |
| **Deliverables** | Declared parameters; startup validation; runtime inspection; `.env.example` seed for non-ROS config |
| **Architecture** | Config sources: ROS params + env (see CONFIGURATION) |
| **Tests** | Invalid param rejected; valid param applied |
| **Acceptance** | Changing a parameter changes node behavior without code edits |

**Learning focus:** Configuration over hard-coding.

---

### PHP-03 — Virtual Sensor Framework

| Item | Detail |
|------|--------|
| **Prerequisites** | PHP-02 |
| **Deliverables** | Virtual soil / temp / humidity / light / CO₂; configurable rate, bounds, noise, outliers, invalid values; publish on environment/soil topics |
| **Architecture** | Feeds later `SensorInterface`; supports SIMULATION |
| **Tests** | Deterministic seed tests; invalid value injection |
| **Acceptance** | Dashboard-less `ros2 topic echo` shows plausible + injectable bad data |

**Learning focus:** Simulation for testability.

---

### PHP-04 — Sensor Abstraction

| Item | Detail |
|------|--------|
| **Prerequisites** | PHP-03 |
| **Deliverables** | `SensorInterface`; Virtual / Mock / Real adapter stubs; nodes use interface only |
| **Architecture** | HARDWARE_ABSTRACTION; DEVELOPMENT_MODE selection |
| **Tests** | MockSensor unit tests; swap implementation without changing consumer |
| **Acceptance** | Consumer code has zero device-specific imports |

**Learning focus:** Dependency inversion / ports & adapters.

**Phase 1 exit criteria:** SIMULATION mode publishes multi-sensor stream via abstractions; CI-ready without Pi.

---

## 5. Phase 2 — Vision & Data (PHP-05 – PHP-10)

**Goal:** Camera → OpenCV → features → rule-based health → reproducible datasets with synchronized metadata.

### PHP-05 — Camera Integration

| Item | Detail |
|------|--------|
| **Prerequisites** | PHP-04 |
| **Deliverables** | USB (or sample) acquisition; `/camera/image_raw`; resolution/FPS params; timestamps; failure / drop / invalid detection; clean shutdown |
| **Modes** | SIMULATION: sample images; DEVELOPMENT: USB |
| **Tests** | Invalid frame rejected; resource release; reconnect policy documented |
| **Acceptance** | Images publish with acquisition timestamps; failure is logged, not silent |

---

### PHP-06 — OpenCV Processing Pipeline

| Item | Detail |
|------|--------|
| **Prerequisites** | PHP-05 |
| **Deliverables** | Validation → resize → denoise → color → segmentation → ROI → features → viz; publish processed image / ROI as designed |
| **Docs** | Per-algorithm writeups (Problem…Tradeoffs) for HSV/morphology/contours as used |
| **Tests** | Unit tests on pure CV functions with fixtures |
| **Acceptance** | Pipeline runs end-to-end on sample images; parameters documented |

---

### PHP-07 — Image Dataset Logger

| Item | Detail |
|------|--------|
| **Prerequisites** | PHP-06 |
| **Deliverables** | Persist images + timestamps + plant_id + sensor context + metadata under `ml/datasets/` layout; manifests |
| **Architecture** | Raw data preserved; no silent overwrite |
| **Tests** | Manifest integrity; missing metadata rejected |
| **Acceptance** | Reproducible dataset folder without manual filename conventions |

---

### PHP-08 — Metadata Synchronization

| Item | Detail |
|------|--------|
| **Prerequisites** | PHP-07 |
| **Deliverables** | Sync windows for image + sensors; handle missing/delayed; document clock assumptions |
| **Tests** | Delayed sensor → no silent wrong join; missing → flagged |
| **Acceptance** | Joined records use acquisition times, not arrival times alone |

---

### PHP-09 — Rule-Based Plant Health Engine

| Item | Detail |
|------|--------|
| **Prerequisites** | PHP-04, preferably PHP-08 |
| **Deliverables** | Configurable rules → `/plant/health` (or equivalent); thresholds externalized |
| **Architecture** | Pre-ML Stage 1; no GPIO |
| **Tests** | Table-driven rule tests |
| **Acceptance** | Dry soil + hot temp → stressed; normal → healthy; rules not in callbacks |

---

### PHP-10 — Feature Extraction

| Item | Detail |
|------|--------|
| **Prerequisites** | PHP-06 |
| **Deliverables** | Feature vector: leaf_area, green_ratio, hue/sat/value stats, shape, plus sensor features; publish `/plant/features` |
| **Tests** | Golden fixtures for feature numeric ranges |
| **Acceptance** | Features stable for fixed input image; documented schema |

**Phase 2 exit criteria:** Synchronized image+sensor datasets; rule health; feature stream ready for ML.

---

## 6. Phase 3 — Machine Learning (PHP-11 – PHP-15)

**Goal:** Defensible classical ML baseline, evaluation with leakage checks, optional DL, ROS inference node, fusion.

### PHP-11 — Classical ML Baseline

| Item | Detail |
|------|--------|
| **Prerequisites** | PHP-10, PHP-07 |
| **Deliverables** | Classifier labels: `healthy` / `stressed` / `unknown`; train offline under `ml/training/`; versioned artifact under `ml/models/` |
| **Architecture** | Stage 3 classical ML; no GPIO |
| **Tests** | Preprocess unit tests; smoke train on tiny fixture |
| **Acceptance** | Model file named with version; training reproducible from manifest |

---

### PHP-12 — ML Evaluation Pipeline

| Item | Detail |
|------|--------|
| **Prerequisites** | PHP-11 |
| **Deliverables** | Split strategy; metrics (acc, precision, recall, F1, confusion); leakage checks; reports under `ml/evaluation/` |
| **Tests** | Leakage detector catches intentional duplicate plant split |
| **Acceptance** | Evaluation report generated; known leakage cases fail the gate |

---

### PHP-13 — Deep Learning Classifier

| Item | Detail |
|------|--------|
| **Prerequisites** | PHP-12; ADR justifying DL vs classical |
| **Deliverables** | Train DL model; evaluate; export (prefer ONNX for edge); version registry entry |
| **Acceptance** | Export loads in inference smoke test; metrics compared to baseline |

---

### PHP-14 — ROS AI Inference Node

| Item | Detail |
|------|--------|
| **Prerequisites** | PHP-11 or PHP-13 artifact |
| **Deliverables** | `plant_health_inference`: subscribe → validate → preprocess → infer → publish prediction + confidence + version + latency |
| **Constraints** | No training, no GPIO, no DB schema ownership, no frontend |
| **UNKNOWN** | confidence < threshold → UNKNOWN |
| **Acceptance** | Capstone Scenario 4 path works in SIMULATION |

---

### PHP-15 — Sensor Fusion

| Item | Detail |
|------|--------|
| **Prerequisites** | PHP-09, PHP-10, PHP-14 |
| **Deliverables** | Combine sensors + CV features + ML into unified health representation for decision consumers |
| **Tests** | Conflicting inputs → documented precedence / UNKNOWN behavior |
| **Acceptance** | Decision engine can subscribe to one fused health interface |

**Phase 3 exit criteria:** Offline ML lifecycle + online inference + fusion; ML never actuates.

---

## 7. Phase 4 — Irrigation & Edge (PHP-16 – PHP-18)

**Goal:** Safe actuation path with mocks for CI and real GPIO for HARDWARE mode.

### PHP-16 — Irrigation Decision Engine

| Item | Detail |
|------|--------|
| **Prerequisites** | PHP-15 |
| **Deliverables** | Decision node: fused inputs → irrigation **intent** (not GPIO); publish `/irrigation/command` as *proposal* or separate intent topic per ADR |
| **Architecture** | Prediction ≠ Decision ≠ Actuation |
| **Tests** | Healthy → no water intent; dry → intent true; UNKNOWN ML alone → no ML-only intent |
| **Acceptance** | Decision never imports GPIO implementations |

---

### PHP-17 — GPIO Abstraction

| Item | Detail |
|------|--------|
| **Prerequisites** | PHP-16 |
| **Deliverables** | `GPIOInterface`, `MockGPIO`, `RaspberryPiGPIO`; irrigation node uses interface |
| **Tests** | MockGPIO records pin transitions |
| **Acceptance** | SIMULATION/DEVELOPMENT use MockGPIO exclusively |

---

### PHP-18 — Irrigation Safety System

| Item | Detail |
|------|--------|
| **Prerequisites** | PHP-17 |
| **Deliverables** | Max duration, max daily, cooldown, min moisture, e-stop, invalid sensor fail-safe, relay tracking, startup/shutdown OFF |
| **Tests** | Each safety rule unit-tested; invalid sensor blocks actuation |
| **Acceptance** | Capstone Scenarios 2, 3, 5 (safety portion) pass with MockGPIO |

**Phase 4 exit criteria:** Full decision → safety → MockGPIO path; fail-safe proven.

---

## 8. Phase 5 — Full-Stack Platform (PHP-19 – PHP-22)

**Goal:** Persist PHS data; expose REST; visualize; choose real-time transport.

### PHP-19 — PostgreSQL Data Layer

| Item | Detail |
|------|--------|
| **Prerequisites** | Stable observation / irrigation / prediction shapes |
| **Deliverables** | Migrations for core entities; repositories; ROS→DB bridge or ingestion service |
| **Stack ADR** | FastAPI+SQLAlchemy (preferred) or Node+Prisma |
| **Acceptance** | Migrate up/down; seed; repository CRUD for plants/readings/events |

---

### PHP-20 — REST API

| Item | Detail |
|------|--------|
| **Prerequisites** | PHP-19 |
| **Deliverables** | Endpoints per API.md; validation; errors; pagination/filter; layering Controller→Service→Repository |
| **Tests** | API integration tests against test DB |
| **Acceptance** | Documented OpenAPI or equivalent; plant/sensor/health/irrigation/models/status readable |

---

### PHP-21 — React Dashboard

| Item | Detail |
|------|--------|
| **Prerequisites** | PHP-20 |
| **Deliverables** | Pages: Dashboard, Plant Detail, Irrigation, ML; typed clients; modular structure |
| **Acceptance** | Operator can see health, sensors, irrigation state, model version from live API |

---

### PHP-22 — Real-Time Monitoring

| Item | Detail |
|------|--------|
| **Prerequisites** | PHP-21 |
| **Deliverables** | ADR comparing polling / WebSocket / SSE / ROS bridge; implement chosen approach |
| **Acceptance** | Dashboard updates without full page reload for status/irrigation/alerts |

**Phase 5 exit criteria:** Browser UI over PostgreSQL-backed API reflecting edge pipeline.

---

## 9. Phase 6 — Production Readiness (PHP-23 – PHP-28)

**Goal:** Deployable, observable, secured, CI-verified system including edge.

### PHP-23 — Dockerization

| Item | Detail |
|------|--------|
| **Deliverables** | Containers for backend, frontend, PostgreSQL; `docker-compose.yml`; ROS on host if needed (ADR) |
| **Acceptance** | `docker compose up` brings API+DB+UI; documented ROS host path |

---

### PHP-24 — Automated Testing Expansion

| Item | Detail |
|------|--------|
| **Deliverables** | Broader unit/integration/E2E with mocks; fixture library |
| **Acceptance** | E2E path: camera/sample → … → MockGPIO → DB → API (headless or smoke UI) |

---

### PHP-25 — CI/CD

| Item | Detail |
|------|--------|
| **Deliverables** | GitHub Actions: lint → typecheck → unit → integration → ROS build → ML smoke |
| **Acceptance** | PR checks green without Raspberry Pi |

---

### PHP-26 — Observability

| Item | Detail |
|------|--------|
| **Deliverables** | `/health`, structured logs, ROS diagnostics, freshness, latencies, irrigation audit, error counters |
| **Acceptance** | Operator can diagnose stale sensor and failed inference from logs/metrics |

---

### PHP-27 — Security Hardening

| Item | Detail |
|------|--------|
| **Deliverables** | AuthN/AuthZ; secrets; CORS; upload/model validation; **actuator authorization** |
| **Acceptance** | Unauthenticated `POST /api/irrigation/manual` rejected in PRODUCTION mode |

---

### PHP-28 — Raspberry Pi / Edge Deployment

| Item | Detail |
|------|--------|
| **Deliverables** | Edge deploy docs/scripts; HARDWARE mode with real sensors/camera/GPIO; networking to server |
| **Acceptance** | Bringup on Pi in HARDWARE mode; safety still enforced; remote dashboard shows live data |

**Phase 6 exit criteria:** CI green; containers for server tier; Pi path documented and exercised.

---

## 10. Phase 7 — Integration & Capstone (PHP-29 – PHP-30)

### PHP-29 — End-to-End Integration

Wire and harden:

```text
Camera → ROS → CV → Features → ML → Health → Fusion
  → Decision → Safety → GPIO (mock or real)
  + Backend → PostgreSQL → API → Dashboard
```

| Acceptance | Detail |
|------------|--------|
| Single bringup | Mode-selectable launch |
| Regression | Prior milestone suites still pass |
| Failure injection | Invalid sensor, low confidence, camera drop handled |

---

### PHP-30 — Final PHS Capstone

Execute and document all scenarios in [CAPSTONE_SCENARIOS.md](./CAPSTONE_SCENARIOS.md):

1. Healthy plant → irrigation OFF  
2. Dry soil → irrigation required (via safety)  
3. Invalid sensor → BLOCKED + alert  
4. Low ML confidence → UNKNOWN; ML-only auto water BLOCKED  
5. Manual irrigation → auth → safety → ON → log → max duration → OFF  

**Capstone deliverables:**

- Demo script / runbook  
- Architecture walkthrough  
- Known limitations and next improvements  
- ADRs finalized  
- Intern educational oral/written answers complete  

**Program exit:** One evolving PlantHealthPlatform demonstrated as Plant Health System (PHS) — not 30 disconnected demos.

---

## 11. Per-Milestone Plan Template

When starting milestone `PHP-NN`, create `plans/milestones/PHP-NN-slug.md`:

```markdown
# PHP-NN — Title

## Goal
## Prerequisites
## Acceptance Criteria
## Architecture Impact
## Files to Create/Modify
## Interfaces
## Tests
## Documentation Updates
## ADRs (if any)
## Known Risks
## Intern Learning Outcomes
```

Update [`milestones/README.md`](./milestones/README.md) status table as files appear.

---

## 12. Dependency Graph (simplified)

```text
01 → 02 → 03 → 04 ─┬→ 05 → 06 ─┬→ 07 → 08 ─┐
                   │           ├→ 10 ──────┤
                   │           └→ 09 ←──────┤
                   │                        ↓
                   │              11 → 12 → 13?
                   │                        ↓
                   │                       14 → 15 → 16 → 17 → 18
                   │                                              ↓
                   └──────────────► 19 → 20 → 21 → 22
                                              ↓
                         23 → 24 → 25 → 26 → 27 → 28 → 29 → 30
```

Notes:

- PHP-09 can start after sensors (PHP-04) even before full CV; enrich with features later.
- PHP-13 is optional path if classical ML meets goals — still document justification either way.
- PHP-19 can begin once observation schemas stabilize (often after PHP-15/16).

---

## 13. Suggested Implementation Order for Tooling Bootstrap (pre–PHP-01)

Before coding PHP-01, establish minimal scaffolding (can be a “PHP-00” checklist, not a graded milestone):

1. Repo README + `.gitignore` + `.env.example`  
2. `docs/` already present — keep INDEX current  
3. Choose ROS distro → ADR  
4. Create empty `ros2_ws` that builds  
5. Choose backend stack → ADR (or defer until PHP-19, but prefer early)  
6. Python tooling: Ruff, Black, mypy, pytest configs  
7. CI skeleton (lint only) optional  

---

## 14. Risk Register

| Risk | Mitigation |
|------|------------|
| Jumping to DL too early | Enforce PHP-11/12 before PHP-13; require ADR |
| ML wired to GPIO | Code review + architectural tests; separate packages |
| Hardware blocks CI | Interfaces + SIMULATION mandatory from PHP-03/04/17 |
| Schema freeze too early | Migrations; evolving entities in DATABASE.md |
| Topic sprawl | Review before new topics; ROS_ARCHITECTURE is source of truth |
| Secret leakage | `.env.example` only; PHP-27 audit |
| Scope creep / refactors | Coding standards scope discipline |
| Timestamp bugs | PHP-08 tests; never use arrival-as-measurement |
| Unsafe irrigation | PHP-18 fail-safe; e-stop; max duration tests |
| Unmaintainable UI | Feature modules; typed API contracts |

---

## 15. Definition of Done — Plant Health System

PHS is complete when:

- [ ] All milestones PHP-01–PHP-30 accepted (or explicitly waived with ADR)  
- [ ] Capstone scenarios 1–5 pass in SIMULATION; HARDWARE demo for subset agreed  
- [ ] Prediction / Decision / Actuation separation intact  
- [ ] Hardware-free CI green  
- [ ] Dashboard + API + DB reflect live (or simulated) plant state  
- [ ] Models versioned; UNKNOWN respected  
- [ ] Irrigation safety enforced; manual path authorized in PRODUCTION  
- [ ] Documentation INDEX + COMPREHENSIVE_DESIGN + this plan accurate  
- [ ] Intern can independently explain and extend the system  

---

## 16. Documentation Update Checklist (per milestone)

- [ ] Root / package README sections as applicable  
- [ ] Relevant `docs/design/*` deep-dive  
- [ ] This plan / ROADMAP status if scope changes  
- [ ] `plans/milestones/PHP-NN-*.md`  
- [ ] ADR if decision is significant  
- [ ] `development/RUNNING_LOG.md` session note (create when work begins)  

---

## 17. Related Documents

| Document | Role |
|----------|------|
| [../design/COMPREHENSIVE_DESIGN.md](../design/COMPREHENSIVE_DESIGN.md) | What to build |
| [ROADMAP.md](./ROADMAP.md) | Milestone titles table |
| [CAPSTONE_SCENARIOS.md](./CAPSTONE_SCENARIOS.md) | Final acceptance scenarios |
| [REPOSITORY_STRUCTURE.md](./REPOSITORY_STRUCTURE.md) | Monorepo layout |
| [milestones/](./milestones/) | Working plans per milestone |
| [../prompt/MASTER_PROMPT.md](../prompt/MASTER_PROMPT.md) | Agent constitution |
| [../INDEX.md](../INDEX.md) | Doc hub |
