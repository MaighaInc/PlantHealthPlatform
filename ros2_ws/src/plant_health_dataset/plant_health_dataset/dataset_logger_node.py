"""ROS node that logs /camera/image_raw with acquisition-time sensor sync (PHP-08)."""

from __future__ import annotations

import math
import sys
from datetime import datetime, timezone
from pathlib import Path

import rclpy
from cv_bridge import CvBridge
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import Float32

_REPO_ROOT = Path(__file__).resolve().parents[4]
_ML_ROOT = _REPO_ROOT / "ml"
if _ML_ROOT.is_dir() and str(_ML_ROOT) not in sys.path:
    sys.path.insert(0, str(_ML_ROOT))

from plant_health_data import (  # noqa: E402
    DatasetLogger,
    DatasetLoggerError,
    SensorTimeBuffer,
    TimedSample,
)

_CHANNELS = (
    "soil_moisture",
    "temperature",
    "humidity",
    "light",
    "co2",
)


class DatasetLoggerNode(Node):
    """
    Persist camera frames joined to sensors via sync windows.

    Float32 sensor topics lack headers; samples are stamped with the local ROS
    clock as ``receive_approx`` (see docs/design/DATA_PIPELINE.md). Image times
    use ``Image.header.stamp`` (acquisition/publish stamp from camera node).
    """

    def __init__(self) -> None:
        super().__init__("dataset_logger")
        self._bridge = CvBridge()
        self._buffer = SensorTimeBuffer(maxlen=500)

        default_root = str(_REPO_ROOT / "ml" / "datasets" / "default")
        self.declare_parameter("dataset_root", default_root)
        self.declare_parameter("plant_id", "plant_001")
        self.declare_parameter("image_topic", "/camera/image_raw")
        self.declare_parameter("save_every_n", 1)
        self.declare_parameter("sync_window_sec", 1.0)

        dataset_root = Path(str(self.get_parameter("dataset_root").value))
        self._plant_id = str(self.get_parameter("plant_id").value).strip()
        image_topic = str(self.get_parameter("image_topic").value)
        self._save_every_n = max(1, int(self.get_parameter("save_every_n").value))
        self._sync_window_sec = float(self.get_parameter("sync_window_sec").value)
        self._frame_counter = 0

        if not self._plant_id:
            raise ValueError("plant_id must be non-empty")
        if self._sync_window_sec < 0:
            raise ValueError("sync_window_sec must be >= 0")

        try:
            self._logger = DatasetLogger(dataset_root)
        except Exception as exc:  # noqa: BLE001
            self.get_logger().error(f"Failed to init DatasetLogger: {exc}")
            raise

        self.create_subscription(Image, image_topic, self._on_image, 10)
        self.create_subscription(
            Float32, "/soil/moisture", self._make_sensor_cb("soil_moisture"), 10
        )
        self.create_subscription(
            Float32, "/environment/temperature", self._make_sensor_cb("temperature"), 10
        )
        self.create_subscription(
            Float32, "/environment/humidity", self._make_sensor_cb("humidity"), 10
        )
        self.create_subscription(
            Float32, "/environment/light", self._make_sensor_cb("light"), 10
        )
        self.create_subscription(
            Float32, "/environment/co2", self._make_sensor_cb("co2"), 10
        )

        self.get_logger().info(
            f"Dataset logger started root={dataset_root} plant_id={self._plant_id} "
            f"image_topic={image_topic} save_every_n={self._save_every_n} "
            f"sync_window_sec={self._sync_window_sec}"
        )

    def _ros_now_iso(self) -> str:
        now = self.get_clock().now().to_msg()
        return datetime.fromtimestamp(
            now.sec + now.nanosec * 1e-9, tz=timezone.utc
        ).strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    def _make_sensor_cb(self, key: str):
        def _cb(msg: Float32) -> None:
            if msg.data is None or (
                isinstance(msg.data, float) and math.isnan(msg.data)
            ):
                return
            # Float32 has no acquisition stamp — document as receive_approx.
            self._buffer.add(
                TimedSample(
                    name=key,
                    value=float(msg.data),
                    timestamp_iso=self._ros_now_iso(),
                    stamp_source="receive_approx",
                )
            )

        return _cb

    def _on_image(self, msg: Image) -> None:
        self._frame_counter += 1
        if self._frame_counter % self._save_every_n != 0:
            return
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
            ts = self._ros_now_iso()
            self.get_logger().warn(
                "Image missing header stamp; using ROS now (not ideal acquisition time)"
            )

        sync = self._buffer.join(
            ts, list(_CHANNELS), window_sec=self._sync_window_sec
        )
        if sync.missing:
            self.get_logger().warn(
                f"Sync incomplete status={sync.sync_status} "
                f"missing={sync.missing} stale_candidates={sync.stale_candidates}"
            )

        try:
            record = self._logger.append_record(
                bgr,
                plant_id=self._plant_id,
                timestamp_iso=ts,
                soil_moisture=sync.values.get("soil_moisture"),
                temperature=sync.values.get("temperature"),
                humidity=sync.values.get("humidity"),
                light=sync.values.get("light"),
                co2=sync.values.get("co2"),
                camera_source=msg.header.frame_id or None,
                frame_id=self._frame_counter,
                extra=sync.to_metadata(),
            )
        except DatasetLoggerError as exc:
            self.get_logger().error(f"dataset log failed: {exc}")
            return

        self.get_logger().info(
            f"Logged {record.image} sync={sync.sync_status} "
            f"manifest_count={self._logger.load_manifest().record_count}"
        )


def main(args: list[str] | None = None) -> None:
    rclpy.init(args=args)
    node: DatasetLoggerNode | None = None
    try:
        node = DatasetLoggerNode()
        rclpy.spin(node)
    except KeyboardInterrupt:
        if node is not None:
            node.get_logger().info("Dataset logger interrupted")
    finally:
        if node is not None:
            node.get_logger().info("Dataset logger shutting down")
            node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
