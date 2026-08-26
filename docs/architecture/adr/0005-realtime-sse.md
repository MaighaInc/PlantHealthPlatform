# ADR 0005 — Real-Time Transport: SSE

**Status:** Accepted  
**Date:** 2026-08-26  
**Supersedes:** —

## Context

PHP-22 needs dashboard updates without full page reload for status / irrigation / alerts.

## Decision

Use **Server-Sent Events (SSE)** from FastAPI (`GET /api/stream/events`) for unidirectional server→browser updates. Keep REST for commands. Polling remains a documented fallback.

## Alternatives Considered

| Option | Notes |
|--------|-------|
| Polling | Simple; higher latency/load |
| WebSocket | Bi-directional; more complexity than needed for dashboards |
| ROS bridge in browser | Wrong tier; ROS stays on edge |

## Consequences

- Frontend EventSource on `/api/stream/events`
- Auth for streams deferred to PHP-27

## References

- [FRONTEND.md](../../design/FRONTEND.md)
- PHP-21 dashboard
