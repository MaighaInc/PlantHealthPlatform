# Observability

> Logging, metrics, health checks, and diagnostics

## Current Requirements

- Meaningful structured logs (ROS logging in nodes)
- Error messages with enough context to diagnose failures

## Progressive Additions (PHP-26)

| Capability | Description |
|------------|-------------|
| Health endpoints | API `/health`, component readiness |
| ROS diagnostics | `/diagnostics` topic, node status |
| Sensor freshness | Staleness detection and alerts |
| Inference latency | Per-prediction timing |
| API latency | Request duration tracking |
| Irrigation events | Audit trail for all actuation |
| Error counters | Rate of failures by component |

## Future Stack (evaluate incrementally)

```text
Prometheus
Grafana
Loki
Alertmanager
```

Introduce only when complexity is justified.

## Performance Tracking

Establish baselines before optimizing:

- Camera FPS, ROS message frequency
- CV and ML inference latency
- API and DB query time
- Memory, CPU, model size

## Related Docs

- [CODING_STANDARDS.md](./CODING_STANDARDS.md)
- [../plans/ROADMAP.md](../plans/ROADMAP.md) — PHP-26
