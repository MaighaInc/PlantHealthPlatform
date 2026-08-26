# PHP-22 — Real-Time Monitoring

## Goal

Dashboard updates without full reload via SSE (ADR-0005).

## Acceptance

- [x] ADR comparing polling / WebSocket / SSE / ROS bridge
- [x] `GET /api/stream/events` SSE heartbeat
- [x] Dashboard EventSource shows live sequence
