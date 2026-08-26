"""Model version registry for classical + DL artifacts (PHP-13)."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REGISTRY_NAME = "registry.json"


def registry_path(model_dir: Path) -> Path:
    return Path(model_dir) / REGISTRY_NAME


def load_registry(model_dir: Path) -> dict[str, Any]:
    path = registry_path(model_dir)
    if not path.is_file():
        return {"schema_version": 1, "models": []}
    return json.loads(path.read_text(encoding="utf-8"))


def upsert_registry_entry(model_dir: Path, entry: dict[str, Any]) -> Path:
    """
    Insert or replace a registry row keyed by (model_name, model_version, format).
    """
    required = {"model_name", "model_version", "format", "artifact"}
    missing = required - set(entry)
    if missing:
        raise ValueError(f"registry entry missing keys: {sorted(missing)}")

    data = load_registry(model_dir)
    models: list[dict[str, Any]] = list(data.get("models") or [])
    key = (entry["model_name"], entry["model_version"], entry["format"])
    models = [
        m
        for m in models
        if (m.get("model_name"), m.get("model_version"), m.get("format")) != key
    ]
    row = dict(entry)
    row.setdefault(
        "registered_utc",
        datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
    )
    models.append(row)
    data["schema_version"] = 1
    data["models"] = models
    path = registry_path(model_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return path
