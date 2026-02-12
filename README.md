# jarvis-mission-control - (IT'S JUST A DEMO AND NEEDS DEVELOPMENT)

**Mission Control:** Intelligent task management system with context ingestion → mission generation → daily prioritization → performance reports.

## 📚 Course Requirements Compliance

### ✅ 1. Özgün Konu
Jarvis Mission Control: Akıllı görev yönetim sistemi
- GitHub repo durumu, hava durumu, haber başlıkları gibi kaynaklardan context toplar
- Context'e göre öncelikli görevler üretir (P1/P2/P3/P4)
- "Why" açıklamasıyla her görevin gerekçesini gösterir
- Zaman serisi raporlarıyla görev yükünü analiz eder

### ✅ 2. FastAPI REST API
6 endpoint ile tam RESTful API:
- `GET /api/v1/health` → health check
- `GET /api/v1/context` → canlı context snapshot (weather, github, news)
- `POST /api/v1/missions/generate` → context'ten görev üretimi
- `GET /api/v1/synthetic/tasks` → **100k-1M sentetik task preview** (cache proof)
- `POST /api/v1/synthetic/tasks/persist` → **100k-1M sentetik task kalıcı kayıt** (SQLite)
- `GET /api/v1/reports/mission-load` → heavy compute report (cache proof)
- `GET /api/v1/report` → aggregated demo report

### ✅ 3. 100k-1M Sentetik Veri + Cache İspatı
`GET /api/v1/synthetic/tasks?n=1000000&seed=42`
- **1 milyon** task için deterministic preview sample üretir (seed ile)
- Redis cache ile MISS→HIT proof:
  ```bash
  # First call (MISS):  x-cache: MISS, x-compute-time-ms: 0-5ms
  # Second call (HIT):  x-cache: HIT,  x-compute-time-ms: 0ms
  ```
- Cache proof headers: `X-Cache`, `X-Compute-Time-ms`, `X-Cache-Key`
- Demo script: `bash infra/scripts/demo.sh`

Kalıcı kayıt (SQLite) için:

`POST /api/v1/synthetic/tasks/persist?n=1000000&seed=42`
- `synthetic_tasks` tablosuna yazar (Mission Control UI'yi kirletmez)
- `X-Compute-Time-ms` ile compute süresini gösterir

### ✅ 4. Responsive Arayüz
- Frontend: React-based responsive UI (teammate: burcuyldrm)
- **UI Theme:** Jarvis/Iron Man inspired cyberpunk aesthetics (terminal-style, typewriter effects, glow animations)
- Backend API: Mobile-first tasarım için CORS + cache headers hazır
- Docker Compose ile backend+frontend+redis orchestration
- Real-time metrics dashboard with animated charts

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
- `client/`: **Active React frontend** (Vite + React 19 + TanStack Query + shadcn/ui)
- `frontend/`: Legacy placeholder (deprecated - use `client/` instead)
- `infra/nginx/`: nginx notes for future deployment
- `infra/scripts/demo.sh`: instructor-friendly demo (health + cache proof)
- `docs/`: architecture + API contract + demo steps

## Docs
- API contract (most critical): `docs/api_contract.md`
- Architecture (1-page): `docs/architecture.md`
- Demo steps: `docs/demo_steps.md`

## Environment Variables

| Variable | Required | Default | Description |
|---------|----------|---------|-------------|
| `REDIS_URL` | No | `redis://localhost:6379/0` | Redis connection URL (optional; if Redis is unavailable, cache is bypassed) |
| `CACHE_TTL_SECONDS` | No | `120` | TTL for context cache |
| `APP_VERSION` | No | `0.1.0` | Application version |
| `EXCHANGE_BASE` | No | `EUR` | Base currency for exchange rates (Frankfurter/ECB) |
| `WEATHER_LAT`, `WEATHER_LON` | Optional | - | Weather coordinates (if not set, weather skipped) |
| `GITHUB_OWNER`, `GITHUB_REPO` | Optional | - | GitHub repo (if not set, GitHub skipped) |
| `TMDB_API_KEY` | Optional | - | TMDB API key for `/context.trending` (if not set, trending skipped) |
| `TRAFFIC_API_KEY` | Optional | - | OpenRouteService API key for `/context.traffic` ETA (if not set, traffic skipped) |
| `TRAFFIC_ORIGIN_LAT`, `TRAFFIC_ORIGIN_LON` | Optional | - | Commute origin coordinates (required only if `TRAFFIC_API_KEY` is set) |
| `TRAFFIC_DEST_LAT`, `TRAFFIC_DEST_LON` | Optional | - | Commute destination coordinates (required only if `TRAFFIC_API_KEY` is set) |

### Context Sources (env → enables)

If required env vars are missing, the source is reported under `sources_skipped` (not `sources_failed`) and `/api/v1/context` can still return **200** as long as at least one source succeeds.

| Source | Env vars that enable it | Output (in `/api/v1/context`) |
|---|---|---|
| `weather` | `WEATHER_LAT`, `WEATHER_LON` (optional) | `weather: { city, lat, lon, tz, temp_c, condition }` |
| `github` | `GITHUB_OWNER`, `GITHUB_REPO` (optional), `GITHUB_TOKEN` (optional) | `github: { owner, repo, open_issues, open_prs }` |
| `news` | none | `news: [{ title, url }]` |
| `exchange` | none (`EXCHANGE_BASE` optional) | `exchange: { base, rates, observed_at }` |
| `trending` | `TMDB_API_KEY` (optional) | `trending: [...]` |
| `traffic` | `TRAFFIC_API_KEY` + (`TRAFFIC_ORIGIN_LAT`, `TRAFFIC_ORIGIN_LON`, `TRAFFIC_DEST_LAT`, `TRAFFIC_DEST_LON`) | `traffic: { origin, destination, eta_minutes }` |

## Local run

Node notu: `client/` build için Node.js 18+ gerekir (Node 20 önerilir). `.nvmrc` ile proje Node 20'yi hedefler.

### Option A: Docker Compose (recommended)
If you have Docker Compose available:

```bash
cp backend/.env.example backend/.env
# edit backend/.env (GITHUB_TOKEN, optional keys, etc.)

docker compose up -d --build
```

API will be at `http://localhost:8000`.
UI will be at `http://localhost:3000`.

Notes:
- `docker-compose.yml` expects `backend/.env` (not `.env.example`) so you can safely customize per-server.
- Redis is not exposed on a host port by default (safer for real servers). It is reachable only from containers.

### Option A2: Frontend HMR (no rebuild loop)
If you are actively developing the UI and don't want to rebuild/restart the frontend container for every change, use the dev profile:

```bash
docker compose --profile dev up -d --build backend redis frontend-dev
```

- UI (Vite dev server): `http://localhost:5173`
- Backend (direct): `http://localhost:8000`
- Backend via UI proxy: `http://localhost:5173/api/v1/health`

Stop dev profile services:

```bash
docker compose --profile dev down
```

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
pip install -r requirements-dev.txt

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
- If Redis is not configured/reachable: `X-Cache: BYPASS`

You can also point the script to another base URL:

```bash
API_BASE_URL="http://localhost:8000" bash infra/scripts/demo.sh
```

## Metrics (Prometheus)
The backend exposes `GET /metrics` in Prometheus text format.

```bash
curl -s http://localhost:8000/metrics | head
curl -s http://localhost:8000/metrics | grep -E 'cache_hits_total|cache_misses_total'

Prod UI (nginx) üzerinden de metrics/health proxylanır:

```bash
curl -s http://localhost:3000/metrics | head
curl -s http://localhost:3000/health | jq .
```
```

## API quick reference
All endpoints are under `/api/v1` and use the same response envelope.

| Endpoint | Method | Description | Cache |
|----------|--------|-------------|-------|
| `/api/v1/health` | GET | Liveness + version | No |
| `/context` | GET | Aggregated context (weather/github/news) | Yes (short TTL) |
| `/synthetic/tasks` | GET | Cache proof endpoint (`?n=100000&seed=42`) | Yes (when seed provided) |
| `/synthetic/tasks/persist` | POST | Persist synthetic tasks to SQLite (`?n=1000000&seed=42`) | No |
| `/missions/generate` | POST | Generate missions from context | No |
| `/reports/mission-load` | GET | Heavy-compute report (`?window=7d&bucket=day&seed=42`) | Yes (when seed provided) |
| `/report` | GET | Demo-friendly report with context + missions | No |

### curl examples

```bash
# Health check (preferred)
curl -s http://localhost:8000/api/v1/health | jq .

# Backward-compatible alias
curl -s http://localhost:8000/health | jq .

# Context snapshot
curl -s http://localhost:8000/api/v1/context | jq '.data | keys'

# Synthetic tasks (cache proof)
curl -sD - http://localhost:8000/api/v1/synthetic/tasks?n=100000\&seed=42 -o /dev/null | grep -i x-cache

# Synthetic tasks persist (SQLite)
curl -sD - -X POST 'http://localhost:8000/api/v1/synthetic/tasks/persist?n=100000&seed=42' -o /dev/null | grep -i x-compute-time-ms

# Mission-load report (cache proof)
curl -sD - 'http://localhost:8000/api/v1/reports/mission-load?window=7d&bucket=day&seed=42' -o /dev/null | grep -i x-cache

# Generate missions (body is optional; defaults are applied)
curl -s -X POST 'http://localhost:8000/api/v1/missions/generate' | jq '.data.run_id'

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

## Contributors

### Frontend Development
- **[@burcuyldrm](https://github.com/burcuyldrm)** - Cyberpunk UI Design & Implementation
  - React 18 + Vite 7.3.1 + TypeScript scaffolding
  - shadcn/ui component library integration (50+ components)
  - Cyberpunk theme design (cyan/purple/green palette, neon glows, terminal aesthetics)
  - Wouter routing setup
  - Framer Motion animations
  - Original work from `feature/frontend-ui` branch

### Backend Development & Integration
- **[@miclaldogan](https://github.com/miclaldogan)** - FastAPI Backend & System Architecture
  - FastAPI REST API with 6 endpoints
  - Redis cache layer with proof headers
  - 6 ingestion sources (weather, github, news, exchange, traffic, trending)
  - Docker Compose orchestration
  - Frontend-backend integration & API adaptation
  - Rate limiting & metrics

### Quality Assurance & Documentation
- **[@mervecaloglu](https://github.com/mervecaloglu)** - Testing & Documentation
  - Backend test suite (18 tests)
  - Documentation improvements
  - Traffic ingestion implementation
  - Environment configuration

- **[@reyyannerva](https://github.com/reyyannerva)** - Specifications & Documentation
  - Mission generation rules (v1 spec)
  - DB schema draft (tasks/context/reports)
  - Synthetic tasks generator spec (100k/1M)
  - Report aggregation spec (bucket/window)
  - Context schema normalization
  - Demo documentation & snapshots
  - 3 merged PRs (#23, #37, #57)
  - 6 closed issues (#2, #3, #6, #8, #14, #76)

## Troubleshooting
- If `jq` is missing (common on fresh servers): either install it (`sudo apt install -y jq`) or remove `| jq .` from curl examples.
- If `docker compose` is missing:
	- On Mint/Ubuntu, `sudo apt install -y docker-compose-v2` typically provides it.
	- Some setups use `docker-compose-plugin` or legacy `docker-compose`.
	- Or use the manual run steps above.
- If backend can’t reach Redis in manual mode: ensure `REDIS_URL=redis://localhost:6379/0`.


