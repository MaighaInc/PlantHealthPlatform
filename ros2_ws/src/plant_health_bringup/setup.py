from setuptools import setup

package_name = "plant_health_bringup"

setup(
    name=package_name,
    version="0.1.0",
    packages=[],
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
        ("share/" + package_name + "/launch", ["launch/plant_health.launch.py"]),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="PlantHealthPlatform",
    maintainer_email="dev@planthealth.local",
    description="Unified bringup for PlantHealthPlatform",
    license="Proprietary",
)
