"""Launch dataset logger node."""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description() -> LaunchDescription:
    default_params = os.path.join(
        get_package_share_directory("plant_health_dataset"),
        "config",
        "dataset_logger.yaml",
    )
    return LaunchDescription(
        [
            DeclareLaunchArgument("params_file", default_value=default_params),
            DeclareLaunchArgument("plant_id", default_value="plant_001"),
            Node(
                package="plant_health_dataset",
                executable="dataset_logger",
                name="dataset_logger",
                output="screen",
                parameters=[
                    LaunchConfiguration("params_file"),
                    {"plant_id": LaunchConfiguration("plant_id")},
                ],
            ),
        ]
    )
