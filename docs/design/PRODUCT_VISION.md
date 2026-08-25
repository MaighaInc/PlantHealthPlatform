# Product Vision

> **Platform:** PlantHealthPlatform (PHP)  
> **Deployed system:** Plant Health System (PHS)

## Mission

Build a modular **Plant Health Monitoring, Plant Intelligence, and Automated Irrigation Platform** that combines robotics, computer vision, machine learning, and full-stack software into one production-oriented system.

## Core Principle

There is **one product** — not 30 independent projects. Approximately 30 milestones incrementally extend the same codebase toward PHS.

## Capability Areas

| Domain | Technologies |
|--------|--------------|
| Robotics | ROS 2, sensors, camera, GPIO, Raspberry Pi edge |
| AI/ML | OpenCV, classical ML, deep learning, inference |
| Platform | FastAPI/Node backend, PostgreSQL, React dashboard |
| Operations | Docker, CI/CD, logging, metrics, testing |

## High-Level Diagram

```text
                         PLANTHEALTHPLATFORM
                                │
             ┌──────────────────┼──────────────────┐
             │                  │                  │
             ▼                  ▼                  ▼
          ROBOTICS             AI/ML            PLATFORM
             │                  │                  │
          ROS 2              OpenCV            Backend
          Sensors            ML/DL             PostgreSQL
          Camera             Inference          REST API
          GPIO               Training           React
          Edge               Evaluation         Dashboard
             │                  │                  │
             └──────────────────┼──────────────────┘
                                │
                                ▼
                       PLANT HEALTH SYSTEM
                                │
                 ┌──────────────┴──────────────┐
                 │                             │
             EDGE DEVICE                   SERVER/CLOUD
                 │                             │
          Raspberry Pi                  API + Database
                 │                             │
                 └──────────────┬──────────────┘
                                │
                                ▼
                         Plant Dashboard
```

## Engineering Objective

Train an engineer who can independently design, implement, integrate, test, debug, document, and deploy production-quality systems — not merely generate large volumes of code.

Prefer:

```text
small implementation + clear architecture + tests + documentation + review
```

## Capstone Outcome

At completion, the intern delivers **one evolving PlantHealthPlatform** demonstrating the full pipeline:

```text
Sensors → Camera → ROS 2 → OpenCV → Features → ML → Health → Fusion
  → Decision → Safety → GPIO → Backend → PostgreSQL → Dashboard
```

## Related Docs

- [SYSTEM_ARCHITECTURE.md](./SYSTEM_ARCHITECTURE.md)
- [SYSTEM_BOUNDARIES.md](./SYSTEM_BOUNDARIES.md)
- [../plans/ROADMAP.md](../plans/ROADMAP.md)
- [../prompt/MASTER_PROMPT.md](../prompt/MASTER_PROMPT.md)
