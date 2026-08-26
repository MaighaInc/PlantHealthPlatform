from setuptools import find_packages, setup

package_name = "plant_health_status"

setup(
    name=package_name,
    version="0.1.0",
    packages=find_packages(exclude=["test"]),
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
        ("share/" + package_name + "/launch", ["launch/status.launch.py"]),
        ("share/" + package_name + "/config", ["config/status_params.yaml"]),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="PlantHealthPlatform",
    maintainer_email="dev@planthealth.local",
    description="System status publisher/subscriber foundation for PlantHealthPlatform",
    license="Proprietary",
    tests_require=["pytest"],
    entry_points={
        "console_scripts": [
            "status_publisher = plant_health_status.status_publisher:main",
            "status_subscriber = plant_health_status.status_subscriber:main",
        ],
    },
)
