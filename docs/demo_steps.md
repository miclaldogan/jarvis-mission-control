# Demo Steps

Goal: show the project works end-to-end and prove caching via headers.

## Local demo (developer machine)
1. Start services:
	- `docker compose up --build`
2. Health check:
	- `curl -i http://localhost:8000/api/v1/health`
3. Read current context (if no context exists yet, expect 404 until ingestion is implemented):
	- `curl -i http://localhost:8000/api/v1/context`
4. Synthetic tasks twice to show cache proof headers (seed enables caching):
	- 1st call (expected MISS): `curl -i 'http://localhost:8000/api/v1/synthetic/tasks?n=100000&seed=42'`
	- 2nd call (expected HIT):  `curl -i 'http://localhost:8000/api/v1/synthetic/tasks?n=100000&seed=42'`
	- Verify headers: `X-Cache`, `X-Compute-Time-ms` (and optionally `X-Cache-Key`)
5. Report twice to show cache:
	- 1st call (expected MISS): `curl -i 'http://localhost:8000/api/v1/report?window=30d&bucket=hour'`
	- 2nd call (expected HIT):  `curl -i 'http://localhost:8000/api/v1/report?window=30d&bucket=hour'`
	- Compare `X-Cache` + compute time

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
- `GET /api/v1/report` responds for a realistic `window` + `bucket`.
