# PHP-05 — Camera Integration

## Goal

Add camera acquisition with `CameraInterface`, SIMULATION sample frames, USB backend, validation, and ROS publish on `/camera/image_raw`.

## Prerequisites

- PHP-04 complete

## Acceptance Criteria

- [x] `CameraInterface` with Simulated / USB / Mock implementations
- [x] Mode-aware factory (`SIMULATION` → simulated; `DEVELOPMENT+` → USB by default)
- [x] Frame validation (None, empty, blank rejected)
- [x] Acquisition timestamps on frames; drops/invalids logged (not silent)
- [x] Clean `release()` on shutdown; USB reconnect policy documented in code
- [x] Launch + YAML; unit tests without ROS
- [x] Topic `/camera/image_raw` documented

## Architecture Impact

```text
CameraInterface
 ├── SimulatedCamera
 ├── UsbCamera
 └── MockCamera
        ↑
   create_camera(mode, backend)
        ↑
   CameraPublisherNode → /camera/image_raw (sensor_msgs/Image)
```

## Reconnect policy (USB)

After `max_consecutive_failures` failed reads: release → wait `reconnect_delay_sec` → reopen once. Failures return `None` for the node to WARN-log.

## Tests

```bash
export PYTHONPATH=ros2_ws/src/plant_health_status:ros2_ws/src/plant_health_sensors:ros2_ws/src/plant_health_camera:shared
python -m pytest tests/unit -q
```

ROS host:

```bash
ros2 launch plant_health_camera camera.launch.py development_mode:=SIMULATION
ros2 topic echo /camera/image_raw --once
```

## Intern Learning Outcomes

- Why acquisition timestamp ≠ ROS message arrival time?
- Why reject blank frames before CV/ML?
