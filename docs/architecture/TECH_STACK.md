# Technology Stack

> Authoritative technology choices for PlantHealthPlatform

## Robotics

| Layer | Primary | Secondary |
|-------|---------|-----------|
| Middleware | ROS 2 Humble or Iron | — |
| Language | Python 3.10+ (`rclpy`) | C++ (`rclcpp`) when performance/hardware justified |

Use C++ only for meaningful value — not for variety.

## Python Ecosystem

```text
rclpy, NumPy, OpenCV, cv_bridge
Pydantic, FastAPI, SQLAlchemy
pytest, mypy, Ruff, Black
```

## Computer Vision

OpenCV + NumPy + cv_bridge — progressive classical CV before deep learning.

## Machine Learning

| Stage | Tools |
|-------|-------|
| Rules | Configurable engine |
| Classical CV | OpenCV features |
| Classical ML | scikit-learn classifiers |
| Deep learning | PyTorch / TensorFlow / ONNX / ONNX Runtime |

## Backend (choose one primary path)

**ML-oriented (preferred):** FastAPI, Pydantic, SQLAlchemy, PostgreSQL

**TS integration:** Node.js, TypeScript, Express/Fastify, Prisma, PostgreSQL

## Frontend

React, TypeScript, Vite, TanStack Query (or equivalent)

## Database

PostgreSQL with migrations

## Infrastructure

Docker (backend, frontend, PostgreSQL — ROS on host when hardware access requires it)

CI/CD via GitHub Actions (`.github/workflows/`)

## Edge

Raspberry Pi — sensors, camera, GPIO, edge inference

## Related Docs

- [../design/ROS_ARCHITECTURE.md](../design/ROS_ARCHITECTURE.md)
- [../design/ML_PIPELINE.md](../design/ML_PIPELINE.md)
- [adr/README.md](./adr/README.md)
