# Frontend Dashboard Design

> React/TypeScript dashboard for Plant Health System

## Stack

- React + TypeScript + Vite
- TanStack Query or equivalent for server state
- Modular component architecture

## Structure

```text
components/
features/
hooks/
services/
pages/
types/
utils/
```

Avoid giant components. Avoid `any` unless justified. API contracts need explicit TypeScript types.

## Pages

### Dashboard (overview)

- Plant count, healthy/stressed counts
- Sensor status, irrigation status
- Latest alerts

### Plant Detail

- Latest image, health status/score
- ML prediction and confidence
- Soil moisture, temperature, humidity
- Historical charts

### Irrigation

- Relay state, irrigation events
- Manual controls, safety state

### ML

- Model version, inference statistics
- Prediction history, confidence distribution

## Real-Time Monitoring (PHP-22)

Evaluate tradeoffs before implementing:

- Polling
- WebSockets
- Server-Sent Events
- ROS bridge

## Related Docs

- [API.md](./API.md)
- [../plans/ROADMAP.md](../plans/ROADMAP.md) — PHP-21, PHP-22
