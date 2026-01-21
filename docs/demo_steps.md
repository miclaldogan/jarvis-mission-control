# Demo Steps

Goal: show the project works end-to-end and prove caching via headers.

## Local demo (developer machine)
1. Start services:
	- `docker compose up --build`
2. Health check:
	- `curl -i http://localhost:8000/api/v1/health`
3. Ingest context:
	- `curl -i -X POST http://localhost:8000/api/v1/context/ingest \
	  -H 'Content-Type: application/json' \
	  -d '{"source":"manual","observed_at":"2026-01-21T09:00:00Z","weather":{"city":"Istanbul","temp_c":7,"condition":"rain"}}'`
4. Generate missions:
	- `curl -i -X POST http://localhost:8000/api/v1/missions/generate \
	  -H 'Content-Type: application/json' \
	  -d '{"date":"2026-01-21","max_missions":8}'`
5. Read today missions twice to show cache proof headers:
	- 1st call (expected MISS): `curl -i http://localhost:8000/api/v1/missions/today`
	- 2nd call (expected HIT): `curl -i http://localhost:8000/api/v1/missions/today`
	- Verify headers: `X-Cache`, `X-Compute-Time-ms`
6. Reports (heavy) twice to show cache:
	- `curl -i 'http://localhost:8000/api/v1/reports/mission-load?window=30d&bucket=hour'`
	- repeat the same request and compare `X-Cache` + timing

## Server demo (VPS)
1. Deploy with Docker Compose (same repo). Confirm ports open.
2. If domain exists:
	- `api.<domain>` routes to backend, `app.<domain>` routes to frontend.
3. Run the same curl steps against `https://api.<domain>/api/v1/...`.
4. Show HTTPS certificate and HTTP→HTTPS redirect.

## Evidence checklist (for the instructor)
- A public URL (or server IP) that serves the API.
- `GET /api/v1/health` returns `200`.
- Cache proof headers observed on cached endpoints:
  - `X-Cache: MISS` then `X-Cache: HIT` on repeated calls
  - `X-Compute-Time-ms` decreases (typically) on HIT
- Report endpoint responds for a realistic `window` + `bucket`.
