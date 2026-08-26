"""ROS 2 node that subscribes to /system/status and logs heartbeats."""

from __future__ import annotations

import rclpy
from rclpy.node import Node
from std_msgs.msg import String

from plant_health_status.heartbeat import (
    DEFAULT_NODE_NAME_SUBSCRIBER,
    SYSTEM_STATUS_TOPIC,
    parse_status_message,
)
from plant_health_status.parameters import (
    ParameterValidationError,
    StatusSubscriberParams,
)


class StatusSubscriberNode(Node):
    """Receives system heartbeats and logs structured fields."""

    def __init__(self) -> None:
        super().__init__(DEFAULT_NODE_NAME_SUBSCRIBER)
        self.declare_parameter("topic", SYSTEM_STATUS_TOPIC)

        try:
            params = StatusSubscriberParams.from_raw(
                topic=str(self.get_parameter("topic").value),
            )
        except ParameterValidationError as exc:
            self.get_logger().error(f"Invalid parameters: {exc}")
            raise

        self._subscription = self.create_subscription(
            String,
            params.topic,
            self._on_message,
            10,
        )
        self.get_logger().info(f"Status subscriber listening on topic={params.topic}")
        self.get_logger().info(f"Active parameters: topic={params.topic}")

    def _on_message(self, msg: String) -> None:
        try:
            fields = parse_status_message(msg.data)
        except ValueError as exc:
            self.get_logger().warn(f"Ignored invalid status payload: {exc}")
            return

        self.get_logger().info(
            "Received status "
            f"state={fields['state']} seq={fields['seq']} "
            f"source={fields['source']} ts={fields['ts']}"
        )


def main(args: list[str] | None = None) -> None:
    rclpy.init(args=args)
    node: StatusSubscriberNode | None = None
    try:
        node = StatusSubscriberNode()
        rclpy.spin(node)
    except ParameterValidationError:
        pass
    except KeyboardInterrupt:
        if node is not None:
            node.get_logger().info("Status subscriber interrupted")
    finally:
        if node is not None:
            node.get_logger().info("Status subscriber shutting down")
            node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
