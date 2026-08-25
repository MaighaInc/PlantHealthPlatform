#!/usr/bin/env bash
# Run hardware-free unit tests (no ROS required).
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"
export PYTHONPATH="${ROOT}/ros2_ws/src/plant_health_status${PYTHONPATH:+:${PYTHONPATH}}"
python -m pytest tests/unit -q "$@"
