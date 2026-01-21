# API Contract

## Base
- Prefix: `/api/v1`
- Content-Type: `application/json`
- Cache proof headers (when caching is applicable):
	- `X-Cache: HIT|MISS`
	- `X-Compute-Time-ms: <number>`

## Common errors (shape)
All error responses use a consistent envelope:

```json
{
	"error": {
		"code": "VALIDATION_ERROR",
		"message": "Human readable message",
		"details": {"field": "..."}
	}
}
```

Typical status codes:
- `400` validation or bad request
- `404` not found
- `409` conflict (e.g., completing an already-completed mission)
- `429` rate limit (if/when external ingestion is proxied)
- `500` unexpected server error

## Endpoints

### GET /api/v1/health
- Purpose: Liveness check for backend + dependencies.
- Request: no params.
- Response example (`200`):

```json
{
	"status": "ok",
	"service": "backend",
	"version": "0.1.0",
	"time": "2026-01-21T00:00:00Z"
}
```

- Error cases: `500` if core dependencies fail (optional).
- Cache: no.
- Headers: cache proof headers not required.

### POST /api/v1/context/ingest
- Purpose: Ingest a normalized context snapshot for later mission generation.
- Request body example:

```json
{
	"source": "manual",
	"observed_at": "2026-01-21T09:00:00Z",
	"weather": {"city": "Istanbul", "temp_c": 7, "condition": "rain"},
	"news": [{"title": "Example headline", "url": "https://example.com"}],
	"github": {"open_issues": 12, "open_prs": 4},
	"calendar": {"events_today": 3}
}
```

- Response example (`202`):

```json
{
	"accepted": true,
	"context_id": "ctx_01HZZZ...",
	"stored_at": "2026-01-21T09:00:01Z"
}
```

- Error cases: `400` invalid schema.
- Cache: no.
- Headers: cache proof headers not required.

### POST /api/v1/missions/generate
- Purpose: Generate missions based on the latest (or specified) context snapshot.
- Request body example:

```json
{
	"context_id": "ctx_01HZZZ...",
	"date": "2026-01-21",
	"max_missions": 8
}
```

- Response example (`200`):

```json
{
	"date": "2026-01-21",
	"context_id": "ctx_01HZZZ...",
	"missions": [
		{
			"id": "msn_001",
			"title": "Review top 3 open PRs",
			"priority": "high",
			"tags": ["github"],
			"completed": false
		}
	]
}
```

- Error cases: `400` invalid params; `404` context not found.
- Cache: no (generation is a write/compute action).
- Headers: cache proof headers not required.

### GET /api/v1/missions/today
- Purpose: Read today’s mission list.
- Request params: optional `date=YYYY-MM-DD`.
- Response example (`200`):

```json
{
	"date": "2026-01-21",
	"missions": [
		{
			"id": "msn_001",
			"title": "Review top 3 open PRs",
			"priority": "high",
			"tags": ["github"],
			"completed": false
		}
	]
}
```

- Error cases: `404` if no missions exist for that date (or return empty list; decide later).
- Cache: yes (safe read; cache invalidated on completion/generation).
- Headers: MUST include `X-Cache`, `X-Compute-Time-ms` when cache layer is enabled.

### POST /api/v1/missions/complete/{id}
- Purpose: Mark a mission completed.
- Path param: `id` mission id.
- Request body: optional

```json
{
	"completed_at": "2026-01-21T10:00:00Z"
}
```

- Response example (`200`):

```json
{
	"id": "msn_001",
	"completed": true,
	"completed_at": "2026-01-21T10:00:00Z"
}
```

- Error cases: `404` mission not found; `409` already completed.
- Cache: no; MUST invalidate affected cached reads (e.g. missions/today, reports).
- Headers: cache proof headers not required.

### POST /api/v1/synthetic/tasks?n=1000000&seed=42
- Purpose: Generate synthetic tasks for load/performance demos.
- Query params:
	- `n` (required): number of tasks (e.g. 1000000)
	- `seed` (optional but recommended): deterministic generation
- Response example (`200`):

```json
{
	"n": 1000000,
	"seed": 42,
	"generated_at": "2026-01-21T10:05:00Z",
	"sample": [
		{"id": "tsk_000001", "title": "Synthetic task #1", "priority": "low"},
		{"id": "tsk_000002", "title": "Synthetic task #2", "priority": "medium"}
	],
	"notes": "Response returns a small sample; full payload strategy can be decided later."
}
```

- Error cases: `400` invalid `n`/`seed` (e.g. `n` too large).
- Cache: yes when `seed` is present (same inputs → same outputs). Without `seed`, cache is off.
- Headers: MUST include `X-Cache`, `X-Compute-Time-ms` when cache is enabled.

### GET /api/v1/reports/mission-load?window=30d&bucket=hour
- Purpose: Heavy report of mission load aggregated by time buckets.
- Query params:
	- `window`: e.g. `7d`, `30d`
	- `bucket`: `hour|day`
- Response example (`200`):

```json
{
	"window": "30d",
	"bucket": "hour",
	"series": [
		{"ts": "2026-01-20T00:00:00Z", "missions_total": 12, "missions_completed": 5},
		{"ts": "2026-01-20T01:00:00Z", "missions_total": 8, "missions_completed": 3}
	]
}
```

- Error cases: `400` invalid `window`/`bucket`.
- Cache: yes (heavy compute).
- Headers: MUST include `X-Cache`, `X-Compute-Time-ms`.
