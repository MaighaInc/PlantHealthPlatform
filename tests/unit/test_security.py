"""Security tests (PHP-27)."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

_BACKEND = Path(__file__).resolve().parents[2] / "backend"
sys.path.insert(0, str(_BACKEND))

from app.security import AuthError, require_actuator_auth  # noqa: E402


def test_production_rejects_missing_token(monkeypatch) -> None:
    monkeypatch.setenv("DEVELOPMENT_MODE", "PRODUCTION")
    monkeypatch.setenv("PHS_API_TOKEN", "secret")
    with pytest.raises(AuthError):
        require_actuator_auth(authorization_header=None, development_mode="PRODUCTION")


def test_production_accepts_valid_bearer(monkeypatch) -> None:
    monkeypatch.setenv("PHS_API_TOKEN", "secret")
    require_actuator_auth(
        authorization_header="Bearer secret", development_mode="PRODUCTION"
    )


def test_simulation_allows_without_token(monkeypatch) -> None:
    monkeypatch.delenv("PHS_API_TOKEN", raising=False)
    require_actuator_auth(authorization_header=None, development_mode="SIMULATION")
