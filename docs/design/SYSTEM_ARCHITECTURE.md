# System Architecture

> Final target architecture for PlantHealthPlatform (PHP) → Plant Health System (PHS)

## Platform Overview

```text
                         ┌────────────────────────────┐
                         │     PLANTHEALTHPLATFORM    │
                         │            PHP             │
                         └──────────────┬─────────────┘
                                        │
        ┌───────────────────────────────┼──────────────────────────────┐
        │                               │                              │
        ▼                               ▼                              ▼
┌───────────────┐              ┌────────────────┐             ┌────────────────┐
│ ROBOTICS      │              │ AI / CV / ML   │             │ APPLICATION    │
│               │              │                │             │ PLATFORM       │
│ ROS 2         │              │ OpenCV         │             │ Backend        │
│ Sensors       │              │ Features       │             │ PostgreSQL     │
│ Camera        │              │ ML             │             │ REST API       │
│ GPIO          │              │ Deep Learning  │             │ React          │
│ Raspberry Pi  │              │ Inference      │             │ Dashboard      │
└───────┬───────┘              └───────┬────────┘             └───────┬────────┘
        │                              │                              │
        └──────────────────────────────┼──────────────────────────────┘
                                       │
                                       ▼
                              ┌──────────────────┐
                              │ Plant Health     │
                              │ Intelligence     │
                              └────────┬─────────┘
                                       │
                                       ▼
                              ┌──────────────────┐
                              │ Decision Engine  │
                              └────────┬─────────┘
                                       │
                                       ▼
                              ┌──────────────────┐
                              │ Safety Layer     │
                              └────────┬─────────┘
                                       │
                                       ▼
                              ┌──────────────────┐
                              │ Irrigation/GPIO  │
                              └────────┬─────────┘
                                       │
                                       ▼
                              ┌──────────────────┐
                              │ PLANT HEALTH     │
                              │ SYSTEM (PHS)     │
                              └──────────────────┘
```

## Data Pipeline

```text
Sensors ──► ROS 2 ──┬──► Database
                    │
Camera ──► OpenCV ──► Features ──► ML ──► Plant Health
```

**Rules:**

- Sensor and image data must be timestamped.
- Never assume `message arrival time == measurement time`.
- Raw data must not be silently overwritten.

## Backend Layering

```text
API / Controller
        ↓
Service
        ↓
Repository
        ↓
Database
```

## ML Lifecycle

```text
Dataset → Training → Evaluation → Model Registry → Inference → Prediction
```

Training must not occur inside the production inference node.

## Development Progression

ML complexity increases in stages:

1. Rule-based logic
2. Classical computer vision
3. Classical ML (Logistic Regression, Random Forest, SVM, etc.)
4. Deep learning (PyTorch/TensorFlow/ONNX) — only after baseline works

## Related Docs

- [ROS_ARCHITECTURE.md](./ROS_ARCHITECTURE.md)
- [DATA_PIPELINE.md](./DATA_PIPELINE.md)
- [ML_PIPELINE.md](./ML_PIPELINE.md)
- [IRRIGATION_SAFETY.md](./IRRIGATION_SAFETY.md)
