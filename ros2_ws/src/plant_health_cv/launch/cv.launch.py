"""Launch CV pipeline node."""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description() -> LaunchDescription:
    default_params = os.path.join(
        get_package_share_directory("plant_health_cv"),
        "config",
        "cv_params.yaml",
    )
    return LaunchDescription(
        [
            DeclareLaunchArgument("params_file", default_value=default_params),
            Node(
                package="plant_health_cv",
                executable="cv_pipeline",
                name="cv_pipeline",
                output="screen",
                parameters=[LaunchConfiguration("params_file")],
            ),
        ]
    )
