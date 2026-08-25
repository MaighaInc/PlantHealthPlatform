# Testing Strategy

> Unit, integration, E2E, and hardware-free CI for PlantHealthPlatform

## Every Milestone Requires Tests

Scope-appropriate tests are mandatory — a milestone is not complete without them.

## Unit Tests

Test in isolation:

- Sensor value conversion
- CV algorithms and feature extraction
- ML preprocessing
- Decision logic and irrigation safety rules
- API service layer

Framework: **pytest** (Python), Vitest/Jest equivalent (frontend when added).

## Integration Tests

Test component interaction:

```text
ROS node → ROS node
API → database
backend → ML inference service
```

## End-to-End (eventually)

```text
camera → ROS → CV → ML → health → decision → safety → GPIO mock
  → database → API → dashboard
```

## Hardware-Free CI

CI must **never** depend on a physical Raspberry Pi.

Use:

```text
MockGPIO
VirtualSensor
SimulatedCamera / sample images
```

The same interfaces must support real and simulated implementations.

## Regression Testing

Before declaring a milestone complete:

```text
New Tests + Existing Tests + Integration Tests
```

If behavior intentionally changes: document, update tests, explain architecture reason.

## CI/CD Target (PHP-25)

Pipeline should run:

```text
lint → type check → unit tests → integration tests → build
```

ROS packages must build in CI. ML pipeline must perform at least smoke validation.

## Performance Baselines

Measure before optimizing:

- Camera FPS, ROS message frequency
- Image processing and ML inference latency
- API and database query latency
- Memory and CPU utilization

## Related Docs

- [MILESTONE_COMPLETION.md](./MILESTONE_COMPLETION.md)
- [DEVELOPMENT_MODES.md](./DEVELOPMENT_MODES.md)
- [../plans/CAPSTONE_SCENARIOS.md](../plans/CAPSTONE_SCENARIOS.md)
