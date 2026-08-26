from setuptools import find_packages, setup

package_name = "plant_health_dataset"

setup(
    name=package_name,
    version="0.1.0",
    packages=find_packages(exclude=["test"]),
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
        ("share/" + package_name + "/launch", ["launch/dataset_logger.launch.py"]),
        ("share/" + package_name + "/config", ["config/dataset_logger.yaml"]),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="PlantHealthPlatform",
    maintainer_email="dev@planthealth.local",
    description="Dataset logging ROS node for PlantHealthPlatform",
    license="Proprietary",
    entry_points={
        "console_scripts": [
            "dataset_logger = plant_health_dataset.dataset_logger_node:main",
        ],
    },
)
