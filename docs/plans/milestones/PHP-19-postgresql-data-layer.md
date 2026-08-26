# PHP-19 — PostgreSQL Data Layer

## Goal

Persist plants, readings, irrigation events, predictions, and model registry via SQLAlchemy repositories (ADR-0004).

## Acceptance

- [x] Models + migrate upgrade/downgrade
- [x] Seed script
- [x] Repository CRUD for plants / readings / irrigation events / models
- [x] SQLite for tests; `DATABASE_URL` for PostgreSQL

```bash
cd backend
export PYTHONPATH=.
export DATABASE_URL=sqlite+pysqlite:///./phs.db
python -m app.db.migrate upgrade
python -m app.db.seed
```
