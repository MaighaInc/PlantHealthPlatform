# ROS 2 workspace for PlantHealthPlatform

Build and run on a host with **ROS 2 Humble** (Ubuntu 22.04 or WSL2):

```bash
cd ros2_ws
source /opt/ros/humble/setup.bash
rosdep install --from-paths src -y --ignore-src  # first time
colcon build --symlink-install --packages-select plant_health_status
source install/setup.bash
ros2 launch plant_health_status status.launch.py
```

Inspect topics:

```bash
ros2 topic list
ros2 topic echo /system/status
ros2 node list
```

Packages live under `src/` using the `plant_health_*` namespace.

Current packages:

- `plant_health_status` — system heartbeat
- `plant_health_sensors` — virtual soil/environment sensors
- `plant_health_camera` — camera acquisition → `/camera/image_raw`
- `plant_health_cv` — OpenCV pipeline → processed + ROI
- `plant_health_dataset` — log images + metadata under `ml/datasets/`

```bash
colcon build --symlink-install --packages-select plant_health_status plant_health_sensors plant_health_camera plant_health_cv plant_health_dataset
ros2 launch plant_health_dataset dataset_logger.launch.py
```

