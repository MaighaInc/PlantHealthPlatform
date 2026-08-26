#!/usr/bin/env bash
# Run hardware-free unit tests (no ROS required).
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

# Prefer local .venv (needed on Windows for onnx/onnxscript short-path installs).
if [[ -x "${ROOT}/.venv/Scripts/python" ]]; then
  PYTHON="${ROOT}/.venv/Scripts/python"
elif [[ -x "${ROOT}/.venv/bin/python" ]]; then
  PYTHON="${ROOT}/.venv/bin/python"
else
  PYTHON="${PYTHON:-python}"
fi

export PYTHONPATH="${ROOT}/ros2_ws/src/plant_health_status:${ROOT}/ros2_ws/src/plant_health_sensors:${ROOT}/ros2_ws/src/plant_health_camera:${ROOT}/ros2_ws/src/plant_health_cv:${ROOT}/ros2_ws/src/plant_health_health:${ROOT}/ros2_ws/src/plant_health_inference:${ROOT}/ros2_ws/src/plant_health_fusion:${ROOT}/ml:${ROOT}/shared${PYTHONPATH:+:${PYTHONPATH}}"
"${PYTHON}" -m pytest tests/unit -q "$@"
