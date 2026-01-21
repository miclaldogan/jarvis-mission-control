# ContextSnapshot Schema

## Overview

The internal `ContextSnapshot` is the normalized data model used by the backend to aggregate contextual information from multiple sources (weather, calendar, news, GitHub). 

The **v1 public API** returns a normalized `Context` object via `GET /api/v1/context` wrapped in the standard [response envelope](api_contract.md#response-envelope-standard).

**Note:** Internal ingestion logic and error tracking (sources_ok, sources_failed) are implementation details. The v1 contract exposes only clean, aggregated fields.

## Context Data Model (Public v1 API)

Exposed via `GET /api/v1/context` in the `data` field of the standard response envelope.

| Field | Type | Description |
|-------|------|-------------|
| `context_id` | string | Unique identifier for this snapshot (e.g., `ctx_01H...`) |
| `observed_at` | string (ISO 8601, UTC) | Timestamp when data was aggregated; format: `YYYY-MM-DDTHH:mm:ssZ` |
| `weather` | WeatherContext \| null | Current weather conditions, or null if unavailable |
| `calendar` | object | Calendar summary (e.g., `{events_today: 3}`) |
| `news` | array | List of news articles |
| `github` | GitHubContext \| null | GitHub repository stats, or null if unavailable |

## Internal ContextSnapshot (Backend)

Used internally during ingestion; not exposed directly in v1 API.

| Field | Type | Description |
|-------|------|-------------|
| `context_id` | string | Unique identifier for this snapshot |
| `observed_at` | string (ISO 8601, UTC) | Timestamp when data was fetched |
| `weather` | WeatherContext \| null | Current weather conditions |
| `calendar` | array | List of calendar events |
| `news` | array | List of news articles |
| `github` | GitHubContext \| null | GitHub repository stats |
| `sources_ok` | array of strings | **[Internal only]** Names of sources that ingested successfully |
| `sources_failed` | array of objects | **[Internal only]** Sources that failed; each has `{source: string, error: string}` |

### WeatherContext

```json
{
  "city": "Istanbul",
  "temp_c": 8,
  "condition": "rain"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `city` | string | City name |
| `temp_c` | number | Temperature in Celsius |
| `condition` | string | One of: `rain`, `snow`, `cloudy`, `clear`, `unknown` |

### GitHubContext

```json
{
  "open_issues": 12,
  "open_prs": 4
}
```

| Field | Type | Description |
|-------|------|-------------|
| `open_issues` | integer | Count of currently open issues |
| `open_prs` | integer | Count of currently open pull requests |

## Full Example (Public v1 Response)

Standard [response envelope](api_contract.md#response-envelope-standard) with Context in the `data` field:

```json
{
  "ok": true,
  "data": {
    "context_id": "ctx_01H2xcejqtf2nrebnz8qp4mk78",
    "observed_at": "2026-01-21T14:30:00Z",
    "weather": {
      "city": "Istanbul",
      "temp_c": 8,
      "condition": "rain"
    },
    "calendar": {
      "events_today": 2
    },
    "news": [
      {
        "title": "AI breakthroughs in 2026",
        "url": "https://example.com/news/1"
      }
    ],
    "github": {
      "open_issues": 12,
      "open_prs": 4
    }
  },
  "meta": {
    "request_id": "req_01H2xcejqtf2nrebnz8qp4mk78",
    "ts": "2026-01-21T14:30:00Z"
  }
}
```

## Partial Success Behavior (Internal)

The backend ingestion process implements partial success: if one source fails (e.g., weather API timeout), ingestion continues with other sources (e.g., GitHub, news). Failed sources are recorded in `sources_failed` (internal only) with source name and error message.

- **Success criteria:** At least one source successfully ingests data.
- **HTTP 502 response:** Returned only if **all** sources fail or the request is malformed.
- **HTTP 200 response:** Returned if at least one source succeeds, even with partial failures.

This allows the API to always return the best available context, ensuring resilience to transient upstream failures.

## References

- [API Contract v1](api_contract.md) — Standard response envelope and error codes
- [Architecture](architecture.md) — Ingestion pipeline and source connectors

