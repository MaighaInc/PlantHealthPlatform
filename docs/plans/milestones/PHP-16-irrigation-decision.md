# PHP-16 — Irrigation Decision Engine

## Goal

Turn fused health into an irrigation **intent** proposal — never GPIO, never `/irrigation/command`.

## Prerequisites

- PHP-15 `/plant/fused_health`
- [ADR-0003](../../architecture/adr/0003-irrigation-intent-topic.md)

## Acceptance Criteria

- [x] Package `plant_health_decision` → `/irrigation/intent`
- [x] Healthy → `water=false`; stressed (corroborated) → `water=true`
- [x] Unknown → no water; **ML-only stressed → blocked**
- [x] Decision package never imports GPIO
- [x] Params refuse publishing to `/irrigation/command`

## Launch

```bash
ros2 launch plant_health_decision decision.launch.py
```

## Architecture

Prediction ≠ Decision ≠ Actuation — this node is Decision only.
