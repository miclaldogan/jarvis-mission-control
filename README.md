# jarvis-mission-control

Mission Control: context ingest → mission generation → daily missions → reports.
Built for a 4-person team workflow (issues/PR/review discipline).
Target architecture: FastAPI backend + Redis cache + responsive frontend.
Deploy target: Docker Compose behind Nginx + optional SSL.

## What exists today (Sprint 1 scope)
- Backend (FastAPI) with a stable response envelope (`ok/data/meta/error`).
- `GET /api/v1/health` working.
- `GET /api/v1/synthetic/tasks` supports `n=100000|1000000` and optional `seed`.
	- Caching is **enabled only when `seed` is provided**.
	- Payload stays small: returns `sample` + `preview_hash` + `meta.total` (not 100k/1M items).
	- Cache proof headers: `X-Cache`, `X-Compute-Time-ms` (and `X-Cache-Key` as extra proof).
- `GET /api/v1/report` exists as a demo-friendly placeholder (not cached in sprint 1).

## Team workflow rules
- No direct pushes to `main` (release/stable). PR required.
- Daily work happens on `dev` via feature branches.
- PR target: `dev`. At least 1 approval.

## Repository structure
- `backend/`: FastAPI app + Dockerfile
- `frontend/`: placeholder (Dockerfile only for now)
- `infra/nginx/`: nginx notes for future deployment
- `infra/scripts/demo.sh`: instructor-friendly demo (health + cache proof)
- `docs/`: architecture + API contract + demo steps

## Docs
- API contract (most critical): `docs/api_contract.md`
- Architecture (1-page): `docs/architecture.md`
- Demo steps: `docs/demo_steps.md`

## Local run

### Option A: Docker Compose (recommended)
If you have Docker Compose available:

```bash
docker compose up --build
```

API will be at `http://localhost:8000`.

### Option B: No Compose plugin (manual run)
Some Linux setups have `docker` but not the `docker compose` plugin.

1) Start Redis:
```bash
docker run --rm -p 6379:6379 --name jarvis-redis redis:7
```

2) Run the backend:
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

export REDIS_URL="redis://localhost:6379/0"
export CACHE_TTL_SECONDS="120"
export APP_VERSION="0.1.0"

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Demo (cache proof)
Run the automated demo script:

```bash
bash infra/scripts/demo.sh
```

Expected:
- First `synthetic/tasks` call: `X-Cache: MISS`
- Second call (same params): `X-Cache: HIT`
- Different `seed`: `MISS`

You can also point the script to another base URL:

```bash
API_BASE_URL="http://localhost:8000" bash infra/scripts/demo.sh
```

## API quick reference
All endpoints are under `/api/v1` and use the same response envelope.

- `GET /health` → liveness + version
- `GET /context` → placeholder (404 until ingestion implemented)
- `GET /synthetic/tasks?n=100000|1000000&seed=42` → cache proof endpoint (seed enables caching)
- `GET /report?window=30d&bucket=hour` → demo-friendly report response

## Configuration
Backend environment variables:
- `APP_VERSION` (default: `0.1.0`)
- `REDIS_URL` (default: `redis://redis:6379/0` for Compose)
- `CACHE_TTL_SECONDS` (default: `120`)

Example file: `backend/.env.example`

## Development workflow
- Branch naming: `feature/<short-name>` off `dev`.
- Open PR to `dev`, get at least 1 approval.
- Merge to `main` only for stable milestones.

## Troubleshooting
- If `docker compose` is missing: install the Docker Compose plugin (`docker-compose-plugin`) or use the manual run steps above.
- If backend can’t reach Redis in manual mode: ensure `REDIS_URL=redis://localhost:6379/0`.
