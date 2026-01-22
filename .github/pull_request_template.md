## Summary

## Issue link
- Fixes/Implements: #

## Evidence (screenshots / curl output)
- UI: screenshots
- API: paste `curl -i ...` output (headers + first JSON line)

## How to test
- Command(s):
- Expected output:

## Checklist (author)
- [ ] Issue linked
- [ ] Clear description
- [ ] Tests run (commands listed above)
- [ ] Breaking change noted (if any)

## Review checklist (fast but solid)

### 0) 30-second preflight
- [ ] Base branch is **dev** (not `main`)
- [ ] Title is clear (e.g., `P1: ...`) and references the issue
- [ ] Changed files match the scope (backend vs docs vs infra)
- [ ] PR is not “too big” (too many unrelated changes)

Quick CLI:

```bash
export GH_REPO=miclaldogan/jarvis-mission-control
gh pr view -R "$GH_REPO" <PR_NO> \
  --json title,baseRefName,headRefName,changedFiles,additions,deletions \
  --jq '{title,base:.baseRefName,head:.headRefName,changedFiles,additions,deletions}'
```

### 1) API contract alignment (most important)
- [ ] Endpoints match docs/api_contract.md exactly
  - Current v1:
    - `GET /api/v1/health`
    - `GET /api/v1/context`
    - `GET /api/v1/synthetic/tasks`
    - `GET /api/v1/report`
- [ ] Response envelope is consistent: `ok/data/meta/error`
- [ ] Field names match the docs (avoid drift like `temp` vs `temp_c` unless mapped)
- [ ] If a new endpoint/field is introduced: docs updated (api_contract + demo_steps)
- [ ] If it’s future work (P2+): clearly labeled as “not in v1”

Red flags:
- [ ] No “v1-looking” endpoints that aren’t in the contract (e.g., `/context/ingest`)

### 2) Cache proof (synthetic/tasks)
- [ ] Cache applies only to `GET /api/v1/synthetic/tasks` (for this sprint)
- [ ] Same params → 2nd call is **HIT**
- [ ] Headers present:
  - [ ] `X-Cache: MISS/HIT`
  - [ ] `X-Compute-Time-ms`
  - [ ] (optional) `X-Cache-Key`
- [ ] Different seed → **MISS** again

Quick test:

```bash
API=http://127.0.0.1:8000
curl -is "$API/api/v1/synthetic/tasks?n=100000&seed=42" | sed -n '1,30p'
curl -is "$API/api/v1/synthetic/tasks?n=100000&seed=42" | sed -n '1,30p'
curl -is "$API/api/v1/synthetic/tasks?n=100000&seed=43" | sed -n '1,30p'
```

### 3) CI / tests
- [ ] PR checks are green:
  - [ ] `backend-tests`
  - [ ] `docker-build`
- [ ] If tests changed/added: `pytest -q` passes locally
- [ ] Redis config is correct (e.g., `REDIS_URL` expectations match CI/compose)

CLI:

```bash
export GH_REPO=miclaldogan/jarvis-mission-control
gh pr checks -R "$GH_REPO" <PR_NO>
```

### 4) Docker / compose (demo safety)
- [ ] `docker compose up -d --build` works
- [ ] `curl /api/v1/health` returns 200
- [ ] infra/scripts/demo.sh still prints MISS → HIT
- [ ] If compose changed: no port conflicts; env vars match README (and `.env.example` if added)

### 5) Git hygiene
- [ ] Only relevant changes are included (no unrelated refactors)
- [ ] No generated artifacts (logs, caches, venv, __pycache__, etc.)
- [ ] If refactor is large: rationale is explained and scope is reasonable

### 6) Merge decision
- Default: **Squash merge** when single-topic + checks green + contract aligned + demo safe
- Changes requested when: contract drift, demo/cache proof regression, wrong base branch, or CI is red

