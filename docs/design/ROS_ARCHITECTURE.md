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

## Planned Topic Structure

```text
/system/status                 ← active (PHP-01)

/environment/temperature
/environment/humidity
/environment/pressure
/environment/light

/soil/moisture

/camera/image_raw
/camera/image_processed

/plant/roi
/plant/features
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
