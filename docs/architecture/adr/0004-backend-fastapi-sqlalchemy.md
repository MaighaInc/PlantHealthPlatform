# ADR 0004 — Backend Stack: FastAPI + SQLAlchemy + PostgreSQL

**Status:** Accepted  
**Date:** 2026-08-26  
**Supersedes:** —

## Context

PHP-19 requires a persistence layer and PHP-20 a REST API. Candidates: FastAPI+SQLAlchemy vs Node+Prisma.

## Decision

Use **Python FastAPI + SQLAlchemy 2.x + Alembic + PostgreSQL**, with SQLite allowed for unit tests via `DATABASE_URL`.

## Alternatives Considered

| Option | Notes |
|--------|-------|
| Node + Prisma | Strong TS frontend fit; splits ML/Python and API languages |
| Django ORM | Heavier than needed for thin API |

## Consequences

- `backend/` owns migrations and repositories
- ROS ingestion can POST or write via shared repository later
- OpenAPI comes free with FastAPI (PHP-20)

## References

- [API.md](../../design/API.md)
- [DATABASE.md](../../design/DATABASE.md)
