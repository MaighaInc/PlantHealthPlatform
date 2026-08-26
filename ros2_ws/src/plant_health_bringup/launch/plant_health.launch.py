"""Unified SIMULATION bringup launch (PHP-29) — compose ROS nodes."""

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare


def generate_launch_description() -> LaunchDescription:
    def incl(pkg: str, launch_file: str):
        return IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                PathJoinSubstitution([FindPackageShare(pkg), "launch", launch_file])
            )
        )

    return LaunchDescription(
        [
            incl("plant_health_status", "status.launch.py"),
            incl("plant_health_sensors", "virtual_sensors.launch.py"),
            incl("plant_health_camera", "camera.launch.py"),
            incl("plant_health_cv", "cv.launch.py"),
            incl("plant_health_health", "health.launch.py"),
            incl("plant_health_inference", "inference.launch.py"),
            incl("plant_health_fusion", "fusion.launch.py"),
            incl("plant_health_decision", "decision.launch.py"),
            incl("plant_health_irrigation", "safety.launch.py"),
            incl("plant_health_irrigation", "irrigation.launch.py"),
        ]
    )
