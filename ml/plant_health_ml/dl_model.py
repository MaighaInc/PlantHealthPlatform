"""Compact feature MLP for Stage-4 / ONNX export (PHP-13)."""

from __future__ import annotations

import torch
from torch import nn


class FeatureMLP(nn.Module):
    """Small MLP over schema v1.0 feature vectors (not an image CNN)."""

    def __init__(self, n_features: int, n_classes: int = 3, hidden: int = 32) -> None:
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(n_features, hidden),
            nn.ReLU(),
            nn.Linear(hidden, hidden),
            nn.ReLU(),
            nn.Linear(hidden, n_classes),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)
