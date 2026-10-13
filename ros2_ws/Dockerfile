# PlantHealthPlatform — ROS 2 Humble SIMULATION stack (all plant_health_* packages).
# Build from repo root: docker build -f ros2_ws/Dockerfile -t phs-ros2 .
FROM ros:humble-ros-base-jammy

ENV DEBIAN_FRONTEND=noninteractive \
    ROS_DISTRO=humble \
    PHS_WS=/opt/phs/ws \
    PHS_MODELS=/opt/phs/models \
    DEVELOPMENT_MODE=SIMULATION \
    ROS_LOCALHOST_ONLY=1

# colcon + cv_bridge (OpenCV bridge for sensor_msgs/Image).
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-pip \
    python3-colcon-common-extensions \
    ros-humble-cv-bridge \
    ros-humble-image-transport \
    && rm -rf /var/lib/apt/lists/*

COPY ros2_ws/requirements.txt /tmp/ros-requirements.txt
RUN pip3 install --no-cache-dir -r /tmp/ros-requirements.txt

WORKDIR ${PHS_WS}
COPY ros2_ws/src ./src

RUN . /opt/ros/${ROS_DISTRO}/setup.sh && \
    colcon build --packages-up-to plant_health_bringup

# Optional joblib artifact for inference.launch.py backend:=joblib
COPY ml/models ${PHS_MODELS}

COPY ros2_ws/docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

ENV PHS_MODEL_PATH=${PHS_MODELS}/plant-health-classifier-1.0.0.joblib

ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["ros2", "launch", "plant_health_bringup", "plant_health.launch.py"]
