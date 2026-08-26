"""ROS 2 CV node: /camera/image_raw → pipeline → processed + ROI images."""

from __future__ import annotations

import rclpy
from cv_bridge import CvBridge
from rclpy.node import Node
from sensor_msgs.msg import Image

from plant_health_cv.parameters import CvNodeParams, CvParameterError
from plant_health_cv.pipeline import run_pipeline


class CvPipelineNode(Node):
    """Subscribes to raw camera images and publishes processed visualization + ROI."""

    def __init__(self) -> None:
        super().__init__("cv_pipeline")
        self._bridge = CvBridge()

        self.declare_parameter("process_width", 320)
        self.declare_parameter("process_height", 240)
        self.declare_parameter("blur_ksize", 5)
        self.declare_parameter("h_min", 35)
        self.declare_parameter("h_max", 85)
        self.declare_parameter("s_min", 40)
        self.declare_parameter("v_min", 40)
        self.declare_parameter("image_topic", "/camera/image_raw")
        self.declare_parameter("processed_topic", "/camera/image_processed")
        self.declare_parameter("roi_topic", "/plant/roi")

        try:
            self._params = CvNodeParams.from_raw(
                process_width=int(self.get_parameter("process_width").value),
                process_height=int(self.get_parameter("process_height").value),
                blur_ksize=int(self.get_parameter("blur_ksize").value),
                h_min=int(self.get_parameter("h_min").value),
                h_max=int(self.get_parameter("h_max").value),
                s_min=int(self.get_parameter("s_min").value),
                v_min=int(self.get_parameter("v_min").value),
                image_topic=str(self.get_parameter("image_topic").value),
                processed_topic=str(self.get_parameter("processed_topic").value),
                roi_topic=str(self.get_parameter("roi_topic").value),
            )
        except (CvParameterError, TypeError, ValueError) as exc:
            self.get_logger().error(f"Invalid parameters: {exc}")
            raise CvParameterError(str(exc)) from exc

        self._pub_processed = self.create_publisher(
            Image, self._params.processed_topic, 10
        )
        self._pub_roi = self.create_publisher(Image, self._params.roi_topic, 10)
        self._sub = self.create_subscription(
            Image, self._params.image_topic, self._on_image, 10
        )
        self.get_logger().info(
            "CV pipeline started "
            f"in={self._params.image_topic} "
            f"processed={self._params.processed_topic} roi={self._params.roi_topic} "
            f"size={self._params.process_width}x{self._params.process_height} "
            f"HSV H=[{self._params.h_min},{self._params.h_max}]"
        )

    def _on_image(self, msg: Image) -> None:
        try:
            bgr = self._bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")
        except Exception as exc:  # noqa: BLE001 — bridge errors vary by encoding
            self.get_logger().warn(f"cv_bridge convert failed: {exc}")
            return

        try:
            result = run_pipeline(
                bgr,
                width=self._params.process_width,
                height=self._params.process_height,
                blur_ksize=self._params.blur_ksize,
                h_min=self._params.h_min,
                h_max=self._params.h_max,
                s_min=self._params.s_min,
                v_min=self._params.v_min,
            )
        except (TypeError, ValueError) as exc:
            self.get_logger().warn(f"pipeline rejected frame: {exc}")
            return

        out = self._bridge.cv2_to_imgmsg(result.viz_bgr, encoding="bgr8")
        out.header = msg.header
        self._pub_processed.publish(out)

        if result.roi_bgr is not None and result.roi_bgr.size > 0:
            roi_msg = self._bridge.cv2_to_imgmsg(result.roi_bgr, encoding="bgr8")
            roi_msg.header = msg.header
            self._pub_roi.publish(roi_msg)

        self.get_logger().info(
            "Processed frame "
            f"green_ratio={result.features.get('green_pixel_ratio', 0):.3f} "
            f"leaf_area={result.features.get('leaf_area', 0):.0f} "
            f"contour_area={result.features.get('contour_area', 0):.1f}"
        )


def main(args: list[str] | None = None) -> None:
    rclpy.init(args=args)
    node: CvPipelineNode | None = None
    try:
        node = CvPipelineNode()
        rclpy.spin(node)
    except CvParameterError:
        pass
    except KeyboardInterrupt:
        if node is not None:
            node.get_logger().info("CV pipeline interrupted")
    finally:
        if node is not None:
            node.get_logger().info("CV pipeline shutting down")
            node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
