"""ROS node: camera image + sensors → /plant/features (PHP-10)."""

from __future__ import annotations

import math
from datetime import datetime, timezone

import rclpy
from cv_bridge import CvBridge
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import Float32, String

from plant_health_cv.features import build_feature_vector
from plant_health_cv.pipeline import run_pipeline


class FeaturePublisherNode(Node):
    """Runs CV pipeline on each image and publishes a schema-stable feature vector."""

    def __init__(self) -> None:
        super().__init__("feature_publisher")
        self._bridge = CvBridge()
        self._sensors: dict[str, float | None] = {
            "soil_moisture": None,
            "temperature": None,
            "humidity": None,
            "light": None,
            "co2": None,
        }

        self.declare_parameter("image_topic", "/camera/image_raw")
        self.declare_parameter("features_topic", "/plant/features")
        self.declare_parameter("process_width", 320)
        self.declare_parameter("process_height", 240)
        self.declare_parameter("blur_ksize", 5)
        self.declare_parameter("h_min", 35)
        self.declare_parameter("h_max", 85)
        self.declare_parameter("s_min", 40)
        self.declare_parameter("v_min", 40)

        image_topic = str(self.get_parameter("image_topic").value)
        features_topic = str(self.get_parameter("features_topic").value)
        self._width = int(self.get_parameter("process_width").value)
        self._height = int(self.get_parameter("process_height").value)
        self._blur = int(self.get_parameter("blur_ksize").value)
        self._h_min = int(self.get_parameter("h_min").value)
        self._h_max = int(self.get_parameter("h_max").value)
        self._s_min = int(self.get_parameter("s_min").value)
        self._v_min = int(self.get_parameter("v_min").value)

        self._pub = self.create_publisher(String, features_topic, 10)
        self.create_subscription(Image, image_topic, self._on_image, 10)
        self.create_subscription(
            Float32, "/soil/moisture", self._make_cb("soil_moisture"), 10
        )
        self.create_subscription(
            Float32, "/environment/temperature", self._make_cb("temperature"), 10
        )
        self.create_subscription(
            Float32, "/environment/humidity", self._make_cb("humidity"), 10
        )
        self.create_subscription(
            Float32, "/environment/light", self._make_cb("light"), 10
        )
        self.create_subscription(
            Float32, "/environment/co2", self._make_cb("co2"), 10
        )

        self.get_logger().info(
            f"Feature publisher started in={image_topic} out={features_topic}"
        )

    def _make_cb(self, key: str):
        def _cb(msg: Float32) -> None:
            if msg.data is None or (
                isinstance(msg.data, float)
                and (math.isnan(msg.data) or math.isinf(msg.data))
            ):
                self._sensors[key] = None
            else:
                self._sensors[key] = float(msg.data)

        return _cb

    def _on_image(self, msg: Image) -> None:
        try:
            bgr = self._bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")
        except Exception as exc:  # noqa: BLE001
            self.get_logger().warn(f"cv_bridge failed: {exc}")
            return

        stamp = msg.header.stamp
        if stamp.sec or stamp.nanosec:
            ts = datetime.fromtimestamp(
                stamp.sec + stamp.nanosec * 1e-9, tz=timezone.utc
            ).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        else:
            ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")

        try:
            result = run_pipeline(
                bgr,
                width=self._width,
                height=self._height,
                blur_ksize=self._blur,
                h_min=self._h_min,
                h_max=self._h_max,
                s_min=self._s_min,
                v_min=self._v_min,
            )
        except (TypeError, ValueError) as exc:
            self.get_logger().warn(f"pipeline failed: {exc}")
            return

        vector = build_feature_vector(
            result.features,
            soil_moisture=self._sensors["soil_moisture"],
            temperature=self._sensors["temperature"],
            humidity=self._sensors["humidity"],
            light=self._sensors["light"],
            co2=self._sensors["co2"],
            timestamp_iso=ts,
        )
        out = String()
        out.data = vector.to_message_data()
        self._pub.publish(out)
        self.get_logger().info(
            "Published features "
            f"green_ratio={vector.features.get('green_pixel_ratio')} "
            f"leaf_area={vector.features.get('leaf_area')} "
            f"soil={vector.features.get('soil_moisture')}"
        )


def main(args: list[str] | None = None) -> None:
    rclpy.init(args=args)
    node: FeaturePublisherNode | None = None
    try:
        node = FeaturePublisherNode()
        rclpy.spin(node)
    except KeyboardInterrupt:
        if node is not None:
            node.get_logger().info("Feature publisher interrupted")
    finally:
        if node is not None:
            node.get_logger().info("Feature publisher shutting down")
            node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
