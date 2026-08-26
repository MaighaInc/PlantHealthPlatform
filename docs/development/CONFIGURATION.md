# Configuration

> Environment-specific settings for PlantHealthPlatform

## Policy

Never hard-code environment-specific values. Never commit secrets.

## Configuration Sources

```text
.env / .env.example
config.yaml / package config/*.yaml
ROS parameters
Launch file arguments
```

| Source | Use for |
|--------|---------|
| `.env` | Process-wide mode, secrets, DB URLs, log level |
| ROS parameters | Per-node runtime (periods, topics, thresholds) |
| Launch arguments | Operator overrides without editing YAML |

## Example Variables

```text
DATABASE_URL
MODEL_PATH
CAMERA_INDEX
CAMERA_WIDTH
CAMERA_HEIGHT
CAMERA_FPS
SOIL_THRESHOLD
IRRIGATION_MAX_SECONDS
LOG_LEVEL
DEVELOPMENT_MODE          # SIMULATION | DEVELOPMENT | HARDWARE | PRODUCTION
```

Copy [`.env.example`](../../.env.example) to `.env`. Helpers: `shared/plant_health_common` (`parse_development_mode`, `load_dotenv_file`).

## ROS Parameters (PHP-02)

`plant_health_status` validates parameters at startup and **rejects** invalid values (node fails to start).

| Node | Parameter | Constraints | Default |
|------|-----------|-------------|---------|
| `status_publisher` | `publish_period_sec` | `0.05` … `60.0` | `1.0` |
| `status_publisher` | `topic` | absolute ROS name | `/system/status` |
| `status_publisher` | `source` | non-empty, no whitespace | `plant_health_status` |
| `status_subscriber` | `topic` | absolute ROS name | `/system/status` |

YAML defaults: `ros2_ws/src/plant_health_status/config/status_params.yaml`

```bash
# Override period without code changes
ros2 launch plant_health_status status.launch.py publish_period_sec:=0.5

# Inspect at runtime (ROS host)
ros2 param list /status_publisher
ros2 param get /status_publisher publish_period_sec
```

## Secrets

- Database credentials
- API keys
- Production auth tokens

Store in environment or secret manager — not in source control.

## Related Docs

- [DEVELOPMENT_MODES.md](./DEVELOPMENT_MODES.md)
- [../design/ROS_ARCHITECTURE.md](../design/ROS_ARCHITECTURE.md)
- [../plans/milestones/PHP-02-ros-parameters.md](../plans/milestones/PHP-02-ros-parameters.md)
