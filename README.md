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
export PYTHONPATH=ros2_ws/src/plant_health_status
python -m pytest tests/unit -q
# or: bash scripts/dev/run_unit_tests.sh
```

### ROS 2 nodes (Humble host)

```bash
cd ros2_ws
source /opt/ros/humble/setup.bash
colcon build --symlink-install --packages-select plant_health_status
source install/setup.bash
ros2 launch plant_health_status status.launch.py
```

Inspect:

```bash
ros2 topic list
ros2 topic echo /system/status
ros2 node list
```

## Configuration

Copy [`.env.example`](./.env.example) to `.env`. Never commit secrets.

## ROS Topics (current)

| Topic | Message | Package |
|-------|---------|---------|
| `/system/status` | `std_msgs/String` | `plant_health_status` |

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

- PHP-02: parameter validation and richer runtime configuration
- PHP-03+: virtual sensors on top of this status foundation
