# Development Modes

> SIMULATION, DEVELOPMENT, HARDWARE, and PRODUCTION runtime modes

## Modes

| Mode | Purpose |
|------|---------|
| **SIMULATION** | CI, automated tests, deterministic demos |
| **DEVELOPMENT** | Local dev with partial hardware |
| **HARDWARE** | Real sensors, camera, Raspberry Pi GPIO |
| **PRODUCTION** | Hardened config, auth, monitoring, controlled deploy |

## Mode Matrix

| Component | SIMULATION | DEVELOPMENT | HARDWARE | PRODUCTION |
|-----------|------------|-------------|----------|------------|
| Sensors | virtual | virtual/mock | real | real |
| Camera | sample images | USB camera | real | real |
| GPIO | MockGPIO | MockGPIO | RaspberryPiGPIO | hardened + auth |
| Database | local/test | local | local/remote | managed PostgreSQL |
| Auth | disabled/minimal | disabled/minimal | optional | required |

## SIMULATION

- Virtual sensors with configurable noise
- Mock GPIO
- Sample/static images
- Deterministic test data

## DEVELOPMENT

- USB camera
- Virtual or mock sensors
- Mock GPIO

## HARDWARE

- Real sensors (BME280, DHT, soil moisture, etc.)
- Real camera
- Raspberry Pi GPIO

## PRODUCTION

- Hardened configuration
- Authentication and authorization
- Monitoring and persistent storage
- Controlled deployment process

## Implementation

Mode selection via configuration (`DEVELOPMENT_MODE` or equivalent). Same interfaces (`SensorInterface`, `GPIOInterface`) across all modes.

## Related Docs

- [../design/HARDWARE_ABSTRACTION.md](../design/HARDWARE_ABSTRACTION.md)
- [CONFIGURATION.md](./CONFIGURATION.md)
- [TESTING.md](./TESTING.md)
