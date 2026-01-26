# Architecture

## Overview
Jarvis Mission Control ingests “context” signals (weather/news/github/etc.), generates a daily mission list, and provides report endpoints with cache proof headers.

## Components
- **Backend (FastAPI)**: REST API under `/api/v1`, owns validation, business rules, and response headers.
- **Redis (cache)**: caches deterministic/heavy endpoints (e.g. reports, synthetic generator with same `seed`, daily missions).
- **Database (later)**: stores context snapshots, missions/tasks, completion status, and report aggregates (exact DB choice can be decided later).
- **Frontend (responsive)**: dashboard/context/lab pages; shows cache badge based on `X-Cache`.
- **Infra (Nginx + SSL)**: reverse proxy to backend/frontend; HTTPS via Let’s Encrypt on VPS.

## Data flow
1. **Context ingestion**: `GET /api/v1/context` fetches live context from external sources (weather, github, news).
2. **Mission generation**: `POST /api/v1/missions/generate` produces missions from context with explainable "why".
3. **Reports**: `GET /api/v1/reports/mission-load` returns load metrics aggregated by `bucket` over `window` (heavy → cached).
4. **Synthetic load**: `GET /api/v1/synthetic/tasks` generates large task sets for performance demos (cached when `seed` is provided).
5. **Demo report**: `GET /api/v1/report` returns combined context + missions + metrics for demo purposes.

### Not yet implemented (future)
- `POST /api/v1/context/ingest` (manual context push; currently auto-fetched)
- `GET /api/v1/missions/today` (daily mission list)
- `POST /api/v1/missions/complete/{id}` (mark mission done)
- Database persistence (currently in-memory/Redis only)

## Cache proof
Endpoints that can be cached MUST return:
- `X-Cache: HIT|MISS`
- `X-Compute-Time-ms: <number>`

The frontend shows a cache badge using `X-Cache`, and the demo uses response headers as “proof”.

## Deployment
- **Local**: Docker Compose.
- **Server**: Docker Compose on Ubuntu VPS.
- **Routing**: Nginx → `api.<domain>` → backend, `app.<domain>` → frontend.
- **SSL**: Let’s Encrypt (Certbot) with HTTP→HTTPS redirect.
