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

Use synchronization windows; document clock differences and delayed messages.

## Dataset Management

Reproducible datasets — do not rely on manual filenames.

Manifest-driven splits for train/test/validation.

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
