#!/usr/bin/env bash
# Build and run the PHS ROS 2 SIMULATION container.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

IMAGE="${PHS_ROS_IMAGE:-phs-ros2}"

docker build -f ros2_ws/Dockerfile -t "$IMAGE" .
exec docker run --rm -it "$IMAGE" "$@"
