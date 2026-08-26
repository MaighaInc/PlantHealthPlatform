# Feature Schema (PHP-10)

> Stable feature vector published on `/plant/features` for ML and dashboards.

**Schema version:** `1.0`  
**Message:** `std_msgs/String` containing JSON

```json
{
  "schema_version": "1.0",
  "timestamp_iso": "2026-08-25T18:30:00.000000Z",
  "source": "plant_health_cv",
  "features": {
    "leaf_area": 1234.0,
    "green_pixel_ratio": 0.21,
    "mean_hue": 55.0,
    "mean_saturation": 120.0,
    "mean_value": 140.0,
    "contour_area": 1100.0,
    "bbox_x": 10.0,
    "bbox_y": 12.0,
    "bbox_w": 80.0,
    "bbox_h": 90.0,
    "centroid_x": 50.0,
    "centroid_y": 55.0,
    "soil_moisture": 41.2,
    "temperature": 27.8,
    "humidity": 63.4,
    "light": 812.0,
    "co2": 420.0
  }
}
```

## Vision features

| Key | Meaning |
|-----|---------|
| `leaf_area` | Count of mask pixels |
| `green_pixel_ratio` | leaf_area / image pixels |
| `mean_hue` / `mean_saturation` / `mean_value` | HSV means on mask |
| `contour_area` | Largest contour area |
| `bbox_*` | Bounding box of largest contour |
| `centroid_*` | Contour centroid |

## Sensor features

Optional; `null` when unavailable (never invented).

| Key | Topic source |
|-----|----------------|
| `soil_moisture` | `/soil/moisture` |
| `temperature` | `/environment/temperature` |
| `humidity` | `/environment/humidity` |
| `light` | `/environment/light` |
| `co2` | `/environment/co2` |

## Code

- Schema: `plant_health_cv/features.py`
- Publisher node: `feature_publisher`
- CV stages: [CV_ALGORITHMS.md](./CV_ALGORITHMS.md)
