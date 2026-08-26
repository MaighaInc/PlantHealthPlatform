# Data Pipeline

> Sensor, image, and metadata flow through PlantHealthPlatform

## End-to-End Flow

```text
Sensors
   │
   ▼
ROS 2
   │
   ├───────────────► Database
   │
   ▼
Camera
   │
   ▼
OpenCV
   │
   ▼
Features
   │
   ▼
ML
   │
   ▼
Plant Health
```

## Timestamp Rules

- Sensor and image data must be timestamped at acquisition.
- Never assume `message arrival time == measurement time`.
- Metadata synchronization (PHP-08) must handle missing and delayed data.

## Synchronization (PHP-08)

Combine:

```text
image + sensor measurements + timestamps + plant metadata
```

### Join algorithm

For each sensor channel, select the sample with minimum `|t_sensor − t_image|` **only if** that delta is within `sync_window_sec`. Otherwise store `null` and list the channel under `missing` (and `stale_candidates` if out-of-window samples existed).

Logged in dataset `extra`:

```text
sensor_sync=acquisition_window_php08
sync_status=complete|partial|none
missing_sensors, stale_candidates, sensor_deltas_sec, …
```

### Clock assumptions

1. Prefer acquisition timestamps on each sample.
2. Never assume message arrival time == measurement time.
3. Bare `std_msgs/Float32` sensor topics have no header — the ROS dataset logger stamps them as `receive_approx` with the local ROS clock (acceptable for same-host SIMULATION; replace with stamped messages for distributed hardware).
4. Image time uses `sensor_msgs/Image.header.stamp`.

Library: `ml/plant_health_data/sync.py`.

## Dataset Management

Reproducible datasets — do not rely on manual filenames.

Layout (PHP-07):

```text
ml/datasets/<name>/
├── images/
├── labels/
├── metadata/records.jsonl
└── manifests/manifest.json
```

- Filenames: `{plant_id}_{seq:06d}_{compact_ts}.png`
- Never overwrite an existing image path
- Manifest tracks `record_count` and layout paths
- Library: `ml/plant_health_data`; ROS node: `plant_health_dataset`

Manifest-driven splits for train/test/validation (later milestones).

## Data Quality Gate

Invalid data is rejected before training or fusion — see [ML_PIPELINE.md](./ML_PIPELINE.md).

## Sensor Fusion Inputs

Eventually combine:

```text
soil moisture, temperature, humidity, light, camera features, ML prediction
```

into a unified health/decision representation.

## Related Docs

- [CV_PIPELINE.md](./CV_PIPELINE.md)
- [ML_PIPELINE.md](./ML_PIPELINE.md)
- [DATABASE.md](./DATABASE.md)
