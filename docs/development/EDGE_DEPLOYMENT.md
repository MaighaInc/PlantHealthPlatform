# Edge / Raspberry Pi Deployment (PHP-28)

## HARDWARE mode bringup

```bash
# On Raspberry Pi (Ubuntu 22.04 + ROS 2 Humble)
export DEVELOPMENT_MODE=HARDWARE
source /opt/ros/humble/setup.bash
cd ~/PlantHealthPlatform/ros2_ws
colcon build --symlink-install
source install/setup.bash

ros2 launch plant_health_sensors virtual_sensors.launch.py  # replace with real drivers when ready
ros2 launch plant_health_camera camera.launch.py development_mode:=HARDWARE
ros2 launch plant_health_irrigation safety.launch.py
ros2 launch plant_health_irrigation irrigation.launch.py development_mode:=HARDWARE gpio_backend:=rpi
```

Point the dashboard/API `DATABASE_URL` at the server tier (Docker host). Safety rules remain enforced regardless of GPIO backend.

## Networking

- Pi publishes ROS locally; optional bridge/VPN to lab network
- API/UI via `docker compose` on server (ADR-0006)
