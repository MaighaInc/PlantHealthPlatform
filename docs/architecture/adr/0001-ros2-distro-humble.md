# ADR 0001 — ROS 2 Distro: Humble Hawksbill

**Status:** Accepted  
**Date:** 2026-08-25  
**Supersedes:** —

## Context

PlantHealthPlatform needs a ROS 2 distribution for edge robotics (sensors, camera, CV, inference, irrigation). Candidates were ROS 2 Humble and Iron. Development may occur on Windows via WSL2 or on Linux (Ubuntu), including Raspberry Pi deployment later.

## Decision

Use **ROS 2 Humble Hawksbill** as the primary supported distribution.

## Alternatives Considered

| Option | Notes |
|--------|-------|
| Iron | Newer; shorter support window relative to Humble LTS |
| Jazzy | Too new for early milestones; revisit later if needed |
| No ROS / custom IPC | Rejects internship learning goals and ecosystem tooling |

## Tradeoffs

**Pros:** LTS on Ubuntu 22.04; large community; stable `rclpy` / message APIs; broad Pi/docs support.  
**Cons:** Not the newest distro; Windows requires WSL2 or a Linux host for native builds.

## Consequences

- Package manifests declare compatibility with Humble.
- CI (PHP-25) should build against Humble on Ubuntu 22.04.
- Iron may be documented as experimental but is not the default.
- Local Windows coding uses pure-Python tests without `rclpy`; full node tests run under WSL/Linux with ROS sourced.

## References

- [TECH_STACK.md](../TECH_STACK.md)
- [../plans/IMPLEMENTATION_PLAN.md](../../plans/IMPLEMENTATION_PLAN.md) — PHP-01
- https://docs.ros.org/en/humble/
