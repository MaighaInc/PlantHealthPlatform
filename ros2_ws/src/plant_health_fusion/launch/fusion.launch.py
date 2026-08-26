"""Launch plant health fusion node."""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description() -> LaunchDescription:
    default_params = os.path.join(
        get_package_share_directory("plant_health_fusion"),
        "config",
        "fusion_params.yaml",
    )
    return LaunchDescription(
        [
            DeclareLaunchArgument("params_file", default_value=default_params),
            DeclareLaunchArgument("publish_period_sec", default_value="1.0"),
            Node(
                package="plant_health_fusion",
                executable="fusion_engine",
                name="plant_health_fusion",
                output="screen",
                parameters=[
                    LaunchConfiguration("params_file"),
                    {
                        "publish_period_sec": ParameterValue(
                            LaunchConfiguration("publish_period_sec"),
                            value_type=float,
                        ),
                    },
                ],
            ),
        ]
    )
