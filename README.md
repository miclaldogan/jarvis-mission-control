# jarvis-mission-control

Mission Control: context ingest → mission generation → daily missions → reports.
Built for a 4-person team workflow (issues/PR/review discipline).
Target architecture: FastAPI backend + Redis cache + responsive frontend.
Deploy target: Docker Compose behind Nginx + optional SSL.

## What exists today (Sprint 2 scope)
- Backend (FastAPI) with a stable response envelope (`ok/data/meta/error`).
- `GET /api/v1/health` → liveness + version.
- `GET /api/v1/context` → aggregated context snapshot (weather, github, news) with cache proof headers.
- `GET /api/v1/synthetic/tasks` → cache proof endpoint (`seed` enables caching).
- `POST /api/v1/missions/generate` → mission generation from context.
- `GET /api/v1/reports/mission-load` → cached heavy-compute report.
- `GET /api/v1/report` → demo-friendly report with context + missions.
- Rate limiting on synthetic (429 with `Retry-After`).
- Cache proof headers: `X-Cache`, `X-Compute-Time-ms`, `X-Cache-Key`.

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

## Metrics (Prometheus)
The backend exposes `GET /metrics` in Prometheus text format.

```bash
curl -s http://localhost:8000/metrics | head
curl -s http://localhost:8000/metrics | grep -E 'cache_hits_total|cache_misses_total'
```

## API quick reference
All endpoints are under `/api/v1` and use the same response envelope.

| Endpoint | Method | Description | Cache |
|----------|--------|-------------|-------|
| `/health` | GET | Liveness + version | No |
| `/context` | GET | Aggregated context (weather/github/news) | Yes (short TTL) |
| `/synthetic/tasks` | GET | Cache proof endpoint (`?n=100000&seed=42`) | Yes (when seed provided) |
| `/missions/generate` | POST | Generate missions from context | No |
| `/reports/mission-load` | GET | Heavy-compute report (`?window=7d&bucket=day&seed=42`) | Yes (when seed provided) |
| `/report` | GET | Demo-friendly report with context + missions | No |

### curl examples

```bash
# Health check
curl -s http://localhost:8000/api/v1/health | jq .

# Context snapshot
curl -s http://localhost:8000/api/v1/context | jq '.data | keys'

# Synthetic tasks (cache proof)
curl -sD - http://localhost:8000/api/v1/synthetic/tasks?n=100000\&seed=42 -o /dev/null | grep -i x-cache

# Mission-load report (cache proof)
curl -sD - 'http://localhost:8000/api/v1/reports/mission-load?window=7d&bucket=day&seed=42' -o /dev/null | grep -i x-cache

# Prometheus metrics
curl -s http://localhost:8000/metrics | grep cache_hits
```

## Configuration
Backend environment variables:
- `APP_VERSION` (default: `0.1.0`)
- `REDIS_URL` (default: `redis://redis:6379/0` for Compose)
- `CACHE_TTL_SECONDS` (default: `120`)
- `SYNTHETIC_RATELIMIT_PER_MIN` (default: `30`)
- `SYNTHETIC_RATELIMIT_WINDOW_SECONDS` (default: `60`)
- `CORS_ALLOWED_ORIGINS` (default: `http://localhost:3000,http://127.0.0.1:3000`)
- `CORS_ALLOW_CREDENTIALS` (default: `false`)

Quick check (rate limit):

```bash
export SYNTHETIC_RATELIMIT_PER_MIN=2
export SYNTHETIC_RATELIMIT_WINDOW_SECONDS=60

for i in 1 2 3; do
	echo "--- $i"
	curl -s -D - -o /dev/null \
		-H 'X-Forwarded-For: 1.2.3.4' \
		'http://localhost:8000/api/v1/synthetic/tasks?n=100000&seed=42' \
		| awk 'NR==1{print "status=" $2} /^Retry-After:/{gsub("\r","",$2); print "retry_after=" $2}'
done
```

Backend also sets baseline security headers on responses:
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `Referrer-Policy: no-referrer`
- `Permissions-Policy: geolocation=(), microphone=(), camera=()`

Example file: `backend/.env.example`

## Development workflow
- Branch naming: `feature/<short-name>` off `dev`.
- Open PR to `dev`, get at least 1 approval.
- Merge to `main` only for stable milestones.

## Troubleshooting
- If `docker compose` is missing:
	- On Mint/Ubuntu, `sudo apt install -y docker-compose-v2` typically provides it.
	- Some setups use `docker-compose-plugin` or legacy `docker-compose`.
	- Or use the manual run steps above.
- If backend can’t reach Redis in manual mode: ensure `REDIS_URL=redis://localhost:6379/0`.


