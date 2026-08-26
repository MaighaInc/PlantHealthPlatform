# Architecture Decision Records (ADRs)

> Formal record of significant architecture and technology choices for PlantHealthPlatform

**Format:** Context → Decision → Consequences → References  
**Status values:** Proposed · Accepted · Superseded · Deprecated  
**Rule:** Changes to accepted ADRs require a new ADR that supersedes the prior record.

---

## Index

| ADR | Title | Status | Date |
|-----|-------|--------|------|
| [0001](./0001-ros2-distro-humble.md) | ROS 2 Distro: Humble Hawksbill | Accepted | 2026-08-25 |
| [0002](./0002-classical-before-feature-mlp-onnx.md) | Classical ML before feature MLP + ONNX | Accepted | 2026-08-25 |
| [0003](./0003-irrigation-intent-topic.md) | Irrigation intent topic separate from command | Accepted | 2026-08-25 |
| [0004](./0004-backend-fastapi-sqlalchemy.md) | Backend: FastAPI + SQLAlchemy + PostgreSQL | Accepted | 2026-08-26 |
| [0005](./0005-realtime-sse.md) | Real-time transport: SSE | Accepted | 2026-08-26 |
| [0006](./0006-ros-on-host-docker-server.md) | ROS on host; Docker for server tier | Accepted | 2026-08-26 |

---

## When to Write an ADR

Create a new ADR when a decision:

- Affects multiple packages, milestones, or subsystems
- Is hard to reverse (schema, auth, ROS topic architecture, ML pipeline)
- Was debated and needs a permanent record
- Deviates from the [Master Prompt](../prompt/MASTER_PROMPT.md)

**Do not** ADR routine implementation details covered by [CODING_STANDARDS.md](../development/CODING_STANDARDS.md).

## Expected Early ADRs

Candidates as the platform grows:

- ~~ROS 2 distro selection (Humble vs Iron)~~ → ADR-0001
- ~~Classical ML before feature MLP / ONNX~~ → ADR-0002
- ~~Irrigation intent vs command topics~~ → ADR-0003
- Backend stack choice (FastAPI vs Node/TS)
- HSV segmentation vs deep-learning segmentation
- Image CNN justification (deferred until labeled image volume)
- Real-time mechanism (polling vs WebSocket vs SSE)
- Docker scope (what runs containerized vs on host)

---

## Template

```markdown
# ADR NNNN — Title

**Status:** Proposed | Accepted | Superseded | Deprecated  
**Date:** YYYY-MM-DD  
**Supersedes:** ADR-XXXX (if applicable)

## Context

What is the issue or forcing function?

## Decision

What was decided?

## Alternatives Considered

What else was evaluated?

## Tradeoffs

Pros and cons of the chosen approach.

## Consequences

What becomes easier or harder? What must change?

## References

Links to docs, issues, or milestone plans.
```

Save as `docs/architecture/adr/NNNN-short-title.md` and update this index.
