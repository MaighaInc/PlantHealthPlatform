# ADR 0003 — Irrigation Intent Topic Separate from Command

**Status:** Accepted  
**Date:** 2026-08-25  
**Supersedes:** —

## Context

PHP-16 introduces an irrigation **decision** engine. Later milestones add safety (PHP-18) and GPIO actuation (PHP-17). Publishing a decision directly on `/irrigation/command` would blur Decision vs Actuation and risk consumers treating proposals as pin-level commands.

## Decision

1. **`plant_health_decision`** publishes **`/irrigation/intent`** — a JSON **proposal** (`water: true|false`, reason, fused snapshot refs). It never imports GPIO.
2. **`/irrigation/command`** is reserved for the **post-safety** actuation path (PHP-17/18 irrigation node), not for raw decision output.
3. Decision input is **`/plant/fused_health`** only (PHP-15).

## Alternatives Considered

| Option | Notes |
|--------|-------|
| Decision publishes `/irrigation/command` as “proposal” | Easy to misuse as actuation; name implies command |
| Decision publishes Bool on `/irrigation/command` | Too lossy; no reason/audit fields |
| Collapse decision into fusion | Violates Prediction ≠ Decision ≠ Actuation |

## Tradeoffs

**Pros:** Clear topic semantics; safety layer can gate intent → command; unit-testable without hardware.  
**Cons:** Extra topic; bringup must wire intent → safety → command.

## Consequences

- PHP-16 acceptance uses `/irrigation/intent`.
- PHP-18 safety node will subscribe to intent and publish gated `/irrigation/command` + `/irrigation/status`.
- Docs and ROS architecture mark `/irrigation/command` as planned until safety lands.

## References

- [SYSTEM_BOUNDARIES.md](../../design/SYSTEM_BOUNDARIES.md)
- [IRRIGATION_SAFETY.md](../../design/IRRIGATION_SAFETY.md)
- [SENSOR_FUSION.md](../../design/SENSOR_FUSION.md)
- [IMPLEMENTATION_PLAN.md](../../plans/IMPLEMENTATION_PLAN.md) — PHP-16…PHP-18
