# Database Design

> PostgreSQL persistence for Plant Health System

## Policy

- Use PostgreSQL with migrations.
- Never require manual production schema modification.
- Backend access via Repository layer — not in HTTP handlers.

## Planned Entities

```text
plants
plant_varieties
devices
sensors
sensor_readings
images
image_metadata
plant_observations
health_predictions
ml_models
inference_results
irrigation_events
alerts
users
system_events
```

Schema will evolve — do not prematurely freeze the data model.

## Backend Layering

```text
API / Controller → Service → Repository → Database
```

## Related Docs

- [API.md](./API.md)
- [../plans/ROADMAP.md](../plans/ROADMAP.md) — PHP-19
