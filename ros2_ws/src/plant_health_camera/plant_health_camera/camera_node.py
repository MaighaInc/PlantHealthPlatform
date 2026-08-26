"""ROS 2 camera publisher — CameraInterface only; cv_bridge for Image msgs."""

from __future__ import annotations

from pathlib import Path

import rclpy
from cv_bridge import CvBridge
from rclpy.node import Node
from sensor_msgs.msg import Image

from plant_health_camera.factory import create_camera
from plant_health_camera.interfaces import CameraInterface
from plant_health_camera.parameters import CameraNodeParams, CameraParameterError
from plant_health_camera.validation import FrameValidationError, validate_frame


class CameraPublisherNode(Node):
    """Publishes validated frames on /camera/image_raw."""

    def __init__(self) -> None:
        super().__init__("camera_publisher")
        self._bridge = CvBridge()
        self._camera: CameraInterface | None = None
        self._drop_count = 0
        self._invalid_count = 0
        self._publish_count = 0

        self.declare_parameter("publish_period_sec", 0.2)
        self.declare_parameter("development_mode", "SIMULATION")
        self.declare_parameter("camera_backend", "auto")
        self.declare_parameter("device_index", 0)
        self.declare_parameter("width", 640)
        self.declare_parameter("height", 480)
        self.declare_parameter("fps", 15.0)
        self.declare_parameter("topic", "/camera/image_raw")

        try:
            params = CameraNodeParams.from_raw(
                publish_period_sec=float(
                    self.get_parameter("publish_period_sec").value
                ),
                development_mode=str(self.get_parameter("development_mode").value),
                camera_backend=str(self.get_parameter("camera_backend").value),
                device_index=int(self.get_parameter("device_index").value),
                width=int(self.get_parameter("width").value),
                height=int(self.get_parameter("height").value),
                fps=float(self.get_parameter("fps").value),
                topic=str(self.get_parameter("topic").value),
            )
        except (CameraParameterError, TypeError, ValueError) as exc:
            self.get_logger().error(f"Invalid parameters: {exc}")
            raise CameraParameterError(str(exc)) from exc

        sample_dir = Path(__file__).resolve().parent / "data" / "samples"
        self._camera = create_camera(
            mode=params.development_mode,
            backend=params.camera_backend,
            device_index=params.device_index,
            width=params.width,
            height=params.height,
            fps=params.fps,
            sample_dir=sample_dir if sample_dir.is_dir() else None,
        )
        self._expect_w = params.width
        self._expect_h = params.height
        self._topic = params.topic

        try:
            self._camera.open()
        except Exception as exc:  # noqa: BLE001 — log and re-raise as param-style failure
            self.get_logger().error(f"Camera open failed: {exc}")
            raise CameraParameterError(str(exc)) from exc

        self._publisher = self.create_publisher(Image, self._topic, 10)
        self._timer = self.create_timer(params.publish_period_sec, self._on_timer)
        self.get_logger().info(
            "Camera publisher started "
            f"mode={params.development_mode} backend={params.camera_backend} "
            f"source={self._camera.source_id} topic={self._topic} "
            f"{params.width}x{params.height}@{params.fps}"
        )

    def _on_timer(self) -> None:
        assert self._camera is not None
        frame = self._camera.read()
        if frame is None:
            self._drop_count += 1
            self.get_logger().warn(
                f"Dropped/unavailable frame source={self._camera.source_id} "
                f"drops={self._drop_count}"
            )
            return

        try:
            validate_frame(
                frame,
                expect_width=None,  # USB may not honor exact size
                expect_height=None,
                reject_blank=True,
            )
        except FrameValidationError as exc:
            self._invalid_count += 1
            self.get_logger().warn(
                f"Invalid frame rejected: {exc} invalids={self._invalid_count}"
            )
            return

        msg = self._bridge.cv2_to_imgmsg(frame.image, encoding="bgr8")
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = frame.source
        # Preserve acquisition time in frame_id field via logging; stamp is ROS now
        # Acquisition ISO is logged for sync work (PHP-08).
        self._publisher.publish(msg)
        self._publish_count += 1
        self.get_logger().info(
            f"Published image frame_id={frame.frame_id} "
            f"acq_ts={frame.timestamp_iso} "
            f"{frame.width}x{frame.height} publishes={self._publish_count}"
        )

    def destroy_node(self) -> bool:
        if self._camera is not None:
            self._camera.release()
            self.get_logger().info("Camera resources released")
        return super().destroy_node()


def main(args: list[str] | None = None) -> None:
    rclpy.init(args=args)
    node: CameraPublisherNode | None = None
    try:
        node = CameraPublisherNode()
        rclpy.spin(node)
    except CameraParameterError:
        pass
    except KeyboardInterrupt:
        if node is not None:
            node.get_logger().info("Camera publisher interrupted")
    finally:
        if node is not None:
            node.get_logger().info("Camera publisher shutting down")
            node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
