# Sensor Fusion (PHP-15)

> Unified plant health for decision consumers — Prediction ≠ Decision ≠ Actuation

## Inputs

| Source | Topic | Role |
|--------|-------|------|
| Rules | `/plant/health` | Stage-1 sensor rules |
| Features | `/plant/features` | CV + sensor vector (optional cues) |
| ML | `/plant/disease_prediction` | Stage-3/4 prediction |

## Output

| Topic | Type | Notes |
|-------|------|-------|
| `/plant/fused_health` | `std_msgs/String` (JSON) | Single interface for PHP-16 decision engine |

## Precedence

1. No rules and no ML → `unknown` (`no_sources`)
2. Only one of rules/ML → that status (`single_source`)
3. One side `unknown` → use the definitive side at reduced confidence (`unknown_deferred`)
4. Both agree → that status (`agree`)
5. **Conflict** (`healthy` vs `stressed`) → **`unknown`** (`conflict_unknown`) — do not invent a winner for irrigation
6. Rules-only `healthy` with very low `green_pixel_ratio` may escalate to `stressed` (`cv_escalate`)

Fusion **never** drives GPIO.

## Code

- `plant_health_fusion` / `fusion_engine`
- Pure logic: `fuse.py` (unit-tested without rclpy)
