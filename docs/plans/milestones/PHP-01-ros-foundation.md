# PHP-01 — ROS 2 Publisher/Subscriber Foundation

## Goal

Establish the ROS 2 workspace and a first `plant_health_*` package that demonstrates publisher/subscriber lifecycle, ROS logging, and documented topics — without requiring physical hardware.

## Prerequisites

- Repo documentation present
- ADR-0001: ROS 2 Humble selected
- Python 3.10+ available for hardware-free unit tests
- ROS 2 Humble (WSL/Linux) for full node smoke tests

## Acceptance Criteria

- [x] `ros2_ws/src/plant_health_status` ament_python package exists
- [x] Status publisher publishes `/system/status`
- [x] Status subscriber receives and logs messages
- [x] Pure-Python heartbeat formatting unit-tested without ROS
- [x] Launch file can start both nodes (on ROS host)
- [x] `.env.example` and tooling (`pyproject.toml`) present
- [x] ADR-0001 recorded; ROS_ARCHITECTURE / README updated
- [x] Milestone docs and RUNNING_LOG started

## Architecture Impact

```text
plant_health_status
  ├── StatusPublisherNode  → /system/status (std_msgs/String)
  └── StatusSubscriberNode ← /system/status
```

Introduces package naming `plant_health_*` and first canonical topic `/system/status`.

## Files to Create/Modify

See git diff for this milestone. Key paths:

- `ros2_ws/src/plant_health_status/`
- `tests/unit/test_heartbeat.py`
- `docs/architecture/adr/0001-ros2-distro-humble.md`
- `.env.example`, `pyproject.toml`

## Interfaces

- Topic: `/system/status` — `std_msgs/msg/String` payload from `format_status_message`
- No custom messages yet (justified later if schema grows)

## Tests

```bash
# Hardware-free (Windows or Linux without ROS)
pip install -e ".[dev]"   # or: pip install pytest
pytest tests/unit -q
```

```bash
# On ROS 2 Humble host (WSL/Ubuntu)
cd ros2_ws && colcon build --packages-select plant_health_status
source install/setup.bash
ros2 launch plant_health_status status.launch.py
# In another terminal:
ros2 topic echo /system/status
```

## Documentation Updates

- README Running / ROS Topics sections
- ROS_ARCHITECTURE topic note for `/system/status`
- This milestone plan; RUNNING_LOG

## ADRs

- [0001-ros2-distro-humble.md](../../architecture/adr/0001-ros2-distro-humble.md)

## Known Risks

- Native ROS not available on Windows → develop nodes in repo; run under WSL
- `rclpy` import fails outside ROS env → unit tests stay pure-Python

## Intern Learning Outcomes

- What is a ROS 2 node / publisher / subscriber?
- Why `/system/status` uses a standard message first?
- How does lifecycle (init → spin → shutdown) work?
- How do we test without hardware?
