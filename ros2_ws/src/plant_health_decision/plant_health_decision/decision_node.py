"""ROS node: /plant/fused_health → /irrigation/intent (PHP-16, no GPIO)."""

from __future__ import annotations

import json

import rclpy
from rclpy.node import Node
from std_msgs.msg import String

from plant_health_decision.decide import decide_irrigation, parse_fused_health
from plant_health_decision.parameters import DecisionNodeParams, DecisionParameterError


class DecisionNode(Node):
    """
    Irrigation *intent* only — Prediction ≠ Decision ≠ Actuation.

    Never imports GPIO. Never publishes /irrigation/command (ADR-0003).
    """

    def __init__(self) -> None:
        super().__init__("plant_health_decision")

        self.declare_parameter("fused_topic", "/plant/fused_health")
        self.declare_parameter("intent_topic", "/irrigation/intent")
        self.declare_parameter("publish_period_sec", 1.0)

        try:
            params = DecisionNodeParams.from_raw(
                fused_topic=str(self.get_parameter("fused_topic").value),
                intent_topic=str(self.get_parameter("intent_topic").value),
                publish_period_sec=float(
                    self.get_parameter("publish_period_sec").value
                ),
            )
        except (DecisionParameterError, TypeError, ValueError) as exc:
            self.get_logger().error(f"Invalid parameters: {exc}")
            raise DecisionParameterError(str(exc)) from exc

        self._fused: dict | None = None
        self._pub = self.create_publisher(String, params.intent_topic, 10)
        self.create_subscription(String, params.fused_topic, self._on_fused, 10)
        self.create_timer(params.publish_period_sec, self._on_timer)

        self.get_logger().info(
            "Decision started "
            f"in={params.fused_topic} out={params.intent_topic} "
            f"(intent only; no GPIO)"
        )

    def _on_fused(self, msg: String) -> None:
        try:
            self._fused = parse_fused_health(msg.data)
        except (TypeError, ValueError, json.JSONDecodeError) as exc:
            self.get_logger().warn(f"bad fused health: {exc}")

    def _on_timer(self) -> None:
        if self._fused is None:
            return
        intent = decide_irrigation(self._fused)
        out = String()
        out.data = intent.to_message_data()
        self._pub.publish(out)
        self.get_logger().info(
            f"intent water={intent.water} reason={intent.reason} "
            f"fused={intent.fused_status}/{intent.fused_precedence}"
        )


def main(args: list[str] | None = None) -> None:
    rclpy.init(args=args)
    node: DecisionNode | None = None
    try:
        node = DecisionNode()
        rclpy.spin(node)
    except DecisionParameterError:
        pass
    except KeyboardInterrupt:
        if node is not None:
            node.get_logger().info("Decision interrupted")
    finally:
        if node is not None:
            node.get_logger().info("Decision shutting down")
            node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
