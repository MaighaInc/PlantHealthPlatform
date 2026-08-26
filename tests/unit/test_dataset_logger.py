"""Unit tests for dataset logger — no ROS required."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pytest

_ML = Path(__file__).resolve().parents[2] / "ml"
sys.path.insert(0, str(_ML))

from plant_health_data import DatasetLogger, DatasetLoggerError, DatasetRecord  # noqa: E402


def _img() -> np.ndarray:
    return np.full((32, 32, 3), 80, dtype=np.uint8)


def test_append_creates_layout_and_manifest(tmp_path: Path) -> None:
    root = tmp_path / "ds1"
    logger = DatasetLogger(root, dataset_id="ds1")
    record = logger.append_record(
        _img(),
        plant_id="plant_001",
        timestamp_iso="2026-08-25T18:30:00.000000Z",
        soil_moisture=41.2,
        temperature=27.8,
        label="healthy",
    )
    assert (root / record.image).is_file()
    assert logger.load_manifest().record_count == 1
    records = logger.iter_records()
    assert len(records) == 1
    assert records[0].soil_moisture == 41.2
    assert records[0].label == "healthy"


def test_refuses_overwrite(tmp_path: Path) -> None:
    logger = DatasetLogger(tmp_path / "ds2")
    logger.append_record(
        _img(),
        plant_id="plant_001",
        timestamp_iso="2026-08-25T18:30:00.000000Z",
    )
    rel = logger.next_image_relpath(
        plant_id="plant_001", timestamp_iso="2026-08-25T18:30:01.000000Z"
    )
    (logger.root / rel).parent.mkdir(parents=True, exist_ok=True)
    (logger.root / rel).write_bytes(b"x")
    with pytest.raises(DatasetLoggerError, match="overwrite"):
        logger.append_record(
            _img(),
            plant_id="plant_001",
            timestamp_iso="2026-08-25T18:30:01.000000Z",
        )


def test_rejects_missing_plant_id(tmp_path: Path) -> None:
    logger = DatasetLogger(tmp_path / "ds3")
    with pytest.raises(DatasetLoggerError, match="plant_id"):
        logger.append_record(
            _img(),
            plant_id="  ",
            timestamp_iso="2026-08-25T18:30:00.000000Z",
        )


def test_rejects_missing_timestamp(tmp_path: Path) -> None:
    logger = DatasetLogger(tmp_path / "ds4")
    with pytest.raises(DatasetLoggerError, match="timestamp"):
        logger.append_record(_img(), plant_id="plant_001", timestamp_iso="")


def test_record_from_dict_requires_fields() -> None:
    with pytest.raises(ValueError, match="plant_id"):
        DatasetRecord.from_dict({"timestamp_iso": "t", "image": "images/a.png"})


def test_manifest_json_roundtrip(tmp_path: Path) -> None:
    logger = DatasetLogger(tmp_path / "ds5", dataset_id="demo")
    logger.append_record(
        _img(),
        plant_id="p1",
        timestamp_iso="2026-08-25T18:30:00.000000Z",
    )
    data = json.loads(logger.manifest_path.read_text(encoding="utf-8"))
    assert data["dataset_id"] == "demo"
    assert data["record_count"] == 1
    assert data["layout"]["metadata"] == "metadata/records.jsonl"
