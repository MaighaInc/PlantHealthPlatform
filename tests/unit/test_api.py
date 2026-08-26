"""API integration tests with TestClient + SQLite (PHP-20)."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

_BACKEND = Path(__file__).resolve().parents[2] / "backend"
sys.path.insert(0, str(_BACKEND))


@pytest.fixture()
def client(tmp_path, monkeypatch):
    db_path = tmp_path / "api.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite+pysqlite:///{db_path}")
    # Re-import app with fresh engine
    for mod in list(sys.modules):
        if mod.startswith("app."):
            del sys.modules[mod]
    from fastapi.testclient import TestClient
    from app.main import app

    return TestClient(app)


def test_system_status_and_plants(client) -> None:
    r = client.get("/api/system/status")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"

    created = client.post("/api/plants", json={"name": "basil", "variety": "genovese"})
    assert created.status_code == 201
    plant_id = created.json()["id"]

    listed = client.get("/api/plants")
    assert listed.status_code == 200
    assert any(p["id"] == plant_id for p in listed.json())

    one = client.get(f"/api/plants/{plant_id}")
    assert one.status_code == 200

    health = client.get(f"/api/plants/{plant_id}/health")
    assert health.status_code == 200
    assert health.json()["status"] == "unknown"

    irr = client.post(
        "/api/irrigation/manual",
        json={"water": False, "reason": "test", "plant_id": plant_id},
    )
    assert irr.status_code == 201
    events = client.get("/api/irrigation/events")
    assert events.status_code == 200
    assert len(events.json()) >= 1

    models = client.get("/api/models")
    assert models.status_code == 200
