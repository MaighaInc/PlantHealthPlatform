"""Launch rule-based health engine."""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description() -> LaunchDescription:
    default_params = os.path.join(
        get_package_share_directory("plant_health_health"),
        "config",
        "health_params.yaml",
    )
    return LaunchDescription(
        [
            DeclareLaunchArgument("params_file", default_value=default_params),
            DeclareLaunchArgument("soil_dry_threshold", default_value="30.0"),
            DeclareLaunchArgument("temp_hot_threshold", default_value="32.0"),
            Node(
                package="plant_health_health",
                executable="health_engine",
                name="health_engine",
                output="screen",
                parameters=[
                    LaunchConfiguration("params_file"),
                    {
                        "soil_dry_threshold": ParameterValue(
                            LaunchConfiguration("soil_dry_threshold"), value_type=float
                        ),
                        "temp_hot_threshold": ParameterValue(
                            LaunchConfiguration("temp_hot_threshold"), value_type=float
                        ),
                    },
                ],
            ),
        ]
    )
