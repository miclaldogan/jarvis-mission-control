# Contributing to Jarvis Mission Control

Thanks for your interest in contributing! This document outlines the workflow and standards for this project.

## Development Workflow

### Branch Strategy
- `main` → stable releases only (protected)
- `dev` → active development (default target for PRs)
- Feature branches: `feature/<short-name>` or `fix/<short-name>` off `dev`

### Pull Request Process

1. **Fork & Branch**
   ```bash
   git checkout dev
   git pull origin dev
   git checkout -b feature/your-feature-name
   ```

2. **Make Changes**
   - Follow existing code style (see below)
   - Add tests for new features
   - Update documentation (`docs/api_contract.md`, `README.md`, etc.)

3. **Test Locally**
   ```bash
   # Backend tests
   docker compose run --rm backend pytest -q
   
   # Demo script (cache proof)
   bash infra/scripts/demo.sh
   ```

4. **Commit & Push**
   - Use clear commit messages: `feat(backend): add mission cache`, `fix(docs): correct endpoint path`
   - Push to your fork/branch

5. **Open PR**
   - Target: `dev` branch
   - Fill out the PR template completely
   - Link the related issue: `Closes #123`
   - Add labels: `backend`, `frontend`, `docs`, `infra`, `p1`/`p2`/`p3`

6. **Review & Merge**
   - At least 1 approval required
   - CI must be green (`backend-tests` + `docker-build`)
   - Maintainer will squash-merge into `dev`

## Code Standards

### Backend (Python/FastAPI)
- **Style**: Follow PEP 8, use type hints
- **Response envelope**: All endpoints MUST use `ok()` / `err()` helpers from `app.http_envelope`
- **Error codes**: Uppercase (`INVALID_PARAMS`, `RATE_LIMITED`, `UPSTREAM_FAILED`, `INTERNAL`)
- **Cache proof headers**: `X-Cache`, `X-Compute-Time-ms`, `X-Cache-Key` (when applicable)
- **Testing**: Every new endpoint needs at least one test in `backend/tests/`

### API Contract
- **Single source of truth**: `docs/api_contract.md`
- All endpoints, error codes, and response schemas MUST be documented there first
- Breaking changes require discussion in an issue before PR

### Docs
- Keep `README.md` quick-reference focused (curl examples, deployment steps)
- Detailed specs go in `docs/` (architecture, API contract, external sources)
- Update `docs/demo_steps.md` if demo flow changes

### Git Hygiene
- No generated files (logs, `__pycache__`, `.venv`, `.env`)
- Keep PRs focused (single feature/fix per PR when possible)
- Rebase on `dev` before opening PR if conflicts arise

## Issue Guidelines

### Creating Issues
Use the provided templates:
- **Bug**: Include steps to reproduce, environment, expected vs actual behavior
- **Feature**: Clear goal, acceptance criteria, sprint priority (P1/P2/P3/P4)

### Sprint Issues (Team Workflow)
All sprint work issues MUST include:
- **Done Checklist**: Concrete deliverables (code, tests, docs, CI green)
- **Proof**: PR link, CI run, demo output, or screenshot
- **Priority**: `P1` (critical) → `P4` (low)

Example:
```markdown
## Done Checklist
- [ ] Endpoint implemented in `backend/app/api/v1/endpoints/`
- [ ] Tests added to `backend/tests/`
- [ ] API contract updated (`docs/api_contract.md`)
- [ ] CI green

## Proof
- [ ] PR link
- [ ] CI run link (backend-tests + docker-build green)
- [ ] Demo proof (`curl` output or screenshot)
```

## Questions or Help?
- Open a discussion in Issues
- Tag maintainers: `@miclaldogan`, `@mervecaloglu`, `@burcuyldrm`

## Code of Conduct
By participating, you agree to abide by the [Code of Conduct](CODE_OF_CONDUCT.md).
