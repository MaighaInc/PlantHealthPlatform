# REST API Design

> Backend HTTP surface for Plant Health System

## Layering

```text
API / Controller
        ↓
Service
        ↓
Repository
        ↓
Database
```

## Planned Endpoints

```text
GET    /api/plants
GET    /api/plants/{id}

GET    /api/sensors
GET    /api/sensors/{id}/readings

GET    /api/plants/{id}/health

GET    /api/plants/{id}/images

GET    /api/irrigation/events

POST   /api/irrigation/manual

GET    /api/models

GET    /api/system/status
```

## Requirements

- Request validation (Pydantic or equivalent)
- Meaningful HTTP status codes
- Structured error handling
- Pagination and filtering
- Timestamps on all time-series responses
- Authentication and authorization architecture (PHP-27)

## Backend Stack Options

**Preferred (ML-oriented):** FastAPI, Pydantic, SQLAlchemy, PostgreSQL

**Alternative (TS integration):** Node.js, TypeScript, Express/Fastify, Prisma, PostgreSQL

Choose based on architectural fit — not popularity alone.

## Related Docs

- [DATABASE.md](./DATABASE.md)
- [FRONTEND.md](./FRONTEND.md)
- [../development/SECURITY.md](../development/SECURITY.md)
- [../plans/ROADMAP.md](../plans/ROADMAP.md) — PHP-20
