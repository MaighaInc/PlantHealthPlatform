"""ROS 2 node publishing virtual soil/environment sensor readings."""

from __future__ import annotations

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32

from plant_health_sensors.parameters import SensorParameterError, VirtualPublisherParams
from plant_health_sensors.sensor_kinds import (
    DEFAULT_BASE_VALUES,
    DEFAULT_BOUNDS,
    DEFAULT_TOPICS,
    SensorKind,
)
from plant_health_sensors.virtual_sensor import (
    VirtualSensor,
    VirtualSensorConfig,
    reading_to_float32,
)


class VirtualSensorPublisherNode(Node):
    """Publishes configured virtual sensors on canonical environment/soil topics."""

    def __init__(self) -> None:
        super().__init__("virtual_sensor_publisher")

        self.declare_parameter("sample_period_sec", 1.0)
        self.declare_parameter(
            "enabled_kinds",
            "soil_moisture,temperature,humidity,light,co2",
        )
        self.declare_parameter("seed", 42)
        self.declare_parameter("noise_std", 0.5)
        self.declare_parameter("outlier_probability", 0.0)
        self.declare_parameter("invalid_probability", 0.0)

        try:
            params = VirtualPublisherParams.from_raw(
                sample_period_sec=float(
                    self.get_parameter("sample_period_sec").value
                ),
                enabled_kinds=str(self.get_parameter("enabled_kinds").value),
                seed=int(self.get_parameter("seed").value),
                noise_std=float(self.get_parameter("noise_std").value),
                outlier_probability=float(
                    self.get_parameter("outlier_probability").value
                ),
                invalid_probability=float(
                    self.get_parameter("invalid_probability").value
                ),
            )
        except (SensorParameterError, TypeError, ValueError) as exc:
            self.get_logger().error(f"Invalid parameters: {exc}")
            raise SensorParameterError(str(exc)) from exc

        self._sensors: dict[SensorKind, VirtualSensor] = {}
        self._publishers = {}

        for index, kind in enumerate(params.enabled_kinds):
            topic = DEFAULT_TOPICS[kind]
            lo, hi = DEFAULT_BOUNDS[kind]
            cfg = VirtualSensorConfig(
                kind=kind,
                sensor_id=f"virtual_{kind.value}",
                base_value=DEFAULT_BASE_VALUES[kind],
                min_value=lo,
                max_value=hi,
                noise_std=params.noise_std,
                outlier_probability=params.outlier_probability,
                invalid_probability=params.invalid_probability,
                seed=params.seed + index,
            )
            self._sensors[kind] = VirtualSensor(cfg)
            self._publishers[kind] = self.create_publisher(Float32, topic, 10)
            self.get_logger().info(
                f"Virtual sensor enabled kind={kind.value} topic={topic}"
            )

        self._timer = self.create_timer(params.sample_period_sec, self._on_timer)
        self.get_logger().info(
            "Virtual sensor publisher started "
            f"period_sec={params.sample_period_sec} seed={params.seed} "
            f"kinds={[k.value for k in params.enabled_kinds]}"
        )

    def _on_timer(self) -> None:
        for kind, sensor in self._sensors.items():
            reading = sensor.read()
            msg = Float32()
            msg.data = reading_to_float32(reading)
            self._publishers[kind].publish(msg)

            if reading.is_invalid:
                self.get_logger().warn(
                    f"Published INVALID reading kind={kind.value} "
                    f"sensor_id={reading.sensor_id}"
                )
            else:
                level = "warn" if reading.is_outlier else "info"
                log = self.get_logger().warn if level == "warn" else self.get_logger().info
                log(
                    f"Published kind={kind.value} value={reading.value:.3f} "
                    f"outlier={reading.is_outlier}"
                )


def main(args: list[str] | None = None) -> None:
    rclpy.init(args=args)
    node: VirtualSensorPublisherNode | None = None
    try:
        node = VirtualSensorPublisherNode()
        rclpy.spin(node)
    except SensorParameterError:
        pass
    except KeyboardInterrupt:
        if node is not None:
            node.get_logger().info("Virtual sensor publisher interrupted")
    finally:
        if node is not None:
            node.get_logger().info("Virtual sensor publisher shutting down")
            node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
