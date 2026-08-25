# Configuration

> Environment-specific settings for PlantHealthPlatform

## Policy

Never hard-code environment-specific values. Never commit secrets.

## Configuration Sources

```text
.env / .env.example
config.yaml
ROS parameters
Launch file arguments
```

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

## ROS Parameters

Use ROS 2 parameters for node runtime configuration (PHP-02). Validate parameter values at startup.

## Secrets

- Database credentials
- API keys
- Production auth tokens

Store in environment or secret manager — not in source control.

## Related Docs

- [DEVELOPMENT_MODES.md](./DEVELOPMENT_MODES.md)
- [../design/ROS_ARCHITECTURE.md](../design/ROS_ARCHITECTURE.md)
