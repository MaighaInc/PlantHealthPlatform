"""Dataset logger — reproducible layout, manifests, no silent overwrites."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import cv2
import numpy as np
import numpy.typing as npt

from plant_health_data.records import DatasetRecord

_SAFE_PLANT_ID = re.compile(r"^[A-Za-z0-9_-]+$")


class DatasetLoggerError(ValueError):
    """Invalid dataset logging operation."""


@dataclass
class Manifest:
    dataset_id: str
    created_utc: str
    updated_utc: str
    record_count: int
    root: str
    schema_version: str = "1.0"

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "dataset_id": self.dataset_id,
            "created_utc": self.created_utc,
            "updated_utc": self.updated_utc,
            "record_count": self.record_count,
            "root": self.root,
            "layout": {
                "images": "images/",
                "metadata": "metadata/records.jsonl",
                "manifest": "manifests/manifest.json",
                "labels": "labels/",
            },
        }


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def _compact_ts(timestamp_iso: str) -> str:
    # 2026-08-25T18:30:00.123456Z → 20260825T183000
    cleaned = timestamp_iso.replace("-", "").replace(":", "").replace(".", "")
    return cleaned[:15] if len(cleaned) >= 15 else cleaned


class DatasetLogger:
    """
    Writes images + JSONL metadata under ``ml/datasets/<name>/``.

    Never overwrites an existing image path. Manifest tracks record counts.
    """

    def __init__(self, root: Path, *, dataset_id: str | None = None) -> None:
        self.root = root.resolve()
        self.dataset_id = dataset_id or self.root.name
        self.images_dir = self.root / "images"
        self.labels_dir = self.root / "labels"
        self.metadata_dir = self.root / "metadata"
        self.manifests_dir = self.root / "manifests"
        self.records_path = self.metadata_dir / "records.jsonl"
        self.manifest_path = self.manifests_dir / "manifest.json"
        self._seq = 0
        self._ensure_layout()
        self._seq = self._count_records()

    def _ensure_layout(self) -> None:
        for path in (
            self.images_dir,
            self.labels_dir,
            self.metadata_dir,
            self.manifests_dir,
        ):
            path.mkdir(parents=True, exist_ok=True)
        if not self.manifest_path.is_file():
            now = _utc_now()
            manifest = Manifest(
                dataset_id=self.dataset_id,
                created_utc=now,
                updated_utc=now,
                record_count=0,
                root=str(self.root),
            )
            self._write_manifest(manifest)

    def _count_records(self) -> int:
        if not self.records_path.is_file():
            return 0
        count = 0
        with self.records_path.open("r", encoding="utf-8") as handle:
            for line in handle:
                if line.strip():
                    count += 1
        return count

    def _write_manifest(self, manifest: Manifest) -> None:
        self.manifest_path.write_text(
            json.dumps(manifest.to_dict(), indent=2) + "\n",
            encoding="utf-8",
        )

    def load_manifest(self) -> Manifest:
        data = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        return Manifest(
            dataset_id=str(data["dataset_id"]),
            created_utc=str(data["created_utc"]),
            updated_utc=str(data["updated_utc"]),
            record_count=int(data["record_count"]),
            root=str(data.get("root", self.root)),
            schema_version=str(data.get("schema_version", "1.0")),
        )

    def next_image_relpath(self, *, plant_id: str, timestamp_iso: str) -> str:
        if not _SAFE_PLANT_ID.match(plant_id):
            raise DatasetLoggerError(
                f"plant_id must match [A-Za-z0-9_-]+, got {plant_id!r}"
            )
        seq = self._seq + 1
        name = f"{plant_id}_{seq:06d}_{_compact_ts(timestamp_iso)}.png"
        return f"images/{name}"

    def append_record(
        self,
        image_bgr: npt.NDArray[np.uint8],
        *,
        plant_id: str,
        timestamp_iso: str,
        soil_moisture: float | None = None,
        temperature: float | None = None,
        humidity: float | None = None,
        light: float | None = None,
        co2: float | None = None,
        label: str | None = None,
        camera_source: str | None = None,
        frame_id: int | None = None,
        extra: dict | None = None,
    ) -> DatasetRecord:
        if image_bgr is None or not isinstance(image_bgr, np.ndarray) or image_bgr.size == 0:
            raise DatasetLoggerError("image_bgr must be a non-empty ndarray")
        if not plant_id or not str(plant_id).strip():
            raise DatasetLoggerError("plant_id is required")
        if not timestamp_iso or not str(timestamp_iso).strip():
            raise DatasetLoggerError("timestamp_iso is required")

        rel = self.next_image_relpath(plant_id=plant_id, timestamp_iso=timestamp_iso)
        abs_path = self.root / rel
        if abs_path.exists():
            raise DatasetLoggerError(f"refusing to overwrite existing image: {rel}")

        abs_path.parent.mkdir(parents=True, exist_ok=True)
        if not cv2.imwrite(str(abs_path), image_bgr):
            raise DatasetLoggerError(f"failed to write image: {rel}")

        record = DatasetRecord(
            plant_id=plant_id,
            timestamp_iso=timestamp_iso,
            image=rel.replace("\\", "/"),
            soil_moisture=soil_moisture,
            temperature=temperature,
            humidity=humidity,
            light=light,
            co2=co2,
            label=label,
            camera_source=camera_source,
            frame_id=frame_id,
            extra=dict(extra or {}),
        )
        record.validate()

        with self.records_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record.to_dict(), sort_keys=True) + "\n")

        self._seq += 1
        created = self.load_manifest().created_utc
        self._write_manifest(
            Manifest(
                dataset_id=self.dataset_id,
                created_utc=created,
                updated_utc=_utc_now(),
                record_count=self._seq,
                root=str(self.root),
            )
        )
        return record

    def iter_records(self) -> list[DatasetRecord]:
        if not self.records_path.is_file():
            return []
        records: list[DatasetRecord] = []
        with self.records_path.open("r", encoding="utf-8") as handle:
            for line_no, line in enumerate(handle, start=1):
                stripped = line.strip()
                if not stripped:
                    continue
                try:
                    records.append(DatasetRecord.from_dict(json.loads(stripped)))
                except (json.JSONDecodeError, ValueError, TypeError) as exc:
                    raise DatasetLoggerError(
                        f"corrupt records.jsonl line {line_no}: {exc}"
                    ) from exc
        return records
