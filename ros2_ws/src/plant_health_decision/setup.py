from setuptools import find_packages, setup

package_name = "plant_health_decision"

setup(
    name=package_name,
    version="0.1.0",
    packages=find_packages(exclude=["test"]),
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
        ("share/" + package_name + "/launch", ["launch/decision.launch.py"]),
        ("share/" + package_name + "/config", ["config/decision_params.yaml"]),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="PlantHealthPlatform",
    maintainer_email="dev@planthealth.local",
    description="Irrigation intent decision engine for PlantHealthPlatform",
    license="Proprietary",
    tests_require=["pytest"],
    entry_points={
        "console_scripts": [
            "decision_engine = plant_health_decision.decision_node:main",
        ],
    },
)
