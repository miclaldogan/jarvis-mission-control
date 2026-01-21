# ContextSnapshot Schema

## Overview

The `ContextSnapshot` is the normalized data model ingested via the `/api/v1/context/ingest` endpoint. It aggregates contextual information from multiple sources (weather, calendar, news, GitHub) and tracks ingestion status.

## Top-Level Schema

| Field | Type | Description |
|-------|------|-------------|
| `context_snapshot_id` | string | Unique identifier for this snapshot (UUID) |
| `fetched_at` | string (ISO 8601, UTC) | Timestamp when data was fetched; format: `YYYY-MM-DDTHH:mm:ssZ` |
| `weather` | WeatherContext \| null | Current weather conditions, or null if unavailable |
| `calendar` | array | List of upcoming calendar events |
| `news` | array | List of news articles |
| `github` | GitHubContext \| null | GitHub repository stats, or null if unavailable |
| `sources_ok` | array of strings | Names of sources that ingested successfully |
| `sources_failed` | array of objects | Sources that failed; each has `{source: string, error: string}` |

## Sub-Schemas

### WeatherContext

```json
{
  "temp": 72,
  "condition": "clear"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `temp` | number | Temperature in Celsius |
| `condition` | string | One of: `rain`, `snow`, `cloudy`, `clear`, `unknown` |

### GitHubContext

```json
{
  "repo": "github.com/user/repo",
  "open_issues": 5
}
```

| Field | Type | Description |
|-------|------|-------------|
| `repo` | string | Repository identifier (e.g., `owner/repo`) |
| `open_issues` | integer | Count of currently open issues |

## Full Example

```json
{
  "context_snapshot_id": "550e8400-e29b-41d4-a716-446655440000",
  "fetched_at": "2026-01-21T14:30:00Z",
  "weather": {
    "temp": 68,
    "condition": "cloudy"
  },
  "calendar": [
    {
      "title": "Team standup",
      "start": "2026-01-21T09:00:00Z",
      "end": "2026-01-21T09:30:00Z"
    },
    {
      "title": "Project review",
      "start": "2026-01-21T15:00:00Z",
      "end": "2026-01-21T16:00:00Z"
    }
  ],
  "news": [
    {
      "title": "AI breakthroughs in 2026",
      "source": "TechNews",
      "published_at": "2026-01-21T10:00:00Z"
    }
  ],
  "github": {
    "repo": "jarvis-mission-control",
    "open_issues": 3
  },
  "sources_ok": ["weather", "calendar", "github"],
  "sources_failed": [
    {
      "source": "news",
      "error": "API rate limit exceeded"
    }
  ]
}
```

## Partial Success Behavior

The `/api/v1/context/ingest` endpoint returns **HTTP 200** even if one or more sources fail to retrieve data. Failed sources are recorded in the `sources_failed` array with the source name and error message. This allows the API to accept partial context when some data sources are temporarily unavailable.

- **Success criteria:** At least one source successfully ingests data.
- **Failure response:** Returns HTTP 5xx or 4xx only if all sources fail or the request is malformed.
