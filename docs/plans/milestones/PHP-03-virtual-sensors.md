# PHP-03 — Virtual Sensor Framework

## Goal

Add configurable virtual soil/environment sensors that publish on canonical ROS topics for SIMULATION — with noise, outliers, and invalid injection — without physical hardware.

## Prerequisites

- PHP-02 complete

## Acceptance Criteria

- [x] Virtual sensors: soil moisture, temperature, humidity, light, CO₂
- [x] Configurable period, bounds, noise, outlier/invalid probabilities, seed
- [x] Publish `std_msgs/Float32` on `/soil/moisture`, `/environment/{temperature,humidity,light,co2}`
- [x] Invalid samples published as NaN + WARN log
- [x] Deterministic seed unit tests; invalid injection tests
- [x] Launch + YAML parameters; docs updated

## Architecture Impact

```text
VirtualSensorConfig → VirtualSensor.read() → SensorReading
        ↓
VirtualSensorPublisherNode → Float32 topics
```

Feeds PHP-04 `SensorInterface` (virtual adapter will wrap `VirtualSensor`).

## Tests

```bash
export PYTHONPATH=ros2_ws/src/plant_health_status:ros2_ws/src/plant_health_sensors:shared
python -m pytest tests/unit -q
```

ROS host:

```bash
ros2 launch plant_health_sensors virtual_sensors.launch.py
ros2 topic echo /soil/moisture
ros2 launch plant_health_sensors virtual_sensors.launch.py invalid_probability:=0.2
```

## Intern Learning Outcomes

- Why simulate sensors before buying hardware?
- How do seeds make flaky sensor tests deterministic?
- Why represent invalid as NaN rather than a magic number like -999?
