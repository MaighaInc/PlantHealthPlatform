"""Development mode and environment helpers (no third-party deps)."""

from __future__ import annotations

import os
from enum import Enum
from pathlib import Path


class DevelopmentMode(str, Enum):
    SIMULATION = "SIMULATION"
    DEVELOPMENT = "DEVELOPMENT"
    HARDWARE = "HARDWARE"
    PRODUCTION = "PRODUCTION"


class ConfigError(ValueError):
    """Invalid environment or file-based configuration."""


_VALID_MODES = {m.value for m in DevelopmentMode}


def parse_development_mode(raw: str | None, *, default: DevelopmentMode = DevelopmentMode.SIMULATION) -> DevelopmentMode:
    if raw is None or raw.strip() == "":
        return default
    value = raw.strip().upper()
    if value not in _VALID_MODES:
        raise ConfigError(
            f"DEVELOPMENT_MODE must be one of {sorted(_VALID_MODES)}, got {raw!r}"
        )
    return DevelopmentMode(value)


def load_dotenv_file(path: Path) -> dict[str, str]:
    """
    Load KEY=VALUE pairs from a .env file into a dict (does not mutate os.environ).

    Lines starting with # and blank lines are ignored. Values may be optionally quoted.
    """
    if not path.is_file():
        raise ConfigError(f".env file not found: {path}")

    result: dict[str, str] = {}
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if "=" not in stripped:
            raise ConfigError(f"invalid .env line {line_no}: {line!r}")
        key, value = stripped.split("=", 1)
        key = key.strip()
        value = value.strip()
        if (value.startswith('"') and value.endswith('"')) or (
            value.startswith("'") and value.endswith("'")
        ):
            value = value[1:-1]
        if not key:
            raise ConfigError(f"empty key on .env line {line_no}")
        result[key] = value
    return result


def apply_dotenv(path: Path, *, override: bool = False) -> dict[str, str]:
    """Load .env into os.environ. Existing keys kept unless override=True."""
    loaded = load_dotenv_file(path)
    for key, value in loaded.items():
        if override or key not in os.environ:
            os.environ[key] = value
    return loaded


def get_development_mode_from_env(
    *,
    default: DevelopmentMode = DevelopmentMode.SIMULATION,
) -> DevelopmentMode:
    return parse_development_mode(os.environ.get("DEVELOPMENT_MODE"), default=default)


def get_log_level_from_env(*, default: str = "INFO") -> str:
    raw = os.environ.get("LOG_LEVEL", default).strip().upper()
    allowed = {"DEBUG", "INFO", "WARN", "WARNING", "ERROR", "FATAL"}
    if raw not in allowed:
        raise ConfigError(f"LOG_LEVEL must be one of {sorted(allowed)}, got {raw!r}")
    return "WARN" if raw == "WARNING" else raw
