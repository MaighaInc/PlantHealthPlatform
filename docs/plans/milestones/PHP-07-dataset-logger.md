# PHP-07 — Image Dataset Logger

## Goal

Persist images + timestamps + plant_id + optional sensor context under `ml/datasets/` with manifests; never silently overwrite raw data.

## Prerequisites

- PHP-06 complete

## Acceptance Criteria

- [x] Layout: `images/`, `labels/`, `metadata/records.jsonl`, `manifests/manifest.json`
- [x] Deterministic filenames `{plant_id}_{seq}_{timestamp}.png`
- [x] Reject missing plant_id / timestamp; refuse overwrite
- [x] ROS node `plant_health_dataset` logs `/camera/image_raw`
- [x] Unit tests for manifest integrity and validation

## Layout

```text
ml/datasets/<name>/
├── images/
├── labels/
├── metadata/records.jsonl
└── manifests/manifest.json
```

## Note on sensors

PHP-07 attaches the *latest* sensor snapshot when available (`extra.sensor_sync=latest_snapshot_php07`). PHP-08 will replace this with proper sync windows.

## Tests

```bash
export PYTHONPATH=...:ml:shared
python -m pytest tests/unit/test_dataset_logger.py -q
```
