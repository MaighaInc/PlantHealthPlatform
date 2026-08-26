"""Classical ML package for PlantHealthPlatform."""

from plant_health_ml.baseline import (
    DEFAULT_VERSION,
    MODEL_NAME,
    TrainedBaseline,
    load_baseline,
    predict_label,
    train_baseline,
)
from plant_health_ml.preprocess import FEATURE_KEYS, LABELS, records_to_matrix

__all__ = [
    "DEFAULT_VERSION",
    "FEATURE_KEYS",
    "LABELS",
    "MODEL_NAME",
    "TrainedBaseline",
    "load_baseline",
    "predict_label",
    "records_to_matrix",
    "train_baseline",
]
