# PHP-10 — Feature Extraction

## Goal

Publish a schema-stable feature vector (vision + sensors) on `/plant/features` for ML.

## Prerequisites

- PHP-06 complete

## Acceptance Criteria

- [x] Documented schema v1.0 (`FEATURE_SCHEMA.md`)
- [x] Vision features from CV pipeline + optional sensor channels
- [x] ROS `feature_publisher` → `/plant/features` (JSON String)
- [x] Golden fixture tests: ranges + stability on fixed image
- [x] Missing sensors stored as `null`

## Tests

```bash
python -m pytest tests/unit/test_features.py -q
```
