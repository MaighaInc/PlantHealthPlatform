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
from plant_health_status.parameters import (
    ParameterValidationError,
    StatusPublisherParams,
)


class StatusPublisherNode(Node):
    """Publishes periodic ONLINE heartbeats for Plant Health System."""

    def __init__(self) -> None:
        super().__init__(DEFAULT_NODE_NAME_PUBLISHER)
        self._sequence = 0

        self.declare_parameter("publish_period_sec", DEFAULT_PUBLISH_PERIOD_SEC)
        self.declare_parameter("topic", SYSTEM_STATUS_TOPIC)
        self.declare_parameter("source", "plant_health_status")

        try:
            params = StatusPublisherParams.from_raw(
                publish_period_sec=float(
                    self.get_parameter("publish_period_sec").value
                ),
                topic=str(self.get_parameter("topic").value),
                source=str(self.get_parameter("source").value),
            )
        except (ParameterValidationError, TypeError, ValueError) as exc:
            self.get_logger().error(f"Invalid parameters: {exc}")
            raise ParameterValidationError(str(exc)) from exc

        self._source = params.source
        self._publisher = self.create_publisher(String, params.topic, 10)
        self._timer = self.create_timer(params.publish_period_sec, self._on_timer)

        self.get_logger().info(
            "Status publisher started "
            f"topic={params.topic} period_sec={params.publish_period_sec} "
            f"source={params.source}"
        )
        # Runtime inspection aid
        self.get_logger().info(
            "Active parameters: "
            f"publish_period_sec={params.publish_period_sec}, "
            f"topic={params.topic}, source={params.source}"
        )

    def _on_timer(self) -> None:
        msg = String()
        msg.data = format_status_message(sequence=self._sequence, source=self._source)
        self._publisher.publish(msg)
        self.get_logger().info(f"Published status seq={self._sequence}")
        self._sequence += 1


def main(args: list[str] | None = None) -> None:
    rclpy.init(args=args)
    node: StatusPublisherNode | None = None
    try:
        node = StatusPublisherNode()
        rclpy.spin(node)
    except ParameterValidationError:
        # Already logged in __init__
        pass
    except KeyboardInterrupt:
        if node is not None:
            node.get_logger().info("Status publisher interrupted")
    finally:
        if node is not None:
            node.get_logger().info("Status publisher shutting down")
            node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
