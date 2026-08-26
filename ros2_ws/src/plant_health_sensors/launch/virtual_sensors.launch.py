"""Launch virtual soil and environment sensors."""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description() -> LaunchDescription:
    default_params = os.path.join(
        get_package_share_directory("plant_health_sensors"),
        "config",
        "virtual_sensors.yaml",
    )

    params_file_arg = DeclareLaunchArgument(
        "params_file",
        default_value=default_params,
        description="YAML parameters for virtual sensors",
    )
    period_arg = DeclareLaunchArgument(
        "sample_period_sec",
        default_value="1.0",
        description="Sample period seconds",
    )
    invalid_arg = DeclareLaunchArgument(
        "invalid_probability",
        default_value="0.0",
        description="Probability of injecting invalid samples [0,1]",
    )

    return LaunchDescription(
        [
            params_file_arg,
            period_arg,
            invalid_arg,
            Node(
                package="plant_health_sensors",
                executable="virtual_sensor_publisher",
                name="virtual_sensor_publisher",
                output="screen",
                parameters=[
                    LaunchConfiguration("params_file"),
                    {
                        "sample_period_sec": ParameterValue(
                            LaunchConfiguration("sample_period_sec"),
                            value_type=float,
                        ),
                        "invalid_probability": ParameterValue(
                            LaunchConfiguration("invalid_probability"),
                            value_type=float,
                        ),
                    },
                ],
            ),
        ]
    )
