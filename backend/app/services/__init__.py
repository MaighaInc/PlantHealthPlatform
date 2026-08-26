"""Service layer — business logic, no Express/FastAPI types leaked to repos."""

from __future__ import annotations

import os

from app.db.models import IrrigationEvent, Plant
from app.repositories import IrrigationEventRepo, PlantRepo


class PlantService:
    def __init__(self, repo: PlantRepo) -> None:
        self._repo = repo

    def list(self, *, limit: int = 50, offset: int = 0) -> list[Plant]:
        return self._repo.list(limit=limit, offset=offset)

    def get(self, plant_id: int) -> Plant | None:
        return self._repo.get(plant_id)

    def create(self, *, name: str, variety: str | None = None) -> Plant:
        return self._repo.create(name=name, variety=variety)


class IrrigationService:
    def __init__(self, repo: IrrigationEventRepo) -> None:
        self._repo = repo

    def manual(
        self, *, water: bool, reason: str, plant_id: int | None = None
    ) -> IrrigationEvent:
        return self._repo.create(
            water=water, reason=reason, source="manual", plant_id=plant_id
        )


class SystemService:
    @staticmethod
    def status(*, database_url: str) -> "StatusDTO":
        mode = os.environ.get("DEVELOPMENT_MODE", "SIMULATION")
        dialect = "sqlite" if database_url.startswith("sqlite") else "postgres"
        return StatusDTO(status="ok", database=dialect, mode=mode)


class StatusDTO:
    def __init__(self, status: str, database: str, mode: str) -> None:
        self.status = status
        self.database = database
        self.mode = mode
