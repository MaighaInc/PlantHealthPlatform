"""Dataset record schema for PlantHealthPlatform (PHP-07)."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


REQUIRED_FIELDS = ("plant_id", "timestamp_iso")


@dataclass
class DatasetRecord:
    """One logged observation — paths are relative to the dataset root."""

    plant_id: str
    timestamp_iso: str
    image: str
    """Relative path under dataset root, e.g. images/plant_001_000001.png"""

    soil_moisture: float | None = None
    temperature: float | None = None
    humidity: float | None = None
    light: float | None = None
    co2: float | None = None
    label: str | None = None
    camera_source: str | None = None
    frame_id: int | None = None
    extra: dict[str, Any] = field(default_factory=dict)

    def validate(self) -> None:
        if not self.plant_id.strip():
            raise ValueError("plant_id is required")
        if not self.timestamp_iso.strip():
            raise ValueError("timestamp_iso is required")
        if not self.image.strip():
            raise ValueError("image path is required")
        if self.image.startswith("/") or ".." in self.image.replace("\\", "/"):
            raise ValueError(f"image path must be relative and safe, got {self.image!r}")

    def to_dict(self) -> dict[str, Any]:
        self.validate()
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> DatasetRecord:
        for key in REQUIRED_FIELDS:
            if key not in data or data[key] in (None, ""):
                raise ValueError(f"missing required metadata field: {key}")
        if "image" not in data or not data["image"]:
            raise ValueError("missing required metadata field: image")
        known = {f.name for f in cls.__dataclass_fields__.values()}  # type: ignore[attr-defined]
        kwargs = {k: v for k, v in data.items() if k in known}
        extra = dict(data.get("extra") or {})
        for k, v in data.items():
            if k not in known:
                extra[k] = v
        kwargs["extra"] = extra
        record = cls(**kwargs)
        record.validate()
        return record
