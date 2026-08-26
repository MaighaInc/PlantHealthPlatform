# PHP-08 — Metadata Synchronization

## Goal

Join image and sensor samples using **acquisition-time sync windows**. Missing or delayed data is flagged — never silently paired.

## Prerequisites

- PHP-07 complete

## Acceptance Criteria

- [x] `SensorTimeBuffer` + `select_nearest_within_window`
- [x] Out-of-window (delayed) samples not joined; marked `stale_candidates` / `missing`
- [x] Partial sync when some channels absent
- [x] Dataset logger uses sync metadata in `extra`
- [x] Clock assumptions documented in `DATA_PIPELINE.md` and `sync.py` docstring
- [x] Unit tests for delayed/missing/complete cases

## Join rule

```text
For each sensor channel:
  candidates = samples with |t_sensor - t_image| ≤ window_sec
  if empty → value=null, channel ∈ missing (and stale_candidates if any existed outside)
  else → nearest by |Δt|
```

## Clock assumptions

See module docstring in `ml/plant_health_data/sync.py` and [DATA_PIPELINE.md](../../design/DATA_PIPELINE.md).
