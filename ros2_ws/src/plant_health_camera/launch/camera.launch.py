"""Launch camera publisher with YAML parameters."""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description() -> LaunchDescription:
    default_params = os.path.join(
        get_package_share_directory("plant_health_camera"),
        "config",
        "camera_params.yaml",
    )

    return LaunchDescription(
        [
            DeclareLaunchArgument("params_file", default_value=default_params),
            DeclareLaunchArgument("development_mode", default_value="SIMULATION"),
            DeclareLaunchArgument("camera_backend", default_value="auto"),
            DeclareLaunchArgument("publish_period_sec", default_value="0.2"),
            Node(
                package="plant_health_camera",
                executable="camera_publisher",
                name="camera_publisher",
                output="screen",
                parameters=[
                    LaunchConfiguration("params_file"),
                    {
                        "development_mode": LaunchConfiguration("development_mode"),
                        "camera_backend": LaunchConfiguration("camera_backend"),
                        "publish_period_sec": ParameterValue(
                            LaunchConfiguration("publish_period_sec"),
                            value_type=float,
                        ),
                    },
                ],
            ),
        ]
    )
