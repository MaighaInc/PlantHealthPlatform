# PHP-15 — Sensor Fusion

## Goal

Combine rule health, CV features, and ML prediction into one fused health interface for the decision engine.

## Prerequisites

- PHP-09 `/plant/health`; PHP-10 `/plant/features`; PHP-14 `/plant/disease_prediction`

## Acceptance Criteria

- [x] Package `plant_health_fusion` publishes `/plant/fused_health` (JSON)
- [x] Documented precedence; **healthy vs stressed conflict → `unknown`**
- [x] Unit tests for conflict / agree / single-source / CV escalate
- [x] No GPIO; fusion never actuates

## Precedence

See module docstring in `plant_health_fusion/fuse.py`:

1. No sources → unknown  
2. Single source → that status  
3. One unknown → defer to definitive source (reduced confidence)  
4. Agree → shared status  
5. Conflict healthy↔stressed → **unknown** (`conflict_unknown`)  
6. Optional low `green_pixel_ratio` may escalate rules-only healthy → stressed

## Launch

```bash
ros2 launch plant_health_fusion fusion.launch.py
```

Decision consumers subscribe to `/plant/fused_health` only.
