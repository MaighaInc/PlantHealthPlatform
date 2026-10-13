# ADR 0006 — ROS Runs on Host; Server Tier in Docker

**Status:** Accepted  
**Date:** 2026-08-26  

## Decision

`docker compose` runs PostgreSQL + API + Web by default. **ROS 2 Humble** may run:

1. **On the host/WSL/Pi** — preferred for HARDWARE (GPIO, USB camera, real sensors).
2. **In Docker** — optional `ros` service / `phs-ros2` image for SIMULATION (`docker compose --profile ros`).

## Consequences

- Server tier documented in README; edge bringup scripts source `/opt/ros/humble` on Pi.
- `ros2_ws/Dockerfile` builds all `plant_health_*` packages with `ROS_LOCALHOST_ONLY=1` by default.
- Cross-container ROS↔API bridging is not wired; dashboard SSE reflects API/DB state.
