"""Launch ML inference node (SIMULATION-friendly mock backend by default)."""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description() -> LaunchDescription:
    default_params = os.path.join(
        get_package_share_directory("plant_health_inference"),
        "config",
        "inference_params.yaml",
    )
    return LaunchDescription(
        [
            DeclareLaunchArgument("params_file", default_value=default_params),
            DeclareLaunchArgument("backend", default_value="mock"),
            DeclareLaunchArgument("confidence_threshold", default_value="0.55"),
            DeclareLaunchArgument("model_path", default_value=""),
            Node(
                package="plant_health_inference",
                executable="inference_engine",
                name="plant_health_inference",
                output="screen",
                parameters=[
                    LaunchConfiguration("params_file"),
                    {
                        "backend": LaunchConfiguration("backend"),
                        "model_path": LaunchConfiguration("model_path"),
                        "confidence_threshold": ParameterValue(
                            LaunchConfiguration("confidence_threshold"),
                            value_type=float,
                        ),
                    },
                ],
            ),
        ]
    )
