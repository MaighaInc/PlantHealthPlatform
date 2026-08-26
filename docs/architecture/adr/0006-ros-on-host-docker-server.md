# ADR 0006 — ROS Runs on Host; Server Tier in Docker

**Status:** Accepted  
**Date:** 2026-08-26  

## Decision

`docker compose` runs PostgreSQL + API + Web. **ROS 2 Humble nodes run on the host/WSL/Pi**, not inside the default compose stack (GPU/device and Humble base image complexity).

## Consequences

Documented in README; edge bringup scripts source `/opt/ros/humble`.
