# PHP-09 — Rule-Based Plant Health Engine

## Goal

Configurable, testable health rules publishing `/plant/health` — no GPIO, thresholds not buried in callbacks.

## Prerequisites

- PHP-04 (sensors); PHP-08 preferred for later fusion

## Acceptance Criteria

- [x] `evaluate_health()` pure function with externalized `HealthRulesConfig`
- [x] Dry soil + hot temp → `stressed` / `water_stress`
- [x] Normal soil/temp → `healthy`
- [x] Invalid sensors → `unknown`
- [x] ROS node `health_engine` publishes `/plant/health`
- [x] Table-driven unit tests

## Rules (priority order)

1. Invalid / NaN / out-of-range soil or temperature → `UNKNOWN`
2. `soil < soil_dry_threshold` AND `temp > temp_hot_threshold` → `STRESSED` (`water_stress`)
3. `soil < soil_dry_threshold` → `STRESSED` (`dry_soil`)
4. Else → `HEALTHY` (`nominal`)

Default thresholds: soil dry `< 30%`, hot temp `> 32°C` (YAML/params).
