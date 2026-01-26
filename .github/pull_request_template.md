## Summary
<!-- Brief description of what this PR does -->

## Issue link
- Fixes/Implements: #

## Changes
<!-- List main changes -->
- 
- 

## Evidence (screenshots / curl output)
<!-- For API changes: paste `curl -i ...` output showing headers -->
<!-- For UI changes: screenshots -->

## How to test
```bash
# Command(s):

# Expected output:

```

## Checklist
- [ ] Issue linked above
- [ ] Base branch is **dev** (not `main`)
- [ ] Tests run locally and pass
- [ ] Docs updated (if API/config changes)
- [ ] No unrelated changes included
- [ ] CI checks pass (backend-tests + docker-build)

---

## For Reviewers

### Quick preflight
- [ ] Base branch is `dev`
- [ ] Title references the issue (e.g., `feat(backend): add cache #50`)
- [ ] Changed files match scope (backend/docs/infra)
- [ ] PR is focused (not too many unrelated changes)

### API contract alignment
- [ ] Endpoints match `docs/api_contract.md`
- [ ] Response envelope: `ok/data/meta/error`
- [ ] Error codes are uppercase (`RATE_LIMITED`, `INVALID_PARAMS`, etc.)
- [ ] Cache proof headers present (when applicable): `X-Cache`, `X-Compute-Time-ms`

### Testing
- [ ] CI is green (`backend-tests` + `docker-build`)
- [ ] Local: `docker compose run --rm backend pytest -q` passes
- [ ] Demo: `bash infra/scripts/demo.sh` still works (if touching cached endpoints)

### Merge decision
**Squash merge** when:
- Single-topic + checks green + API contract aligned + demo safe

**Request changes** when:
- API contract drift, cache proof regression, wrong base branch, or CI is red
