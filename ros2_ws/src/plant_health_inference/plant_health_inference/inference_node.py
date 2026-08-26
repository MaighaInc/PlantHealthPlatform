"""ROS node: /plant/features → ML inference → /plant/disease_prediction (PHP-14)."""

from __future__ import annotations

import json

import rclpy
from rclpy.node import Node
from std_msgs.msg import String

from plant_health_inference.engine import (
    create_backend,
    parse_features_message,
    run_inference,
)
from plant_health_inference.parameters import InferenceNodeParams, InferenceParameterError


class InferenceNode(Node):
    """
    Online inference only — no training, no GPIO, no DB schema ownership.

    Capstone Scenario 4 (SIMULATION): features in → prediction JSON out.
    """

    def __init__(self) -> None:
        super().__init__("plant_health_inference")

        self.declare_parameter("features_topic", "/plant/features")
        self.declare_parameter("prediction_topic", "/plant/disease_prediction")
        self.declare_parameter("backend", "mock")
        self.declare_parameter("model_path", "")
        self.declare_parameter("confidence_threshold", 0.55)
        self.declare_parameter("mock_label", "healthy")
        self.declare_parameter("mock_confidence", 0.95)

        try:
            params = InferenceNodeParams.from_raw(
                features_topic=str(self.get_parameter("features_topic").value),
                prediction_topic=str(self.get_parameter("prediction_topic").value),
                backend=str(self.get_parameter("backend").value),
                model_path=str(self.get_parameter("model_path").value),
                confidence_threshold=float(
                    self.get_parameter("confidence_threshold").value
                ),
                mock_label=str(self.get_parameter("mock_label").value),
                mock_confidence=float(self.get_parameter("mock_confidence").value),
            )
        except (InferenceParameterError, TypeError, ValueError) as exc:
            self.get_logger().error(f"Invalid parameters: {exc}")
            raise InferenceParameterError(str(exc)) from exc

        self._threshold = params.confidence_threshold
        try:
            self._backend = create_backend(
                params.backend,
                model_path=params.model_path or None,
                mock_label=params.mock_label,
                mock_confidence=params.mock_confidence,
            )
        except (OSError, ValueError) as exc:
            self.get_logger().error(f"Failed to load backend: {exc}")
            raise InferenceParameterError(str(exc)) from exc

        self._pub = self.create_publisher(String, params.prediction_topic, 10)
        self.create_subscription(String, params.features_topic, self._on_features, 10)

        self.get_logger().info(
            "Inference started "
            f"in={params.features_topic} out={params.prediction_topic} "
            f"backend={params.backend} model={self._backend.model_name}-"
            f"{self._backend.model_version} threshold={self._threshold}"
        )

    def _on_features(self, msg: String) -> None:
        try:
            features = parse_features_message(msg.data)
            result = run_inference(
                features, self._backend, confidence_threshold=self._threshold
            )
        except (TypeError, ValueError, json.JSONDecodeError) as exc:
            self.get_logger().warn(f"inference skipped: {exc}")
            return
        except Exception as exc:  # noqa: BLE001
            self.get_logger().warn(f"inference failed: {exc}")
            return

        out = String()
        out.data = result.to_message_data()
        self._pub.publish(out)
        self.get_logger().info(
            f"prediction={result.prediction} conf={result.confidence:.3f} "
            f"latency_ms={result.latency_ms:.2f} "
            f"model={result.model_name}-{result.model_version}"
        )


def main(args: list[str] | None = None) -> None:
    rclpy.init(args=args)
    node: InferenceNode | None = None
    try:
        node = InferenceNode()
        rclpy.spin(node)
    except InferenceParameterError:
        pass
    except KeyboardInterrupt:
        if node is not None:
            node.get_logger().info("Inference interrupted")
    finally:
        if node is not None:
            node.get_logger().info("Inference shutting down")
            node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
