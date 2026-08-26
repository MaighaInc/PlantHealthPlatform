"""ROS node: sensor readings → rule health → /plant/health (no GPIO)."""

from __future__ import annotations

import math

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32, String

from plant_health_health.parameters import HealthNodeParams, HealthParameterError
from plant_health_health.rules import HealthInputs, evaluate_health


class HealthEngineNode(Node):
    """Rule-based plant health publisher — thresholds from parameters/YAML only."""

    def __init__(self) -> None:
        super().__init__("health_engine")
        self._soil: float | None = None
        self._temp: float | None = None
        self._humidity: float | None = None
        self._light: float | None = None

        self.declare_parameter("soil_dry_threshold", 30.0)
        self.declare_parameter("temp_hot_threshold", 32.0)
        self.declare_parameter("publish_period_sec", 1.0)
        self.declare_parameter("health_topic", "/plant/health")

        try:
            params = HealthNodeParams.from_raw(
                soil_dry_threshold=float(
                    self.get_parameter("soil_dry_threshold").value
                ),
                temp_hot_threshold=float(
                    self.get_parameter("temp_hot_threshold").value
                ),
                publish_period_sec=float(
                    self.get_parameter("publish_period_sec").value
                ),
                health_topic=str(self.get_parameter("health_topic").value),
            )
        except (HealthParameterError, TypeError, ValueError) as exc:
            self.get_logger().error(f"Invalid parameters: {exc}")
            raise HealthParameterError(str(exc)) from exc

        self._rules = params.to_rules_config()
        self._publisher = self.create_publisher(String, params.health_topic, 10)
        self.create_subscription(Float32, "/soil/moisture", self._on_soil, 10)
        self.create_subscription(
            Float32, "/environment/temperature", self._on_temp, 10
        )
        self.create_subscription(
            Float32, "/environment/humidity", self._on_humidity, 10
        )
        self.create_subscription(Float32, "/environment/light", self._on_light, 10)
        self.create_timer(params.publish_period_sec, self._on_timer)

        self.get_logger().info(
            "Health engine started "
            f"topic={params.health_topic} "
            f"soil_dry<{self._rules.soil_dry_threshold} "
            f"temp_hot>{self._rules.temp_hot_threshold}"
        )

    @staticmethod
    def _read_float(msg: Float32) -> float | None:
        if msg.data is None or (
            isinstance(msg.data, float) and (math.isnan(msg.data) or math.isinf(msg.data))
        ):
            return None
        return float(msg.data)

    def _on_soil(self, msg: Float32) -> None:
        self._soil = self._read_float(msg)

    def _on_temp(self, msg: Float32) -> None:
        self._temp = self._read_float(msg)

    def _on_humidity(self, msg: Float32) -> None:
        self._humidity = self._read_float(msg)

    def _on_light(self, msg: Float32) -> None:
        self._light = self._read_float(msg)

    def _on_timer(self) -> None:
        assessment = evaluate_health(
            HealthInputs(
                soil_moisture=self._soil,
                temperature=self._temp,
                humidity=self._humidity,
                light=self._light,
            ),
            self._rules,
        )
        msg = String()
        msg.data = assessment.to_message_data()
        self._publisher.publish(msg)
        self.get_logger().info(
            f"Health status={assessment.status.value} reason={assessment.reason} "
            f"score={assessment.score:.2f} rules={list(assessment.rules_fired)}"
        )


def main(args: list[str] | None = None) -> None:
    rclpy.init(args=args)
    node: HealthEngineNode | None = None
    try:
        node = HealthEngineNode()
        rclpy.spin(node)
    except HealthParameterError:
        pass
    except KeyboardInterrupt:
        if node is not None:
            node.get_logger().info("Health engine interrupted")
    finally:
        if node is not None:
            node.get_logger().info("Health engine shutting down")
            node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
