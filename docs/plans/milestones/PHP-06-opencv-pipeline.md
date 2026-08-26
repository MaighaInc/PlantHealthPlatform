# PHP-06 — OpenCV Processing Pipeline

## Goal

Implement classical CV pipeline: validate → resize → denoise → HSV segment → ROI → features → viz; publish processed + ROI images.

## Prerequisites

- PHP-05 complete

## Acceptance Criteria

- [x] Pure-Python/OpenCV `run_pipeline()` with documented stages
- [x] Algorithm writeups in `docs/design/CV_ALGORITHMS.md`
- [x] ROS node `cv_pipeline` subscribes `/camera/image_raw`
- [x] Publishes `/camera/image_processed` and `/plant/roi`
- [x] Tunable HSV/blur/size parameters
- [x] Unit tests on synthetic + sample plant image

## Tests

```bash
export PYTHONPATH=ros2_ws/src/plant_health_status:ros2_ws/src/plant_health_sensors:ros2_ws/src/plant_health_camera:ros2_ws/src/plant_health_cv:shared
python -m pytest tests/unit -q
```

```bash
ros2 launch plant_health_camera camera.launch.py development_mode:=SIMULATION
ros2 launch plant_health_cv cv.launch.py
ros2 topic hz /camera/image_processed
```
