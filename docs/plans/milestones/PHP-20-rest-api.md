# PHP-20 — REST API

## Goal

Expose Plant Health System HTTP API with Controller → Service → Repository layering.

## Run

```bash
cd backend
export PYTHONPATH=.
export DATABASE_URL=sqlite+pysqlite:///./phs.db
uvicorn app.main:app --reload --port 8000
# OpenAPI: http://localhost:8000/docs
```

## Acceptance

- [x] Endpoints for plants, sensors readings, health, irrigation, models, status
- [x] Validation via Pydantic; 404s; pagination query params
- [x] Integration tests with TestClient
