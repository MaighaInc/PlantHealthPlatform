"""Seed script for local/dev DB (PHP-19)."""

from __future__ import annotations

from app.db.session import init_db, make_engine, make_session_factory
from app.repositories import IrrigationEventRepo, MlModelRepo, PlantRepo, SensorReadingRepo


def seed(url: str | None = None) -> None:
    engine = make_engine(url)
    init_db(engine)
    factory = make_session_factory(engine)
    with factory() as session:
        plants = PlantRepo(session)
        plant = plants.create(name="demo-basil", variety="genovese")
        SensorReadingRepo(session).create(
            plant_id=plant.id, kind="soil_moisture", value=42.0, unit="%"
        )
        IrrigationEventRepo(session).create(
            plant_id=plant.id, water=False, reason="seed", source="seed"
        )
        MlModelRepo(session).upsert(
            name="plant-health-classifier",
            version="1.0.0",
            format="joblib",
            artifact="plant-health-classifier-1.0.0.joblib",
        )
        session.commit()
        print(f"seeded plant id={plant.id}")


if __name__ == "__main__":
    seed()
