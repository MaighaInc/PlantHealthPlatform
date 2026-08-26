from setuptools import find_packages, setup

package_name = "plant_health_cv"

setup(
    name=package_name,
    version="0.1.0",
    packages=find_packages(exclude=["test"]),
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
        ("share/" + package_name + "/launch", ["launch/cv.launch.py"]),
        ("share/" + package_name + "/config", ["config/cv_params.yaml"]),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="PlantHealthPlatform",
    maintainer_email="dev@planthealth.local",
    description="OpenCV plant segmentation and feature pipeline for PlantHealthPlatform",
    license="Proprietary",
    tests_require=["pytest"],
    entry_points={
        "console_scripts": [
            "cv_pipeline = plant_health_cv.cv_node:main",
        ],
    },
)
