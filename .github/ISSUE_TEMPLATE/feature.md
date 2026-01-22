---
name: Feature Request
about: Propose a new feature or enhancement
labels: [feature]
---

## Goal
<!-- What problem does this feature solve? Why is it needed? -->

## Acceptance criteria
- [ ] <!-- Concrete deliverable 1 -->
- [ ] <!-- Concrete deliverable 2 -->
- [ ] <!-- Tests added/updated -->
- [ ] <!-- Docs updated (API contract, README, etc.) -->
- [ ] <!-- CI green -->

## Proposed solution
<!-- How would you implement this? (optional, but helpful) -->

## Alternatives considered
<!-- Any other approaches you thought about? -->

## Priority
<!-- P1 (critical), P2 (high), P3 (medium), P4 (low) -->
- Priority: **P?**

## Notes
<!-- Additional context, links, references, etc. -->

---

## Done Checklist
<!-- For team workflow: fill this during sprint planning or implementation -->
- [ ] <!-- Specific implementation task 1 -->
- [ ] <!-- Specific implementation task 2 -->
- [ ] CI green

## Integration Checklist
<!-- ⚠️ CRITICAL: Check compatibility with existing codebase -->
- [ ] No conflicts with existing cache layer (we use async Redis, not sync in-memory)
- [ ] No import path conflicts (check `app/` module structure)
- [ ] New dependencies added to `requirements.txt` (if any)
- [ ] Existing tests still pass (`pytest -q` before PR)
- [ ] Code style matches existing patterns (async/await, type hints, error handling)
- [ ] Environment variables documented in README (if new ones added)

## Proof
<!-- For team workflow: fill after PR is merged -->
- [ ] PR link
- [ ] CI run link (backend-tests + docker-build green)
- [ ] Demo proof (curl output, screenshot, or demo.sh run)
