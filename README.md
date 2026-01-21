# jarvis-mission-control

Mission Control: context ingest → mission generation → daily missions → reports.
Built for a 4-person team workflow (issues/PR/review discipline).
Target architecture: FastAPI backend + Redis cache + responsive frontend.
Deploy target: Docker Compose behind Nginx + optional SSL.

## Team workflow rules
- No direct pushes to `main` (release/stable). PR required.
- Daily work happens on `dev` via feature branches.
- PR target: `dev`. At least 1 approval.

## Docs
- API contract (most critical): `docs/api_contract.md`
- Architecture (1-page): `docs/architecture.md`
- Demo steps: `docs/demo_steps.md`

## Local run (placeholder)
- `docker compose up --build`
