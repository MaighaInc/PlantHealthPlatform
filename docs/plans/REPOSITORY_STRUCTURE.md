# Repository Structure

> Recommended monorepo layout for PlantHealthPlatform

## Single Repository Principle

All milestones evolve one repository: `PlantHealthPlatform/` (this repo: `E:\MaiGit\PHP`).

Do not create unnecessary directories before they are needed.

## Recommended Layout

```text
PlantHealthPlatform/
│
├── ros2_ws/
│   └── src/
│       ├── plant_health_status/
│       ├── plant_health_sensors/
│       ├── plant_health_camera/
│       ├── plant_health_cv/
│       ├── plant_health_ml/
│       ├── plant_health_inference/
│       ├── plant_health_decision/
│       ├── plant_health_irrigation/
│       └── plant_health_bringup/
│
├── backend/
│   ├── app/
│   ├── tests/
│   └── migrations/
│
├── frontend/
│   ├── src/
│   └── tests/
│
├── ml/
│   ├── datasets/
│   ├── notebooks/
│   ├── training/
│   ├── evaluation/
│   ├── models/
│   └── inference/
│
├── edge/
│   ├── gpio/
│   ├── hardware/
│   └── deployment/
│
├── shared/
│
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
│
├── docs/                    ← design, plans, development docs
│
├── scripts/
│
├── docker/
│
├── deployment/
│
├── .github/
│   └── workflows/
│
├── README.md
├── docker-compose.yml
└── .env.example
```

## Package Naming

| Context | Convention | Avoid |
|---------|------------|-------|
| ROS packages | `plant_health_*` | `php_*` |
| Python modules | `plant_health_*` | `php_*` |
| Product name | PlantHealthPlatform (PHP) | — |
| Deployed system | Plant Health System (PHS) | — |

## Documentation Location

All design, plan, and development docs live under `docs/`:

```text
docs/
├── prompt/          agent instructions
├── design/          system design
├── plans/           roadmap and milestone plans
├── development/     process and standards
└── architecture/    tech stack and ADRs
```

## Related Docs

- [ROADMAP.md](./ROADMAP.md)
- [../INDEX.md](../INDEX.md)
