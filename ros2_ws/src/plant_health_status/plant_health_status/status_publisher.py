"""ROS 2 node that publishes system heartbeat on /system/status."""

from __future__ import annotations

import rclpy
from rclpy.node import Node
from std_msgs.msg import String

from plant_health_status.heartbeat import (
    DEFAULT_NODE_NAME_PUBLISHER,
    DEFAULT_PUBLISH_PERIOD_SEC,
    SYSTEM_STATUS_TOPIC,
    format_status_message,
)


class StatusPublisherNode(Node):
    """Publishes periodic ONLINE heartbeats for Plant Health System."""

    def __init__(self) -> None:
        super().__init__(DEFAULT_NODE_NAME_PUBLISHER)
        self._sequence = 0

        self.declare_parameter("publish_period_sec", DEFAULT_PUBLISH_PERIOD_SEC)
        self.declare_parameter("topic", SYSTEM_STATUS_TOPIC)
        self.declare_parameter("source", "plant_health_status")

        period = float(self.get_parameter("publish_period_sec").value)
        topic = str(self.get_parameter("topic").value)
        self._source = str(self.get_parameter("source").value)

        if period <= 0:
            self.get_logger().error("publish_period_sec must be > 0; using default")
            period = DEFAULT_PUBLISH_PERIOD_SEC

        self._publisher = self.create_publisher(String, topic, 10)
        self._timer = self.create_timer(period, self._on_timer)

        self.get_logger().info(
            f"Status publisher started topic={topic} period_sec={period}"
        )

    def _on_timer(self) -> None:
        msg = String()
        msg.data = format_status_message(sequence=self._sequence, source=self._source)
        self._publisher.publish(msg)
        self.get_logger().info(f"Published status seq={self._sequence}")
        self._sequence += 1


def main(args: list[str] | None = None) -> None:
    rclpy.init(args=args)
    node = StatusPublisherNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("Status publisher interrupted")
    finally:
        node.get_logger().info("Status publisher shutting down")
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
