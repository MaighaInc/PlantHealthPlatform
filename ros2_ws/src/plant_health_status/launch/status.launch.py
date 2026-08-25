"""Launch status publisher and subscriber together."""

from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description() -> LaunchDescription:
    return LaunchDescription(
        [
            Node(
                package="plant_health_status",
                executable="status_publisher",
                name="status_publisher",
                output="screen",
                parameters=[{"publish_period_sec": 1.0}],
            ),
            Node(
                package="plant_health_status",
                executable="status_subscriber",
                name="status_subscriber",
                output="screen",
            ),
        ]
    )
