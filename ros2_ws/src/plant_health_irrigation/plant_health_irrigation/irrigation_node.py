"""ROS node: /irrigation/command → GPIOInterface → /irrigation/status (PHP-17)."""

from __future__ import annotations

import json

import rclpy
from rclpy.node import Node
from std_msgs.msg import String

from plant_health_irrigation.actuator import (
    apply_irrigation_command,
    parse_irrigation_command,
)
from plant_health_irrigation.factory import GPIOFactoryError, create_gpio
from plant_health_irrigation.interfaces import PinState
from plant_health_irrigation.parameters import (
    IrrigationNodeParams,
    IrrigationParameterError,
)


class IrrigationNode(Node):
    """
    Actuation driver using GPIOInterface only.

    SIMULATION/DEVELOPMENT → MockGPIO exclusively (factory-enforced).
    Does not implement safety limits (PHP-18).
    """

    def __init__(self) -> None:
        super().__init__("plant_health_irrigation")

        self.declare_parameter("command_topic", "/irrigation/command")
        self.declare_parameter("status_topic", "/irrigation/status")
        self.declare_parameter("development_mode", "SIMULATION")
        self.declare_parameter("gpio_backend", "auto")
        self.declare_parameter("relay_pin", 17)
        self.declare_parameter("active_high", True)

        try:
            params = IrrigationNodeParams.from_raw(
                command_topic=str(self.get_parameter("command_topic").value),
                status_topic=str(self.get_parameter("status_topic").value),
                development_mode=str(self.get_parameter("development_mode").value),
                gpio_backend=str(self.get_parameter("gpio_backend").value),
                relay_pin=int(self.get_parameter("relay_pin").value),
                active_high=bool(self.get_parameter("active_high").value),
            )
            self._gpio = create_gpio(
                mode=params.development_mode, backend=params.gpio_backend
            )
        except (IrrigationParameterError, GPIOFactoryError, TypeError, ValueError) as exc:
            self.get_logger().error(f"Invalid parameters / GPIO: {exc}")
            raise IrrigationParameterError(str(exc)) from exc

        self._pin = params.relay_pin
        self._active_high = params.active_high
        self._gpio.setup_output(self._pin, initial=PinState.LOW)

        self._pub = self.create_publisher(String, params.status_topic, 10)
        self.create_subscription(String, params.command_topic, self._on_command, 10)

        self.get_logger().info(
            "Irrigation GPIO started "
            f"cmd={params.command_topic} status={params.status_topic} "
            f"mode={params.development_mode} pin={self._pin} "
            f"gpio={type(self._gpio).__name__}"
        )

    def _on_command(self, msg: String) -> None:
        try:
            command = parse_irrigation_command(msg.data)
            status = apply_irrigation_command(
                self._gpio,
                command,
                relay_pin=self._pin,
                active_high=self._active_high,
            )
        except (TypeError, ValueError, RuntimeError, json.JSONDecodeError) as exc:
            self.get_logger().warn(f"command skipped: {exc}")
            return

        out = String()
        out.data = status.to_message_data()
        self._pub.publish(out)
        self.get_logger().info(
            f"relay water={status.water} pin={status.pin} "
            f"state={status.pin_state} reason={status.reason}"
        )

    def destroy_node(self) -> bool:
        try:
            self._gpio.cleanup()
        except Exception as exc:  # noqa: BLE001
            self.get_logger().warn(f"GPIO cleanup: {exc}")
        return super().destroy_node()


def main(args: list[str] | None = None) -> None:
    rclpy.init(args=args)
    node: IrrigationNode | None = None
    try:
        node = IrrigationNode()
        rclpy.spin(node)
    except IrrigationParameterError:
        pass
    except KeyboardInterrupt:
        if node is not None:
            node.get_logger().info("Irrigation interrupted")
    finally:
        if node is not None:
            node.get_logger().info("Irrigation shutting down")
            node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
