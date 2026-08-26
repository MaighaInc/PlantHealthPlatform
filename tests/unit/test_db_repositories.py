"""Repository CRUD tests (PHP-19) — SQLite in-memory."""

from __future__ import annotations

import sys
from pathlib import Path

_BACKEND = Path(__file__).resolve().parents[2] / "backend"
sys.path.insert(0, str(_BACKEND))

from app.db.migrate import downgrade, upgrade  # noqa: E402
from app.db.session import make_engine, make_session_factory  # noqa: E402
from app.repositories import (  # noqa: E402
    IrrigationEventRepo,
    MlModelRepo,
    PlantRepo,
    SensorReadingRepo,
)


def test_migrate_and_plant_crud(tmp_path) -> None:
    url = f"sqlite+pysqlite:///{tmp_path / 't.db'}"
    upgrade(url)
    engine = make_engine(url)
    factory = make_session_factory(engine)
    with factory() as session:
        plant = PlantRepo(session).create(name="p1", variety="v")
        SensorReadingRepo(session).create(
            plant_id=plant.id, kind="temperature", value=22.5, unit="C"
        )
        IrrigationEventRepo(session).create(water=True, reason="test", plant_id=plant.id)
        MlModelRepo(session).upsert(
            name="m", version="1.0.0", format="joblib", artifact="m.joblib"
        )
        session.commit()
        assert PlantRepo(session).get(plant.id) is not None
        assert len(PlantRepo(session).list()) == 1
        assert len(SensorReadingRepo(session).list_for_plant(plant.id)) == 1
        assert len(IrrigationEventRepo(session).list()) == 1
        assert len(MlModelRepo(session).list()) == 1
    downgrade(url)
