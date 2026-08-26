"""Auth helpers for actuator endpoints (PHP-27)."""

from __future__ import annotations

import os


class AuthError(PermissionError):
    pass


def require_actuator_auth(
    *,
    authorization_header: str | None,
    development_mode: str | None = None,
) -> None:
    """
    PRODUCTION requires ``Authorization: Bearer <PHS_API_TOKEN>``.
    SIMULATION/DEVELOPMENT/HARDWARE may skip if token unset.
    """
    mode = (development_mode or os.environ.get("DEVELOPMENT_MODE", "SIMULATION")).upper()
    token = os.environ.get("PHS_API_TOKEN", "")
    if mode != "PRODUCTION":
        return
    if not token:
        raise AuthError("PHS_API_TOKEN must be set in PRODUCTION")
    if not authorization_header or not authorization_header.startswith("Bearer "):
        raise AuthError("missing bearer token")
    provided = authorization_header.removeprefix("Bearer ").strip()
    if provided != token:
        raise AuthError("invalid token")
