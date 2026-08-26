# PlantHealthPlatform (PHP)

**Plant Health Robotics, Computer Vision, Machine Learning & Full-Stack Engineering**

One unified production-oriented platform incrementally built through ~30 development milestones, culminating in the **Plant Health System (PHS)**.

## Naming

| Term | Meaning |
|------|---------|
| **PlantHealthPlatform (PHP)** | Overall software platform and repository |
| **Plant Health System (PHS)** | Integrated running system |
| `plant_health_*` | Preferred ROS/Python package namespace |
| Do **not** use `php_*` | Conflicts with PHP programming language |

## Documentation

All design, plan, and development docs live under [`docs/`](./docs/).

**Start here:** [`docs/INDEX.md`](./docs/INDEX.md)

| Doc | Purpose |
|-----|---------|
| [docs/design/COMPREHENSIVE_DESIGN.md](./docs/design/COMPREHENSIVE_DESIGN.md) | Unified system design (all concepts) |
| [docs/plans/IMPLEMENTATION_PLAN.md](./docs/plans/IMPLEMENTATION_PLAN.md) | Unified delivery plan (PHP-01 … PHP-30) |
| [docs/prompt/MASTER_PROMPT.md](./docs/prompt/MASTER_PROMPT.md) | Coding-agent constitution (read before implementing) |

## Core Principle

> Build **ONE system incrementally** — never 30 disconnected projects.

Every milestone extends the same platform, preserves regression behavior, and moves PHS closer to production readiness.

## Prerequisites

- Python 3.10+ (unit tests on any OS)
- ROS 2 **Humble** on Ubuntu 22.04 or WSL2 for building/running nodes ([ADR-0001](./docs/architecture/adr/0001-ros2-distro-humble.md))

## Installation (tests)

```bash
python -m pip install pytest
# or: python -m pip install -e ".[dev]"
```

## Running

### Hardware-free unit tests (no ROS)

```bash
export PYTHONPATH=ros2_ws/src/plant_health_status:ros2_ws/src/plant_health_sensors:ros2_ws/src/plant_health_camera:ros2_ws/src/plant_health_cv:ros2_ws/src/plant_health_health:ml:shared
python -m pytest tests/unit -q
# or: bash scripts/dev/run_unit_tests.sh
```

### ROS 2 nodes (Humble host)

```bash
cd ros2_ws
source /opt/ros/humble/setup.bash
colcon build --symlink-install --packages-select plant_health_status plant_health_sensors plant_health_camera plant_health_cv plant_health_dataset plant_health_health
source install/setup.bash
ros2 launch plant_health_status status.launch.py
# faster heartbeat without code edits:
ros2 launch plant_health_status status.launch.py publish_period_sec:=0.5
# virtual sensors (SIMULATION):
ros2 launch plant_health_sensors virtual_sensors.launch.py
ros2 launch plant_health_sensors virtual_sensors.launch.py invalid_probability:=0.1
# camera (SIMULATION sample frames):
ros2 launch plant_health_camera camera.launch.py development_mode:=SIMULATION
# OpenCV pipeline:
ros2 launch plant_health_cv cv.launch.py
# dataset logger:
ros2 launch plant_health_dataset dataset_logger.launch.py plant_id:=plant_001
# rule-based health:
ros2 launch plant_health_health health.launch.py
ros2 topic echo /plant/health
# features (launched with CV):
ros2 launch plant_health_cv cv.launch.py
ros2 topic echo /plant/features
```

Inspect:

```bash
ros2 topic list
ros2 topic echo /system/status
ros2 topic echo /soil/moisture
ros2 topic hz /camera/image_raw
ros2 topic hz /camera/image_processed
ros2 node list
ros2 param get /status_publisher publish_period_sec
```

## Configuration

Copy [`.env.example`](./.env.example) to `.env`. Never commit secrets.

## ROS Topics (current)

| Topic | Message | Package |
|-------|---------|---------|
| `/system/status` | `std_msgs/String` | `plant_health_status` |
| `/soil/moisture` | `std_msgs/Float32` | `plant_health_sensors` |
| `/environment/temperature` | `std_msgs/Float32` | `plant_health_sensors` |
| `/environment/humidity` | `std_msgs/Float32` | `plant_health_sensors` |
| `/environment/light` | `std_msgs/Float32` | `plant_health_sensors` |
| `/environment/co2` | `std_msgs/Float32` | `plant_health_sensors` |
| `/camera/image_raw` | `sensor_msgs/Image` | `plant_health_camera` |
| `/camera/image_processed` | `sensor_msgs/Image` | `plant_health_cv` |
| `/plant/roi` | `sensor_msgs/Image` | `plant_health_cv` |
| `/plant/health` | `std_msgs/String` | `plant_health_health` |
| `/plant/features` | `std_msgs/String` (JSON) | `plant_health_cv` |

See [docs/design/ROS_ARCHITECTURE.md](./docs/design/ROS_ARCHITECTURE.md).

## Testing

See [docs/development/TESTING.md](./docs/development/TESTING.md). PHP-01 focuses on pure-Python heartbeat tests plus ROS launch smoke on a Humble host.

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `ModuleNotFoundError: rclpy` on Windows | Expected — run nodes under WSL/Ubuntu; use `pytest tests/unit` locally |
| `colcon: command not found` | Install ROS 2 Humble desktop/base and source `/opt/ros/humble/setup.bash` |
| No messages on `/system/status` | Ensure launch is running; check `ros2 node list` and QoS/topic name |

## Design Decisions

- [ADR-0001 — ROS 2 Humble](./docs/architecture/adr/0001-ros2-distro-humble.md)

## Known Limitations

- Full ROS launch smoke is not runnable on native Windows without WSL.
- `/system/status` uses `std_msgs/String` until a richer custom message is justified.

## Future Improvements

- PHP-11: classical ML baseline on feature vectors
- Stamped sensor messages (replace Float32 receive_approx)
- Wire concrete RealSensor drivers (BME280/DHT) replacing RealSensorStub
