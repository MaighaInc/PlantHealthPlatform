# Hardware Abstraction

> Sensor and GPIO interfaces for testable, mode-aware hardware access

## Principle

Hardware must never dominate application architecture. Application code uses interfaces; implementations swap by development mode.

## Sensor Interface

```text
SensorInterface
 ├── VirtualSensor       (simulation — configurable noise, outliers)
 ├── MockSensor          (deterministic tests)
 └── RealSensorAdapter   (BME280, DHT, etc.)
```

Usage:

```python
reading = sensor.read()
```

Not direct register/I2C calls in business logic.

## Virtual Sensor Framework (PHP-03)

Support for soil moisture, temperature, humidity, light, CO2 with:

- Configurable sampling rate
- Min/max bounds
- Noise and invalid values
- Outlier injection (for testing)

## GPIO Interface

```text
GPIOInterface
 ├── MockGPIO
 └── RaspberryPiGPIO
```

## Development Modes

| Mode | Sensors | Camera | GPIO |
|------|---------|--------|------|
| SIMULATION | virtual | sample images | mock |
| DEVELOPMENT | virtual/mock | USB camera | mock |
| HARDWARE | real | real | Raspberry Pi |
| PRODUCTION | real | real | hardened + auth |

## CI Requirement

CI must never depend on physical Raspberry Pi. Same interfaces support real and simulated implementations.

## Related Docs

- [IRRIGATION_SAFETY.md](./IRRIGATION_SAFETY.md)
- [../development/DEVELOPMENT_MODES.md](../development/DEVELOPMENT_MODES.md)
- [../plans/ROADMAP.md](../plans/ROADMAP.md) — PHP-03, PHP-04, PHP-17
