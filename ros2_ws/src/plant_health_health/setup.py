from setuptools import find_packages, setup

package_name = "plant_health_health"

setup(
    name=package_name,
    version="0.1.0",
    packages=find_packages(exclude=["test"]),
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
        ("share/" + package_name + "/launch", ["launch/health.launch.py"]),
        ("share/" + package_name + "/config", ["config/health_params.yaml"]),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="PlantHealthPlatform",
    maintainer_email="dev@planthealth.local",
    description="Rule-based plant health engine for PlantHealthPlatform",
    license="Proprietary",
    entry_points={
        "console_scripts": [
            "health_engine = plant_health_health.health_node:main",
        ],
    },
)
