"""Launch CV pipeline and feature publisher."""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description() -> LaunchDescription:
    share = get_package_share_directory("plant_health_cv")
    cv_params = os.path.join(share, "config", "cv_params.yaml")
    feat_params = os.path.join(share, "config", "features_params.yaml")
    return LaunchDescription(
        [
            DeclareLaunchArgument("cv_params_file", default_value=cv_params),
            DeclareLaunchArgument("features_params_file", default_value=feat_params),
            Node(
                package="plant_health_cv",
                executable="cv_pipeline",
                name="cv_pipeline",
                output="screen",
                parameters=[LaunchConfiguration("cv_params_file")],
            ),
            Node(
                package="plant_health_cv",
                executable="feature_publisher",
                name="feature_publisher",
                output="screen",
                parameters=[LaunchConfiguration("features_params_file")],
            ),
        ]
    )
