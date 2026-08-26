from setuptools import find_packages, setup

package_name = "plant_health_sensors"

setup(
    name=package_name,
    version="0.1.0",
    packages=find_packages(exclude=["test"]),
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
        ("share/" + package_name + "/launch", ["launch/virtual_sensors.launch.py"]),
        ("share/" + package_name + "/config", ["config/virtual_sensors.yaml"]),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="PlantHealthPlatform",
    maintainer_email="dev@planthealth.local",
    description="Virtual and physical sensor nodes for PlantHealthPlatform",
    license="Proprietary",
    tests_require=["pytest"],
    entry_points={
        "console_scripts": [
            "virtual_sensor_publisher = plant_health_sensors.virtual_sensor_node:main",
        ],
    },
)
