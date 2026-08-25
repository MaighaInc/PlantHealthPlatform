# Coding Standards

> Git, dependencies, error handling, and code quality for PlantHealthPlatform

## Git

Branch naming:

```text
feature/php-01-ros-foundation
feature/php-06-opencv
```

Commit messages (meaningful):

```text
feat(sensor): add configurable virtual soil sensor
test(cv): add leaf segmentation tests
fix(irrigation): enforce maximum watering duration
feat(ml): add baseline health classifier
```

Avoid: `stuff`, `changes`, `final`, `fix`, `test`, `asdf`

## Scope Discipline

When implementing a milestone:

- Do not refactor unrelated modules
- Do not rename unrelated files
- Do not upgrade dependencies without justification
- Do not rewrite working systems unnecessarily
- Do not introduce frameworks without justification
- Do not change APIs without considering consumers

## Dependency Discipline

Before adding a dependency, document:

```text
Package:
Purpose:
Why it is needed:
Why existing dependencies cannot solve it:
Maintenance implications:
Security implications:
```

## Error Handling

Never:

```python
except Exception:
    pass
```

Every exception must be handled, logged, transformed, or propagated with diagnostic context.

## Logging

Use structured meaningful logs — ROS nodes use ROS logging.

```text
INFO  Camera initialized
INFO  Model loaded version=1.2.0
WARN  Soil sensor returned invalid value
ERROR Camera frame acquisition failed
```

Avoid scattered `print()` in production code.

## Python Tooling

- Python 3.10+
- pytest, mypy, Ruff, Black
- Pydantic for validation

## Frontend

- TypeScript strict where possible
- Avoid `any` unless justified
- Explicit API contract types

## Engineering Decisions

For meaningful decisions, document in ADRs:

```text
Decision / Context / Why / Alternatives / Tradeoffs / Consequences
```

## Educational Requirement

After each milestone, the intern should explain: what was built, why, integration, alternatives, failure modes, testing, deployment, and improvements.

## Related Docs

- [AGENT_WORKFLOW.md](./AGENT_WORKFLOW.md)
- [../architecture/adr/README.md](../architecture/adr/README.md)
