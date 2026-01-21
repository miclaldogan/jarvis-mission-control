# API Contract (v1)

## Base URL & versioning
- Prefix: `/api/v1`
- Content-Type: `application/json`

## Auth
- None for now (course/demo simplicity).
- If later required: `Authorization: Bearer <token>`.

## Response envelope (standard)
All endpoints return the same envelope.

### Success
```json
{
	"ok": true,
	"data": {},
	"meta": {
		"request_id": "req_01H...",
		"ts": "2026-01-21T12:00:00Z"
	}
}
```

### Error
```json
{
	"ok": false,
	"data": null,
	"meta": {
		"request_id": "req_01H...",
		"ts": "2026-01-21T12:00:00Z"
	},
	"error": {
		"code": "INVALID_PARAMS",
		"message": "Human readable message",
		"details": {"field": "..."}
	}
}
```

## Cache proof headers (standard)
For cacheable endpoints, the server MUST return:
- `X-Cache: HIT|MISS`
- `X-Compute-Time-ms: <int>`
- `X-Cache-Key: <string>` (optional but recommended as proof)
- `Cache-Control: public, max-age=<seconds>` (or `private` if needed)

### Cacheable endpoints
- `GET /api/v1/synthetic/tasks`
- `GET /api/v1/report` (optional; not required for sprint 1)

## Endpoints

### GET /api/v1/health
- Purpose: Liveness check.
- Query params: none.
- Cache: no.
- Success (`200`) example:
```json
{
	"ok": true,
	"data": {
		"status": "ok",
		"service": "backend",
		"version": "0.1.0",
		"time": "2026-01-21T12:00:00Z"
	},
	"meta": {"request_id": "req_01H...", "ts": "2026-01-21T12:00:00Z"}
}
```
- Errors: `INTERNAL` (500).

### GET /api/v1/context
- Purpose: Return the latest aggregated context snapshot (ingestion output).
- Query params (optional):
	- `at`: ISO timestamp (returns snapshot closest to time)
- Cache: optional (short TTL ok).
- Success (`200`) example:
```json
{
	"ok": true,
	"data": {
		"context_id": "ctx_01H...",
		"observed_at": "2026-01-21T09:00:00Z",
		"weather": {"city": "Istanbul", "temp_c": 7, "condition": "rain"},
		"news": [{"title": "Example headline", "url": "https://example.com"}],
		"github": {"open_issues": 12, "open_prs": 4},
		"calendar": {"events_today": 3}
	},
	"meta": {"request_id": "req_01H...", "ts": "2026-01-21T12:00:00Z"}
}
```
- Errors:
	- `NOT_FOUND` (404) if no context exists yet.
	- `INVALID_PARAMS` (400) for invalid `at`.

### GET /api/v1/synthetic/tasks
- Purpose: Generate synthetic tasks for load/performance demos.
- Query params:
	- `n` (required): `100000` or `1000000`
	- `seed` (optional, recommended): deterministic generation
- Cache:
	- Cache ON if `seed` is provided.
	- Cache OFF if `seed` missing.
- Payload strategy (decision): do NOT return full list for 100k/1M.
	- `meta.total = n`
	- `data.sample = first 50 tasks`
	- `data.preview_hash` = stable hash derived from `(n, seed)` and sample content
- Success (`200`) example:
```json
{
	"ok": true,
	"data": {
		"n": 100000,
		"seed": 42,
		"sample": [
			{"id": "tsk_000001", "title": "Synthetic task #1", "priority": "low"},
			{"id": "tsk_000002", "title": "Synthetic task #2", "priority": "medium"}
		],
		"preview_hash": "sha256:..."
	},
	"meta": {
		"request_id": "req_01H...",
		"ts": "2026-01-21T12:00:00Z",
		"total": 100000
	}
}
```
- Headers (when cached): `X-Cache`, `X-Compute-Time-ms`, optional `X-Cache-Key`.
- Errors:
	- `INVALID_PARAMS` (400) for invalid `n`/`seed`.

### GET /api/v1/report
- Purpose: Return a single “demo-friendly” report that includes:
	- current context summary
	- missions list (embedded here for simplicity)
	- performance/cache metrics
- Query params (optional):
	- `window`: `7d|30d` (default `30d`)
	- `bucket`: `hour|day` (default `hour`)
- Cache: optional (not required for sprint 1; demo focuses on `synthetic/tasks`).
- Missions schema v1
	- Minimum fields (required):
		- `id` (string)
		- `title` (string)
		- `priority` (string: `P1|P2|P3|P4`)
		- `status` (string: `open|done|snoozed`)
		- `due_at` (string|null, ISO timestamp)
		- `tags` (string[])
		- `why` (string)
		- `actions` (array)
			- each action: `{ "label": string, "type": "link"|"api", "target": string }`
	- Optional but recommended:
		- `evidence` (object)
			- `sources` (string[]; e.g. `weather|github|news`)
			- `confidence` (number; 0..1)
		- `cache` (object)
			- `generated_at` (string, ISO timestamp)
			- `seed` (number|null)
- Success (`200`) example:
```json
{
	"ok": true,
	"data": {
		"context": {
			"context_id": "ctx_01H...",
			"observed_at": "2026-01-21T09:00:00Z",
			"weather": {"city": "Istanbul", "temp_c": 7, "condition": "rain"}
		},
		"missions": [
			{
				"id": "msn_001",
				"title": "Bugün yağmur var: dışarı planını 18:00 sonrası yap",
				"priority": "P2",
				"status": "open",
				"due_at": null,
				"tags": ["weather", "planning"],
				"why": "Yağmur 14:00–17:00 arası yoğun görünüyor.",
				"actions": [
					{"label": "Hava detayına git", "type": "link", "target": "/ui/context#weather"}
				],
				"evidence": {"sources": ["weather"], "confidence": 0.78}
			}
		],
		"metrics": {
			"window": "30d",
			"bucket": "hour",
			"series": [
				{"ts": "2026-01-20T00:00:00Z", "missions_total": 12, "missions_completed": 5}
			]
		}
	},
	"meta": {"request_id": "req_01H...", "ts": "2026-01-21T12:00:00Z"}
}
```
- Headers:
	- `X-Compute-Time-ms` recommended.
	- Cache proof headers only if/when report caching is enabled.
- Errors:
	- `INVALID_PARAMS` (400) for invalid `window`/`bucket`.
	- `INTERNAL` (500).

## Error codes
- `INVALID_PARAMS` → 400
- `NOT_FOUND` → 404
- `RATE_LIMITED` → 429
- `UPSTREAM_FAILED` → 502
- `INTERNAL` → 500
