"""Unit tests for development mode / .env helpers."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

_SHARED = Path(__file__).resolve().parents[2] / "shared"
sys.path.insert(0, str(_SHARED))

from plant_health_common import (  # noqa: E402
    ConfigError,
    DevelopmentMode,
    load_dotenv_file,
    parse_development_mode,
)


def test_parse_development_mode_default() -> None:
    assert parse_development_mode(None) == DevelopmentMode.SIMULATION
    assert parse_development_mode("") == DevelopmentMode.SIMULATION


def test_parse_development_mode_valid() -> None:
    assert parse_development_mode("hardware") == DevelopmentMode.HARDWARE
    assert parse_development_mode("PRODUCTION") == DevelopmentMode.PRODUCTION


def test_parse_development_mode_invalid() -> None:
    with pytest.raises(ConfigError, match="DEVELOPMENT_MODE"):
        parse_development_mode("STAGING")


def test_load_dotenv_file(tmp_path: Path) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text(
        "# comment\nDEVELOPMENT_MODE=DEVELOPMENT\nLOG_LEVEL=DEBUG\n",
        encoding="utf-8",
    )
    loaded = load_dotenv_file(env_file)
    assert loaded["DEVELOPMENT_MODE"] == "DEVELOPMENT"
    assert loaded["LOG_LEVEL"] == "DEBUG"


def test_load_dotenv_rejects_bad_line(tmp_path: Path) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text("NOT_A_PAIR\n", encoding="utf-8")
    with pytest.raises(ConfigError, match="invalid .env"):
        load_dotenv_file(env_file)


def test_env_mode_round_trip(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DEVELOPMENT_MODE", "SIMULATION")
    assert os.environ["DEVELOPMENT_MODE"] == "SIMULATION"
    assert parse_development_mode(os.environ["DEVELOPMENT_MODE"]) == DevelopmentMode.SIMULATION
