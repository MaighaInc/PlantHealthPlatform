"""Classical + Stage-4 ML package for PlantHealthPlatform."""

from plant_health_ml.baseline import (
    DEFAULT_VERSION,
    MODEL_NAME,
    TrainedBaseline,
    load_baseline,
    predict_label,
    predict_with_confidence,
    train_baseline,
)
from plant_health_ml.dl_train import (
    TrainedMLP,
    load_onnx_session,
    train_feature_mlp,
)
from plant_health_ml.evaluate import EvaluationResult, evaluate_baseline
from plant_health_ml.leakage import LeakageReport, check_leakage
from plant_health_ml.metrics import compute_classification_metrics
from plant_health_ml.preprocess import FEATURE_KEYS, LABELS, records_to_matrix
from plant_health_ml.splits import plant_group_split

__all__ = [
    "DEFAULT_VERSION",
    "FEATURE_KEYS",
    "LABELS",
    "MODEL_NAME",
    "EvaluationResult",
    "LeakageReport",
    "TrainedBaseline",
    "TrainedMLP",
    "check_leakage",
    "compute_classification_metrics",
    "evaluate_baseline",
    "load_baseline",
    "load_onnx_session",
    "plant_group_split",
    "predict_label",
    "predict_with_confidence",
    "records_to_matrix",
    "train_baseline",
    "train_feature_mlp",
]
