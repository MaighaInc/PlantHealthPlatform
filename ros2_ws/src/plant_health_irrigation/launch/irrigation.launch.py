"""Launch irrigation GPIO actuator (MockGPIO in SIMULATION/DEVELOPMENT)."""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description() -> LaunchDescription:
    default_params = os.path.join(
        get_package_share_directory("plant_health_irrigation"),
        "config",
        "irrigation_params.yaml",
    )
    return LaunchDescription(
        [
            DeclareLaunchArgument("params_file", default_value=default_params),
            DeclareLaunchArgument("development_mode", default_value="SIMULATION"),
            DeclareLaunchArgument("gpio_backend", default_value="auto"),
            Node(
                package="plant_health_irrigation",
                executable="irrigation_actuator",
                name="plant_health_irrigation",
                output="screen",
                parameters=[
                    LaunchConfiguration("params_file"),
                    {
                        "development_mode": LaunchConfiguration("development_mode"),
                        "gpio_backend": LaunchConfiguration("gpio_backend"),
                    },
                ],
            ),
        ]
    )
