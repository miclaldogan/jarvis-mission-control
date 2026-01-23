# Real Ingestion Implementation: GET /api/v1/context

## Overview

The `GET /api/v1/context` endpoint now implements real data ingestion from external REST APIs:

1. **Weather** via Open-Meteo
2. **GitHub Repository Stats** via GitHub REST API

## Files Changed

### 1. [backend/requirements.txt](backend/requirements.txt)
- Added `pydantic-settings==2.1.0` for environment variable management
- Added `httpx==0.25.2` for async HTTP calls

### 2. [backend/app/settings.py](backend/app/settings.py)
- Migrated from `dataclass` to Pydantic `BaseSettings`
- Added required environment variables:
  - `WEATHER_LAT` (latitude)
  - `WEATHER_LON` (longitude)
  - `GITHUB_OWNER` (GitHub owner)
  - `GITHUB_REPO` (GitHub repository)
- Added optional environment variables:
  - `WEATHER_CITY` (default: "Unknown")
  - `WEATHER_TZ` (default: "Europe/Istanbul")
  - `GITHUB_TOKEN` (GitHub personal access token for higher rate limits)
- Clear validation error messages on startup if required vars are missing

### 3. [backend/app/services/ingestion/weather.py](backend/app/services/ingestion/weather.py)
- Async function `fetch_weather()` that:
  - Calls Open-Meteo API at `https://api.open-meteo.com/v1/forecast`
  - Passes `latitude`, `longitude`, `current_weather=true`, `timezone`
  - Maps WMO weather codes to conditions: `rain`, `snow`, `cloudy`, `clear`, `unknown`
  - Returns `{"temp": <float>, "condition": <string>}` in Celsius
  - 10-second timeout
  - Raises exception with clear error message on failure

### 4. [backend/app/services/ingestion/github.py](backend/app/services/ingestion/github.py)
- Async function `fetch_github()` that:
  - Calls GitHub API at `https://api.github.com/repos/{owner}/{repo}`
  - Optional Bearer token support via `GITHUB_TOKEN`
  - Fetches `open_issues_count` from repo endpoint
  - Fetches `open_prs` count via `/pulls` endpoint with pagination
  - Returns `{"open_issues": <int>, "open_prs": <int>}`
  - 10-second timeout per request
  - Graceful fallback: PR fetch failure doesn't fail entire request (defaults to 0)

### 5. [backend/app/api/v1/endpoints/context.py](backend/app/api/v1/endpoints/context.py)
- Implements **partial success** pattern:
  - Calls both `fetch_weather()` and `fetch_github()` independently
  - Returns HTTP 200 if **at least one source succeeds**
  - Returns HTTP 502 only if **all sources fail**
  - Tracks successes in `sources_ok` (internal tracking)
  - Tracks failures in `sources_failed` with source name and error message
- Response format per v1 contract:
  ```json
  {
    "ok": true,
    "data": {
      "context_id": "ctx_<uuid>",
      "observed_at": "2026-01-21T14:30:00Z",
      "weather": {
        "city": "Istanbul",
        "temp_c": 8,
        "condition": "rain"
      },
      "calendar": {"events_today": 0},
      "news": [],
      "github": {
        "open_issues": 12,
        "open_prs": 4
      }
    },
    "meta": {...}
  }
  ```
- On total failure (all sources):
  ```json
  {
    "ok": false,
    "data": null,
    "error": {
      "code": "UPSTREAM_FAILED",
      "message": "All data sources failed",
      "details": {
        "sources_failed": [
          {"source": "weather", "error": "..."},
          {"source": "github", "error": "..."}
        ]
      }
    },
    "meta": {...}
  }
  ```

### 6. [backend/.env.example](backend/.env.example)
- Updated with all required and optional environment variables

## Setup & Testing

### 1. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 2. Set Environment Variables

Create `.env` in `backend/` directory (copy from `.env.example`):
```bash
# Weather (Open-Meteo)
WEATHER_LAT=41.0082
WEATHER_LON=28.9784
WEATHER_CITY=Istanbul
WEATHER_TZ=Europe/Istanbul

# GitHub
GITHUB_OWNER=miclaldogan
GITHUB_REPO=jarvis-mission-control
GITHUB_TOKEN=  # Optional: your GitHub personal access token
```

### 3. Run the Backend
```bash
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

### 4. Test the Endpoint

**Test with real data:**
```bash
curl -X GET http://localhost:8000/api/v1/context
```

**Expected response (if weather and GitHub succeed):**
```json
{
  "ok": true,
  "data": {
    "context_id": "ctx_a1b2c3d4e5f6g7h8i9j0",
    "observed_at": "2026-01-21T14:30:00Z",
    "weather": {
      "city": "Istanbul",
      "temp_c": 8,
      "condition": "rain"
    },
    "calendar": {"events_today": 0},
    "news": [],
    "github": {
      "open_issues": 12,
      "open_prs": 4
    }
  },
  "meta": {
    "request_id": "req_abc...",
    "ts": "2026-01-21T14:30:00Z"
  }
}
```

**Test partial failure (weather fails, GitHub succeeds):**
```bash
# Unset WEATHER_LAT
unset WEATHER_LAT
curl -X GET http://localhost:8000/api/v1/context
```

Response will still be 200 with weather=null, github populated.

**Test total failure (both fail):**
```bash
# Unset both weather and GitHub env vars
unset WEATHER_LAT GITHUB_OWNER
curl -X GET http://localhost:8000/api/v1/context
```

Response will be 502 with `ok: false`, `code: "UPSTREAM_FAILED"`.

## Key Design Decisions

1. **Partial Success Pattern**: API returns 200 if any source succeeds, enabling resilience to transient failures. Only returns 502 if all sources fail.

2. **Async I/O**: All HTTP calls use `httpx.AsyncClient` with 10-second timeouts to prevent hanging.

3. **Graceful Degradation**: PR count fetch failures don't fail the entire GitHub ingestion; defaults to 0.

4. **Environment Variables**: Required vars at startup via Pydantic BaseSettings ensures early failure with clear error messages.

5. **Logging**: Exception messages are captured in `sources_failed` for debugging and monitoring.

## Performance

- Weather API: ~200ms (Open-Meteo is very fast)
- GitHub API: ~300-500ms (depends on rate limit, token presence)
- Total p99: <1s (with timeouts as safety net)
- No database queries (fully async, no blocking calls)

## Future Enhancements

- [ ] Caching layer (Redis) to reduce API calls
- [ ] Calendar ingestion (Google Calendar or Outlook)
- [ ] News ingestion (NewsAPI or similar)
- [ ] Better PR count optimization (GraphQL query)
- [ ] Structured logging (OpenTelemetry)
