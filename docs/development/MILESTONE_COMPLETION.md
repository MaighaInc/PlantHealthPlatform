# Milestone Completion Criteria

> When a PHP milestone is considered done

## A milestone is NOT complete merely because the code runs.

## Required Checklist

- [ ] Implementation works as specified
- [ ] Existing functionality remains intact (regression verified)
- [ ] Tests exist for new behavior
- [ ] All relevant tests pass
- [ ] Documentation updated (README + relevant `docs/` pages)
- [ ] Configuration is reproducible (`.env.example`, ROS params documented)
- [ ] Errors are handled — no silent `except: pass`
- [ ] Architecture is understood by the intern
- [ ] Acceptance criteria for the milestone are satisfied
- [ ] Git changes are focused — no unrelated refactors
- [ ] No unnecessary dependencies introduced

## Regression Requirement

Because every milestone extends the same product:

```text
New Tests + Existing Tests + Integration Tests
```

must all be considered before sign-off.

If existing behavior intentionally changes:

1. Document the change
2. Update tests
3. Explain the architectural reason
4. Update documentation

## Educational Completion

The intern should be able to answer:

```text
What did I build?
Why did I build it?
How does it integrate?
What alternatives did I consider?
What can fail?
How did I test it?
How would I deploy it?
How would I improve it?
```

## Code Review

After every significant milestone, perform a PR-style review covering correctness, architecture, testing, security, and technical debt.

## Related Docs

- [AGENT_WORKFLOW.md](./AGENT_WORKFLOW.md)
- [TESTING.md](./TESTING.md)
- [../plans/ROADMAP.md](../plans/ROADMAP.md)
