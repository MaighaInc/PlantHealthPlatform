# ROS 2 Architecture

> Topics, messages, nodes, and bringup conventions for PlantHealthPlatform

## Package Namespace

Use `plant_health_*` for ROS packages. Do **not** use `php_*`.

Recommended packages:

```text
plant_health_status/
plant_health_sensors/
plant_health_camera/
plant_health_cv/
plant_health_ml/
plant_health_inference/
plant_health_decision/
plant_health_irrigation/
plant_health_bringup/
```

## Active Topics

| Topic | Type | Direction | Introduced | Notes |
|-------|------|-----------|------------|-------|
| `/system/status` | `std_msgs/String` | pub: `status_publisher` / sub: `status_subscriber` | PHP-01 | Heartbeat payload `state=…;seq=…;source=…;ts=…` |
| `/soil/moisture` | `std_msgs/Float32` | pub: `virtual_sensor_publisher` | PHP-03 | % moisture; NaN = invalid |
| `/environment/temperature` | `std_msgs/Float32` | pub: `virtual_sensor_publisher` | PHP-03 | °C; NaN = invalid |
| `/environment/humidity` | `std_msgs/Float32` | pub: `virtual_sensor_publisher` | PHP-03 | % RH; NaN = invalid |
| `/environment/light` | `std_msgs/Float32` | pub: `virtual_sensor_publisher` | PHP-03 | lux-like; NaN = invalid |
| `/environment/co2` | `std_msgs/Float32` | pub: `virtual_sensor_publisher` | PHP-03 | ppm; NaN = invalid |
| `/camera/image_raw` | `sensor_msgs/Image` | pub: `camera_publisher` | PHP-05 | BGR8; acquisition ts logged |
| `/camera/image_processed` | `sensor_msgs/Image` | pub: `cv_pipeline` | PHP-06 | Viz overlay (contours/bbox) |
| `/plant/roi` | `sensor_msgs/Image` | pub: `cv_pipeline` | PHP-06 | Cropped largest green region |

## Planned Topic Structure

```text
/system/status                 ← active (PHP-01)
/soil/moisture                 ← active (PHP-03)
/environment/temperature       ← active (PHP-03)
/environment/humidity          ← active (PHP-03)
/environment/light             ← active (PHP-03)
/environment/co2               ← active (PHP-03)
/environment/pressure          ← planned
/camera/image_raw              ← active (PHP-05)
/camera/image_processed        ← active (PHP-06)
/plant/roi                     ← active (PHP-06)
/plant/features                ← planned (PHP-10)
/plant/health
/plant/disease_prediction

/irrigation/command
/irrigation/status

/diagnostics
```

Entries without an “Active Topics” row are **planned**. Before adding a topic:

1. Inspect existing topic architecture
2. Determine whether an existing topic can be reused
3. Follow naming conventions
4. Document the new topic

Never randomly create duplicate topics.

## Message Design

Prefer standard messages:

- `std_msgs`
- `sensor_msgs`
- `geometry_msgs`
- `example_interfaces`

Introduce custom messages only when justified. Example custom message:

```text
PlantHealth.msg
  float32 health_score
  string health_status
  string disease
  float32 confidence
  builtin_interfaces/Time timestamp
```

Before creating a custom message, document:

- Why standard messages are insufficient
- What information is required
- Compatibility implications

## Unified Bringup

Package: `plant_health_bringup`

Target launch:

```bash
ros2 launch plant_health_bringup plant_health.launch.py
```

Should eventually launch (mode-dependent):

- camera
- sensor nodes
- CV
- ML inference
- health engine
- decision engine
- irrigation
- diagnostics

Parameters must remain configurable via ROS parameters and external config files.

## Logging

ROS nodes use ROS logging — not scattered `print()` statements.

Examples:

```text
INFO  Camera initialized
WARN  Soil sensor returned invalid value
ERROR Camera frame acquisition failed
```

## Related Docs

- [CV_PIPELINE.md](./CV_PIPELINE.md)
- [../architecture/TECH_STACK.md](../architecture/TECH_STACK.md)
- [../development/CONFIGURATION.md](../development/CONFIGURATION.md)
