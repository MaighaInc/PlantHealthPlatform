"""Repository layer — no HTTP types (PHP-19)."""

from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import HealthPrediction, IrrigationEvent, MlModel, Plant, SensorReading


@dataclass
class PlantRepo:
    session: Session

    def create(self, *, name: str, variety: str | None = None) -> Plant:
        plant = Plant(name=name, variety=variety)
        self.session.add(plant)
        self.session.flush()
        return plant

    def get(self, plant_id: int) -> Plant | None:
        return self.session.get(Plant, plant_id)

    def list(self, *, limit: int = 100, offset: int = 0) -> list[Plant]:
        stmt = select(Plant).order_by(Plant.id).offset(offset).limit(limit)
        return list(self.session.scalars(stmt))


@dataclass
class SensorReadingRepo:
    session: Session

    def create(
        self,
        *,
        plant_id: int,
        kind: str,
        value: float | None,
        unit: str | None = None,
    ) -> SensorReading:
        row = SensorReading(plant_id=plant_id, kind=kind, value=value, unit=unit)
        self.session.add(row)
        self.session.flush()
        return row

    def list_for_plant(self, plant_id: int, *, limit: int = 100) -> list[SensorReading]:
        stmt = (
            select(SensorReading)
            .where(SensorReading.plant_id == plant_id)
            .order_by(SensorReading.id.desc())
            .limit(limit)
        )
        return list(self.session.scalars(stmt))


@dataclass
class IrrigationEventRepo:
    session: Session

    def create(
        self,
        *,
        water: bool,
        reason: str,
        source: str = "system",
        plant_id: int | None = None,
    ) -> IrrigationEvent:
        row = IrrigationEvent(
            plant_id=plant_id, water=water, reason=reason, source=source
        )
        self.session.add(row)
        self.session.flush()
        return row

    def list(self, *, limit: int = 100) -> list[IrrigationEvent]:
        stmt = select(IrrigationEvent).order_by(IrrigationEvent.id.desc()).limit(limit)
        return list(self.session.scalars(stmt))


@dataclass
class HealthPredictionRepo:
    session: Session

    def create(
        self,
        *,
        status: str,
        confidence: float,
        plant_id: int | None = None,
        model_name: str | None = None,
        model_version: str | None = None,
        payload: str | None = None,
    ) -> HealthPrediction:
        row = HealthPrediction(
            plant_id=plant_id,
            status=status,
            confidence=confidence,
            model_name=model_name,
            model_version=model_version,
            payload=payload,
        )
        self.session.add(row)
        self.session.flush()
        return row


@dataclass
class MlModelRepo:
    session: Session

    def upsert(
        self, *, name: str, version: str, format: str, artifact: str
    ) -> MlModel:
        stmt = select(MlModel).where(MlModel.name == name, MlModel.version == version)
        existing = self.session.scalars(stmt).first()
        if existing:
            existing.format = format
            existing.artifact = artifact
            self.session.flush()
            return existing
        row = MlModel(name=name, version=version, format=format, artifact=artifact)
        self.session.add(row)
        self.session.flush()
        return row

    def list(self) -> list[MlModel]:
        return list(self.session.scalars(select(MlModel).order_by(MlModel.id)))
