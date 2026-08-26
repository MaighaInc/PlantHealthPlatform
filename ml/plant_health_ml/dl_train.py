"""Train feature MLP, evaluate vs classical baseline, export ONNX (PHP-13)."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Sequence

import numpy as np
import torch
from torch import nn

from plant_health_ml.baseline import build_baseline_pipeline
from plant_health_ml.dl_model import FeatureMLP
from plant_health_ml.leakage import check_leakage
from plant_health_ml.metrics import compute_classification_metrics
from plant_health_ml.preprocess import FEATURE_KEYS, LABELS, records_to_matrix
from plant_health_ml.registry import upsert_registry_entry
from plant_health_ml.splits import plant_group_split

MODEL_NAME = "plant-health-mlp"
DEFAULT_VERSION = "1.0.0"
LABEL_TO_IDX = {label: i for i, label in enumerate(LABELS)}
IDX_TO_LABEL = {i: label for label, i in LABEL_TO_IDX.items()}


@dataclass(frozen=True)
class TrainedMLP:
    model_name: str
    model_version: str
    torch_path: Path
    onnx_path: Path
    metadata_path: Path
    metrics: dict[str, Any]
    baseline_metrics: dict[str, Any]
    comparison: dict[str, Any]


def _standardize(
    x_train: np.ndarray, x_test: np.ndarray
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    mean = x_train.mean(axis=0)
    std = x_train.std(axis=0)
    std = np.where(std < 1e-8, 1.0, std)
    return (x_train - mean) / std, (x_test - mean) / std, mean, std


def _labels_to_indices(y: np.ndarray) -> np.ndarray:
    return np.asarray([LABEL_TO_IDX[str(v)] for v in y], dtype=np.int64)


def train_feature_mlp(
    records: Sequence[dict[str, Any]],
    *,
    model_dir: Path,
    model_version: str = DEFAULT_VERSION,
    seed: int = 42,
    test_size: float = 0.25,
    epochs: int = 80,
    hidden: int = 32,
    lr: float = 1e-2,
) -> TrainedMLP:
    """Plant-group split → leakage gate → train MLP → compare to RF → ONNX export."""
    if not records:
        raise ValueError("records must be non-empty")

    train, test = plant_group_split(records, test_size=test_size, seed=seed)
    leakage = check_leakage(train, test, feature_keys=FEATURE_KEYS)
    if not leakage.ok:
        kinds = ", ".join(f.kind for f in leakage.findings)
        raise ValueError(f"leakage gate failed: {kinds}")

    x_train, y_train, keys = records_to_matrix(train)
    x_test, y_test, _ = records_to_matrix(test, feature_keys=keys)

    # Classical baseline on the same split (comparator)
    rf = build_baseline_pipeline(random_state=seed)
    rf.fit(x_train, y_train)
    rf_pred = rf.predict(x_test)
    baseline_metrics = compute_classification_metrics(y_test, rf_pred, labels=LABELS)

    x_tr, x_te, mean, std = _standardize(x_train, x_test)
    y_tr_i = _labels_to_indices(y_train)
    y_te_i = _labels_to_indices(y_test)

    torch.manual_seed(seed)
    device = torch.device("cpu")
    model = FeatureMLP(n_features=len(keys), n_classes=len(LABELS), hidden=hidden).to(device)
    opt = torch.optim.Adam(model.parameters(), lr=lr)
    loss_fn = nn.CrossEntropyLoss()

    xt = torch.tensor(x_tr, dtype=torch.float32, device=device)
    yt = torch.tensor(y_tr_i, dtype=torch.long, device=device)
    model.train()
    for _ in range(epochs):
        opt.zero_grad()
        logits = model(xt)
        loss = loss_fn(logits, yt)
        loss.backward()
        opt.step()

    model.eval()
    with torch.no_grad():
        logits = model(torch.tensor(x_te, dtype=torch.float32, device=device))
        pred_i = logits.argmax(dim=1).cpu().numpy()
    y_pred = np.asarray([IDX_TO_LABEL[int(i)] for i in pred_i], dtype=object)
    metrics = compute_classification_metrics(y_test, y_pred, labels=LABELS)

    comparison = {
        "mlp_accuracy": metrics["accuracy"],
        "baseline_accuracy": baseline_metrics["accuracy"],
        "mlp_f1_macro": metrics["f1_macro"],
        "baseline_f1_macro": baseline_metrics["f1_macro"],
        "mlp_minus_baseline_accuracy": float(
            metrics["accuracy"] - baseline_metrics["accuracy"]
        ),
        "note": (
            "Classical RF remains the preferred tabular baseline (ADR-0002); "
            "MLP exists for ONNX edge export and Stage-4 progression."
        ),
    }

    model_dir = Path(model_dir)
    model_dir.mkdir(parents=True, exist_ok=True)
    stem = f"{MODEL_NAME}-{model_version}"
    torch_path = model_dir / f"{stem}.pt"
    onnx_path = model_dir / f"{stem}.onnx"
    metadata_path = model_dir / f"{stem}.meta.json"

    payload = {
        "model_name": MODEL_NAME,
        "model_version": model_version,
        "state_dict": model.state_dict(),
        "feature_keys": keys,
        "labels": list(LABELS),
        "mean": mean.tolist(),
        "std": std.tolist(),
        "hidden": hidden,
    }
    torch.save(payload, torch_path)

    export_onnx(model, n_features=len(keys), onnx_path=onnx_path)

    metadata = {
        "model_name": MODEL_NAME,
        "model_version": model_version,
        "algorithm": "FeatureMLP",
        "feature_keys": keys,
        "labels": list(LABELS),
        "hidden": hidden,
        "epochs": epochs,
        "seed": seed,
        "mean": mean.tolist(),
        "std": std.tolist(),
        "n_train": len(train),
        "n_test": len(test),
        "metrics": metrics,
        "baseline_metrics": baseline_metrics,
        "comparison": comparison,
        "artifacts": {"torch": torch_path.name, "onnx": onnx_path.name},
        "trained_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        "adr": "0002",
    }
    metadata_path.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")

    upsert_registry_entry(
        model_dir,
        {
            "model_name": MODEL_NAME,
            "model_version": model_version,
            "format": "onnx",
            "artifact": onnx_path.name,
            "framework": "pytorch",
            "task": "plant_health_classification",
            "labels": list(LABELS),
            "metrics": {"accuracy": metrics["accuracy"], "f1_macro": metrics["f1_macro"]},
            "baseline_accuracy": baseline_metrics["accuracy"],
            "adr": "0002",
        },
    )
    upsert_registry_entry(
        model_dir,
        {
            "model_name": MODEL_NAME,
            "model_version": model_version,
            "format": "torch",
            "artifact": torch_path.name,
            "framework": "pytorch",
            "task": "plant_health_classification",
            "labels": list(LABELS),
            "adr": "0002",
        },
    )
    upsert_registry_entry(
        model_dir,
        {
            "model_name": "plant-health-classifier",
            "model_version": "1.0.0",
            "format": "joblib",
            "artifact": "plant-health-classifier-1.0.0.joblib",
            "framework": "sklearn",
            "task": "plant_health_classification",
            "labels": list(LABELS),
            "role": "classical_baseline",
            "adr": "0002",
        },
    )

    return TrainedMLP(
        model_name=MODEL_NAME,
        model_version=model_version,
        torch_path=torch_path,
        onnx_path=onnx_path,
        metadata_path=metadata_path,
        metrics=metrics,
        baseline_metrics=baseline_metrics,
        comparison=comparison,
    )


def export_onnx(model: FeatureMLP, *, n_features: int, onnx_path: Path) -> Path:
    """Export MLP to ONNX. Requires the ``onnx`` package (see repo ``.venv`` on Windows)."""
    try:
        import onnx  # noqa: F401
    except ImportError as exc:
        raise ImportError(
            "ONNX export requires the 'onnx' package. "
            "On Windows, use the project .venv (short path): "
            "python -m venv .venv && .venv/Scripts/pip install -e '.[ml]' "
            "(or pip install onnx onnxruntime torch scikit-learn)."
        ) from exc

    model.eval()
    dummy = torch.zeros(1, n_features, dtype=torch.float32)
    onnx_path = Path(onnx_path)
    onnx_path.parent.mkdir(parents=True, exist_ok=True)
    torch.onnx.export(
        model,
        dummy,
        str(onnx_path),
        input_names=["features"],
        output_names=["logits"],
        dynamic_axes={"features": {0: "batch"}, "logits": {0: "batch"}},
        opset_version=17,
        dynamo=False,
    )
    return onnx_path


def load_onnx_session(onnx_path: Path):
    """Smoke-load ONNX with ONNX Runtime (preferred edge runtime)."""
    import onnxruntime as ort

    path = Path(onnx_path)
    if not path.is_file():
        raise FileNotFoundError(path)
    session = ort.InferenceSession(str(path), providers=["CPUExecutionProvider"])
    return session


def onnx_predict_labels(
    session,
    x: np.ndarray,
    *,
    mean: Sequence[float],
    std: Sequence[float],
) -> list[str]:
    mean_a = np.asarray(mean, dtype=np.float32)
    std_a = np.asarray(std, dtype=np.float32)
    std_a = np.where(std_a < 1e-8, 1.0, std_a)
    x_n = ((np.asarray(x, dtype=np.float32) - mean_a) / std_a).astype(np.float32)
    logits = session.run(None, {"features": x_n})[0]
    idx = np.argmax(logits, axis=1)
    return [IDX_TO_LABEL[int(i)] for i in idx]
