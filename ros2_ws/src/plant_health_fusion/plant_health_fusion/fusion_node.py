"""ROS node: fuse rules + features + ML → /plant/fused_health (PHP-15)."""

from __future__ import annotations

import json

import rclpy
from rclpy.node import Node
from std_msgs.msg import String

from plant_health_fusion.fuse import (
    fuse_health,
    parse_features_optional,
    parse_ml_prediction,
    parse_rules_health,
)
from plant_health_fusion.parameters import FusionNodeParams, FusionParameterError


class FusionNode(Node):
    """Combine health, features, and ML into one decision-facing interface."""

    def __init__(self) -> None:
        super().__init__("plant_health_fusion")

        self.declare_parameter("health_topic", "/plant/health")
        self.declare_parameter("features_topic", "/plant/features")
        self.declare_parameter("prediction_topic", "/plant/disease_prediction")
        self.declare_parameter("fused_topic", "/plant/fused_health")
        self.declare_parameter("publish_period_sec", 1.0)
        self.declare_parameter("green_stress_threshold", 0.08)

        try:
            params = FusionNodeParams.from_raw(
                health_topic=str(self.get_parameter("health_topic").value),
                features_topic=str(self.get_parameter("features_topic").value),
                prediction_topic=str(self.get_parameter("prediction_topic").value),
                fused_topic=str(self.get_parameter("fused_topic").value),
                publish_period_sec=float(
                    self.get_parameter("publish_period_sec").value
                ),
                green_stress_threshold=float(
                    self.get_parameter("green_stress_threshold").value
                ),
            )
        except (FusionParameterError, TypeError, ValueError) as exc:
            self.get_logger().error(f"Invalid parameters: {exc}")
            raise FusionParameterError(str(exc)) from exc

        self._green_thr = params.green_stress_threshold
        self._rules: dict | None = None
        self._ml: dict | None = None
        self._features: dict = {}

        self._pub = self.create_publisher(String, params.fused_topic, 10)
        self.create_subscription(String, params.health_topic, self._on_health, 10)
        self.create_subscription(String, params.features_topic, self._on_features, 10)
        self.create_subscription(
            String, params.prediction_topic, self._on_prediction, 10
        )
        self.create_timer(params.publish_period_sec, self._on_timer)

        self.get_logger().info(
            "Fusion started "
            f"out={params.fused_topic} period={params.publish_period_sec}s "
            f"green_thr={self._green_thr}"
        )

    def _on_health(self, msg: String) -> None:
        try:
            self._rules = parse_rules_health(msg.data)
        except (TypeError, ValueError) as exc:
            self.get_logger().warn(f"bad health message: {exc}")

    def _on_features(self, msg: String) -> None:
        try:
            self._features = parse_features_optional(msg.data)
        except (TypeError, ValueError, json.JSONDecodeError) as exc:
            self.get_logger().warn(f"bad features message: {exc}")

    def _on_prediction(self, msg: String) -> None:
        try:
            self._ml = parse_ml_prediction(msg.data)
        except (TypeError, ValueError, json.JSONDecodeError) as exc:
            self.get_logger().warn(f"bad prediction message: {exc}")

    def _on_timer(self) -> None:
        fused = fuse_health(
            rules=self._rules,
            ml=self._ml,
            features=self._features,
            green_stress_threshold=self._green_thr,
        )
        out = String()
        out.data = fused.to_message_data()
        self._pub.publish(out)
        self.get_logger().info(
            f"fused status={fused.status} precedence={fused.precedence} "
            f"reason={fused.reason} conf={fused.confidence:.3f}"
        )


def main(args: list[str] | None = None) -> None:
    rclpy.init(args=args)
    node: FusionNode | None = None
    try:
        node = FusionNode()
        rclpy.spin(node)
    except FusionParameterError:
        pass
    except KeyboardInterrupt:
        if node is not None:
            node.get_logger().info("Fusion interrupted")
    finally:
        if node is not None:
            node.get_logger().info("Fusion shutting down")
            node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
