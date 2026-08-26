"""Launch status publisher and subscriber with YAML parameters."""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description() -> LaunchDescription:
    default_params = os.path.join(
        get_package_share_directory("plant_health_status"),
        "config",
        "status_params.yaml",
    )

    params_file_arg = DeclareLaunchArgument(
        "params_file",
        default_value=default_params,
        description="Path to ROS parameter YAML for status nodes",
    )
    publish_period_arg = DeclareLaunchArgument(
        "publish_period_sec",
        default_value="1.0",
        description="Heartbeat period in seconds (overrides YAML)",
    )

    params_file = LaunchConfiguration("params_file")
    publish_period_sec = LaunchConfiguration("publish_period_sec")

    return LaunchDescription(
        [
            params_file_arg,
            publish_period_arg,
            Node(
                package="plant_health_status",
                executable="status_publisher",
                name="status_publisher",
                output="screen",
                parameters=[
                    params_file,
                    {
                        "publish_period_sec": ParameterValue(
                            publish_period_sec, value_type=float
                        )
                    },
                ],
            ),
            Node(
                package="plant_health_status",
                executable="status_subscriber",
                name="status_subscriber",
                output="screen",
                parameters=[params_file],
            ),
        ]
    )
