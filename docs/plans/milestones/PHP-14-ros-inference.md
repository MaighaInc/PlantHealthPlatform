# PHP-14 — ROS AI Inference Node

## Goal

Online inference: subscribe to `/plant/features`, validate/preprocess, run model, publish prediction + confidence + model version + latency on `/plant/disease_prediction`. No training, no GPIO.

## Prerequisites

- PHP-10 features; PHP-11 (or PHP-13) model artifact
- ADR-0002 for ONNX path (joblib default for SIMULATION)

## Acceptance Criteria

- [x] Package `plant_health_inference` with `inference_engine` node
- [x] Publish JSON: prediction, confidence, model_name, model_version, latency_ms
- [x] `confidence < threshold` → `unknown`
- [x] Backends: `mock` (SIMULATION) and `joblib` (classical baseline)
- [x] Unit tests cover Scenario 4 path without rclpy
- [x] No GPIO / no training in node

## Launch (SIMULATION)

```bash
ros2 launch plant_health_inference inference.launch.py backend:=mock
# With classical model:
ros2 launch plant_health_inference inference.launch.py backend:=joblib \
  model_path:=/abs/path/ml/models/plant-health-classifier-1.0.0.joblib
```

## Capstone Scenario 4 (SIMULATION)

`/plant/features` → `inference_engine` → `/plant/disease_prediction` using mock or joblib backend.
