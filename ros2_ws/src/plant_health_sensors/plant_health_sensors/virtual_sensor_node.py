"""ROS 2 node publishing sensor readings via SensorInterface only."""

from __future__ import annotations

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32

from plant_health_sensors.factory import create_sensors
from plant_health_sensors.interfaces import SensorInterface
from plant_health_sensors.parameters import SensorParameterError, VirtualPublisherParams
from plant_health_sensors.readings import reading_to_float32
from plant_health_sensors.sampling import sample_all
from plant_health_sensors.sensor_kinds import DEFAULT_TOPICS


class VirtualSensorPublisherNode(Node):
    """Publishes sensors on canonical topics — backends selected by mode/factory."""

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
        self.declare_parameter("development_mode", "SIMULATION")
        self.declare_parameter("sensor_backend", "auto")

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
                development_mode=str(self.get_parameter("development_mode").value),
                sensor_backend=str(self.get_parameter("sensor_backend").value),
            )
        except (SensorParameterError, TypeError, ValueError) as exc:
            self.get_logger().error(f"Invalid parameters: {exc}")
            raise SensorParameterError(str(exc)) from exc

        # Consumer holds SensorInterface only — no VirtualSensor / Mock / Real types.
        self._sensors: list[SensorInterface] = create_sensors(
            params.enabled_kinds,
            mode=params.development_mode,
            backend=params.sensor_backend,
            seed=params.seed,
            noise_std=params.noise_std,
            outlier_probability=params.outlier_probability,
            invalid_probability=params.invalid_probability,
        )
        self._publishers = {
            sensor.kind: self.create_publisher(Float32, DEFAULT_TOPICS[sensor.kind], 10)
            for sensor in self._sensors
        }

        for sensor in self._sensors:
            topic = DEFAULT_TOPICS[sensor.kind]
            self.get_logger().info(
                f"Sensor enabled kind={sensor.kind.value} "
                f"id={sensor.sensor_id} topic={topic} "
                f"type={type(sensor).__name__}"
            )

        self._timer = self.create_timer(params.sample_period_sec, self._on_timer)
        self.get_logger().info(
            "Sensor publisher started "
            f"mode={params.development_mode} backend={params.sensor_backend} "
            f"period_sec={params.sample_period_sec} seed={params.seed}"
        )

    def _on_timer(self) -> None:
        for reading in sample_all(self._sensors):
            msg = Float32()
            msg.data = reading_to_float32(reading)
            self._publishers[reading.kind].publish(msg)

            if reading.is_invalid:
                self.get_logger().warn(
                    f"Published INVALID reading kind={reading.kind.value} "
                    f"sensor_id={reading.sensor_id}"
                )
            else:
                log = (
                    self.get_logger().warn
                    if reading.is_outlier
                    else self.get_logger().info
                )
                log(
                    f"Published kind={reading.kind.value} value={reading.value:.3f} "
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
            node.get_logger().info("Sensor publisher interrupted")
    finally:
        if node is not None:
            node.get_logger().info("Sensor publisher shutting down")
            node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
