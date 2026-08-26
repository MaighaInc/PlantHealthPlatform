"""FastAPI application — Controller → Service → Repository (PHP-20)."""

from __future__ import annotations

import os
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.db.session import init_db, make_engine, make_session_factory
from app.repositories import (
    HealthPredictionRepo,
    IrrigationEventRepo,
    MlModelRepo,
    PlantRepo,
    SensorReadingRepo,
)
from app.services import IrrigationService, PlantService, SystemService

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite+pysqlite:///./phs.db")
_engine = make_engine(DATABASE_URL)
init_db(_engine)
_SessionLocal = make_session_factory(_engine)

app = FastAPI(title="Plant Health System API", version="0.1.0")


def get_db() -> Session:
    session = _SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


Db = Annotated[Session, Depends(get_db)]


class PlantOut(BaseModel):
    id: int
    name: str
    variety: str | None = None


class PlantCreate(BaseModel):
    name: str = Field(min_length=1, max_length=128)
    variety: str | None = None


class ReadingOut(BaseModel):
    id: int
    plant_id: int
    kind: str
    value: float | None
    unit: str | None


class IrrigationEventOut(BaseModel):
    id: int
    plant_id: int | None
    water: bool
    reason: str
    source: str


class ManualIrrigationIn(BaseModel):
    water: bool
    reason: str = "manual"
    plant_id: int | None = None


class ModelOut(BaseModel):
    id: int
    name: str
    version: str
    format: str
    artifact: str


class StatusOut(BaseModel):
    status: str
    database: str
    mode: str


@app.get("/api/plants", response_model=list[PlantOut])
def list_plants(
    db: Db,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
) -> list[PlantOut]:
    rows = PlantService(PlantRepo(db)).list(limit=limit, offset=offset)
    return [PlantOut(id=r.id, name=r.name, variety=r.variety) for r in rows]


@app.post("/api/plants", response_model=PlantOut, status_code=201)
def create_plant(body: PlantCreate, db: Db) -> PlantOut:
    plant = PlantService(PlantRepo(db)).create(name=body.name, variety=body.variety)
    return PlantOut(id=plant.id, name=plant.name, variety=plant.variety)


@app.get("/api/plants/{plant_id}", response_model=PlantOut)
def get_plant(plant_id: int, db: Db) -> PlantOut:
    plant = PlantService(PlantRepo(db)).get(plant_id)
    if plant is None:
        raise HTTPException(status_code=404, detail="plant not found")
    return PlantOut(id=plant.id, name=plant.name, variety=plant.variety)


@app.get("/api/plants/{plant_id}/health")
def plant_health(plant_id: int, db: Db) -> dict:
    from sqlalchemy import select

    from app.db.models import HealthPrediction

    plant = PlantRepo(db).get(plant_id)
    if plant is None:
        raise HTTPException(status_code=404, detail="plant not found")
    row = db.scalars(
        select(HealthPrediction)
        .where(HealthPrediction.plant_id == plant_id)
        .order_by(HealthPrediction.id.desc())
        .limit(1)
    ).first()
    if row is None:
        return {"plant_id": plant_id, "status": "unknown", "confidence": 0.0}
    return {
        "plant_id": plant_id,
        "status": row.status,
        "confidence": row.confidence,
        "model_name": row.model_name,
        "model_version": row.model_version,
    }


@app.get("/api/sensors/{plant_id}/readings", response_model=list[ReadingOut])
def sensor_readings(plant_id: int, db: Db, limit: int = Query(50, ge=1, le=200)) -> list[ReadingOut]:
    rows = SensorReadingRepo(db).list_for_plant(plant_id, limit=limit)
    return [
        ReadingOut(id=r.id, plant_id=r.plant_id, kind=r.kind, value=r.value, unit=r.unit)
        for r in rows
    ]


@app.get("/api/irrigation/events", response_model=list[IrrigationEventOut])
def irrigation_events(db: Db, limit: int = Query(50, ge=1, le=200)) -> list[IrrigationEventOut]:
    rows = IrrigationEventRepo(db).list(limit=limit)
    return [
        IrrigationEventOut(
            id=r.id, plant_id=r.plant_id, water=r.water, reason=r.reason, source=r.source
        )
        for r in rows
    ]


@app.post("/api/irrigation/manual", response_model=IrrigationEventOut, status_code=201)
def manual_irrigation(body: ManualIrrigationIn, db: Db) -> IrrigationEventOut:
    # Auth enforced in PHP-27; DEVELOPMENT allows
    event = IrrigationService(IrrigationEventRepo(db)).manual(
        water=body.water, reason=body.reason, plant_id=body.plant_id
    )
    return IrrigationEventOut(
        id=event.id,
        plant_id=event.plant_id,
        water=event.water,
        reason=event.reason,
        source=event.source,
    )


@app.get("/api/models", response_model=list[ModelOut])
def list_models(db: Db) -> list[ModelOut]:
    rows = MlModelRepo(db).list()
    return [
        ModelOut(
            id=r.id, name=r.name, version=r.version, format=r.format, artifact=r.artifact
        )
        for r in rows
    ]


@app.get("/api/system/status", response_model=StatusOut)
def system_status() -> StatusOut:
    return SystemService.status(database_url=DATABASE_URL)


@app.get("/health")
def health() -> dict:
    return {"ok": True}
