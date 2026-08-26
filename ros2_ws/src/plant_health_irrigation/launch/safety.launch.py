"""Launch irrigation safety gate (intent → command)."""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description() -> LaunchDescription:
    return LaunchDescription(
        [
            DeclareLaunchArgument("max_duration_sec", default_value="30.0"),
            DeclareLaunchArgument("cooldown_sec", default_value="60.0"),
            DeclareLaunchArgument("e_stop", default_value="false"),
            Node(
                package="plant_health_irrigation",
                executable="irrigation_safety",
                name="plant_health_safety",
                output="screen",
                parameters=[
                    {
                        "max_duration_sec": ParameterValue(
                            LaunchConfiguration("max_duration_sec"), value_type=float
                        ),
                        "cooldown_sec": ParameterValue(
                            LaunchConfiguration("cooldown_sec"), value_type=float
                        ),
                        "e_stop": ParameterValue(
                            LaunchConfiguration("e_stop"), value_type=bool
                        ),
                    },
                ],
            ),
        ]
    )
