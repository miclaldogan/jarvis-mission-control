from __future__ import annotations

import os
from datetime import datetime, timezone
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from app.http_envelope import ok, err
from app.services.ingestion.weather import fetch_weather
from app.services.ingestion.github import fetch_github

router = APIRouter()

@router.get("/context")
async def get_context(request: Request):
    """
    Return latest aggregated context snapshot.

    Partial success:
      - If one source fails but another succeeds -> 200 with failed list.
      - If all sources fail -> 502.
    """
    fetched_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    data: dict = {"fetched_at": fetched_at, "weather": None, "github": None}
    sources_ok: list[str] = []
    sources_failed: list[dict[str, str]] = []

    # Weather
    try:
        w = await fetch_weather()
        data["weather"] = {
            "city": os.getenv("WEATHER_CITY", "Unknown"),
            "lat": os.getenv("WEATHER_LAT"),
            "lon": os.getenv("WEATHER_LON"),
            "tz": os.getenv("WEATHER_TZ"),
            # normalize common keys from ingestion
            "temp_c": w.get("temp") if isinstance(w, dict) else None,
            "condition": w.get("condition") if isinstance(w, dict) else None,
            "raw": w if isinstance(w, dict) else {"value": w},
        }
        sources_ok.append("weather")
    except Exception as e:
        sources_failed.append({"source": "weather", "error": str(e)})

    # GitHub
    try:
        g = await fetch_github()
        data["github"] = {
            "owner": os.getenv("GITHUB_OWNER"),
            "repo": os.getenv("GITHUB_REPO"),
            "open_issues": g.get("open_issues") if isinstance(g, dict) else None,
            "open_prs": g.get("open_prs") if isinstance(g, dict) else None,
            "raw": g if isinstance(g, dict) else {"value": g},
        }
        sources_ok.append("github")
    except Exception as e:
        sources_failed.append({"source": "github", "error": str(e)})

    data["sources_ok"] = sources_ok
    data["sources_failed"] = sources_failed

    if len(sources_ok) == 0:
        payload = err(request, code="BAD_GATEWAY", message="All context sources failed", details={"sources_failed": sources_failed})
        return JSONResponse(payload, status_code=502)

    payload = ok(request, data)
    return JSONResponse(payload, status_code=200)
