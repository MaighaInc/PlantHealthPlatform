# Agent Workflow

> 10-step workflow for every implementation task on PlantHealthPlatform

---

## STEP 1 — UNDERSTAND

Restate the requirement. Identify:

- Milestone (e.g. PHP-06)
- Existing functionality
- New capability
- Acceptance criteria

---

## STEP 2 — INSPECT

Inspect the existing repository **before** making changes.

Never assume files, APIs, packages, dependencies, topics, or schema exist.

---

## STEP 3 — ARCHITECT

Explain:

```text
Current Architecture
        ↓
New Capability
        ↓
Integration Points
        ↓
Data Flow
```

---

## STEP 4 — PLAN

Provide:

```text
Files to create
Files to modify
Dependencies
Interfaces
Tests
Documentation
```

---

## STEP 5 — IMPLEMENT

Implement the smallest useful increment. Avoid unnecessary refactoring.

---

## STEP 6 — TEST

Run relevant:

- Unit tests
- Integration tests
- Linting
- Type checks
- Build checks
- ROS checks

---

## STEP 7 — DIAGNOSE

If something fails:

1. Identify root cause
2. Explain the cause
3. Make the smallest appropriate fix
4. Rerun tests
5. Verify regression behavior

Do not blindly retry commands.

---

## STEP 8 — REVIEW

Pull-request-style review covering:

- Correctness, architecture, testing, security, performance
- Error handling, maintainability, ROS/ML conventions
- Resource management, technical debt

Explain what is wrong and why — do not auto-rewrite everything.

---

## STEP 9 — DOCUMENT

Update:

- README
- Relevant design docs
- ADRs for significant decisions
- Milestone plan under `docs/plans/milestones/`

---

## STEP 10 — SUMMARIZE

Report:

```text
Implemented
Tests
Files changed
Architecture impact
Known limitations
Technical debt
Next milestone
```

---

## Standard Response Format

For development tasks, use these sections:

| Section | Content |
|---------|---------|
| **Understanding** | Requirement restatement |
| **Existing Architecture** | What exists today |
| **Proposed Change** | Integration approach |
| **Plan** | Implementation steps |
| **Files** | Create/modify list |
| **Implementation** | Code changes |
| **Tests** | What was run |
| **Review** | Bugs, risks, debt |
| **Intern Task** | What the intern should implement (if educational) |
| **Acceptance Criteria** | Objective completion checks |
| **Next Step** | Next logical milestone |

---

## Progressive Assistance (Educational Tasks)

| Level | Action |
|-------|--------|
| 1 — Concept | Explain what needs to happen |
| 2 — Architecture | Components and interfaces |
| 3 — Skeleton | Interfaces and minimal scaffolding |
| 4 — Hint | Algorithmic guidance |
| 5 — Partial | Difficult portions only |
| 6 — Reference | Full solution only when justified |

## Related Docs

- [MILESTONE_COMPLETION.md](./MILESTONE_COMPLETION.md)
- [CODING_STANDARDS.md](./CODING_STANDARDS.md)
- [../prompt/MASTER_PROMPT.md](../prompt/MASTER_PROMPT.md)
