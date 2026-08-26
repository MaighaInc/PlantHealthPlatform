"""ROS safety node: /irrigation/intent + soil → gated /irrigation/command (PHP-18)."""

from __future__ import annotations

import math
import time

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32, String

from plant_health_irrigation.safety import (
    SafetyConfig,
    SafetyState,
    apply_safety_transition,
    build_command_message,
    evaluate_safety,
    parse_intent_message,
)


class SafetyNode(Node):
    """Safety layer between decision intent and GPIO command."""

    def __init__(self) -> None:
        super().__init__("plant_health_safety")

        self.declare_parameter("intent_topic", "/irrigation/intent")
        self.declare_parameter("command_topic", "/irrigation/command")
        self.declare_parameter("soil_topic", "/soil/moisture")
        self.declare_parameter("publish_period_sec", 0.5)
        self.declare_parameter("max_duration_sec", 30.0)
        self.declare_parameter("max_daily_sec", 300.0)
        self.declare_parameter("cooldown_sec", 60.0)
        self.declare_parameter("wet_stop_threshold", 70.0)
        self.declare_parameter("e_stop", False)

        self._config = SafetyConfig(
            max_duration_sec=float(self.get_parameter("max_duration_sec").value),
            max_daily_sec=float(self.get_parameter("max_daily_sec").value),
            cooldown_sec=float(self.get_parameter("cooldown_sec").value),
            wet_stop_threshold=float(self.get_parameter("wet_stop_threshold").value),
        )
        self._state = SafetyState(
            e_stop=bool(self.get_parameter("e_stop").value),
        )
        self._intent_water = False
        self._intent_reason = "startup"
        self._soil: float | None = None

        command_topic = str(self.get_parameter("command_topic").value)
        self._pub = self.create_publisher(String, command_topic, 10)
        self.create_subscription(
            String,
            str(self.get_parameter("intent_topic").value),
            self._on_intent,
            10,
        )
        self.create_subscription(
            Float32,
            str(self.get_parameter("soil_topic").value),
            self._on_soil,
            10,
        )
        period = float(self.get_parameter("publish_period_sec").value)
        self.create_timer(period, self._on_timer)

        # Startup-safe: publish OFF immediately
        self._publish_command(False, "startup_off")
        self.get_logger().info(
            f"Safety started → {command_topic} "
            f"max_dur={self._config.max_duration_sec}s "
            f"cooldown={self._config.cooldown_sec}s"
        )

    def _on_intent(self, msg: String) -> None:
        try:
            parsed = parse_intent_message(msg.data)
            self._intent_water = parsed["water"]
            self._intent_reason = parsed["reason"]
        except (TypeError, ValueError) as exc:
            self.get_logger().warn(f"bad intent: {exc}")

    def _on_soil(self, msg: Float32) -> None:
        if msg.data is None or (
            isinstance(msg.data, float) and (math.isnan(msg.data) or math.isinf(msg.data))
        ):
            self._soil = None
        else:
            self._soil = float(msg.data)

    def _on_timer(self) -> None:
        # Refresh e_stop from parameter for runtime override
        self._state.e_stop = bool(self.get_parameter("e_stop").value)
        now = time.monotonic()
        decision = evaluate_safety(
            intent_water=self._intent_water,
            soil_moisture=self._soil,
            config=self._config,
            state=self._state,
            now_mono=now,
        )
        apply_safety_transition(decision, self._state, now_mono=now)
        reason = decision.reason
        if decision.allow_water and self._intent_reason:
            reason = f"{decision.reason}:{self._intent_reason}"
        self._publish_command(decision.allow_water, reason)

    def _publish_command(self, water: bool, reason: str) -> None:
        out = String()
        out.data = build_command_message(water=water, reason=reason)
        self._pub.publish(out)
        self.get_logger().info(f"command water={water} reason={reason}")

    def destroy_node(self) -> bool:
        self._publish_command(False, "shutdown_off")
        return super().destroy_node()


def main(args: list[str] | None = None) -> None:
    rclpy.init(args=args)
    node: SafetyNode | None = None
    try:
        node = SafetyNode()
        rclpy.spin(node)
    except KeyboardInterrupt:
        if node is not None:
            node.get_logger().info("Safety interrupted")
    finally:
        if node is not None:
            node.get_logger().info("Safety shutting down")
            node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
