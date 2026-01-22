from __future__ import annotations

import os
import uuid
from datetime import datetime, timezone
from typing import Any

from app.services.ingestion.github import fetch_github
from app.services.ingestion.news import fetch_news
from app.services.ingestion.weather import fetch_weather
from app.services.ingestion.exchange import fetch_exchange_rates
from app.services.ingestion.trending import fetch_trending


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _missing(*names: str) -> list[str]:
    out: list[str] = []
    for name in names:
        if not os.getenv(name):
            out.append(name)
    return out


async def build_context_snapshot(*, debug: bool = False, news_limit: int = 5) -> dict[str, Any]:
    """Aggregate multiple external sources into a single normalized context dict.

    Contract notes:
    - Always returns a normalized schema.
    - Exposes source health lists (ok/failed/skipped) to support UI resilience.
    - Raw payloads are included only when debug=true.
    """

    observed_at = _now_iso()
    context_id = f"ctx_{uuid.uuid4().hex[:12]}"

    data: dict[str, Any] = {
        "context_id": context_id,
        "observed_at": observed_at,
        # backward-compatible alias (will be deprecated in docs)
        "fetched_at": observed_at,
        "weather": None,
        "github": None,
        "news": [],
        "calendar": {"events_today": 0},
        "exchange": None,
        "trending": [],
        "sources_ok": [],
        "sources_failed": [],
        "sources_skipped": [],
    }

    # Weather
    missing_weather = _missing("WEATHER_LAT", "WEATHER_LON")
    if missing_weather:
        data["sources_skipped"].append(
            {"source": "weather", "reason": f"Missing required env vars: {', '.join(missing_weather)}"}
        )
    else:
        try:
            w = await fetch_weather()
            weather_obj: dict[str, Any] = {
                "city": os.getenv("WEATHER_CITY", "Unknown"),
                "lat": os.getenv("WEATHER_LAT"),
                "lon": os.getenv("WEATHER_LON"),
                "tz": os.getenv("WEATHER_TZ"),
                "temp_c": w.get("temp") if isinstance(w, dict) else None,
                "condition": w.get("condition") if isinstance(w, dict) else None,
            }
            if debug:
                weather_obj["raw"] = w if isinstance(w, dict) else {"value": w}
            data["weather"] = weather_obj
            data["sources_ok"].append("weather")
        except Exception as e:
            data["sources_failed"].append({"source": "weather", "error": str(e)})

    # GitHub
    missing_github = _missing("GITHUB_OWNER", "GITHUB_REPO")
    if missing_github:
        data["sources_skipped"].append(
            {"source": "github", "reason": f"Missing required env vars: {', '.join(missing_github)}"}
        )
    else:
        try:
            g = await fetch_github()
            github_obj: dict[str, Any] = {
                "owner": os.getenv("GITHUB_OWNER"),
                "repo": os.getenv("GITHUB_REPO"),
                "open_issues": g.get("open_issues") if isinstance(g, dict) else None,
                "open_prs": g.get("open_prs") if isinstance(g, dict) else None,
            }
            if debug:
                github_obj["raw"] = g if isinstance(g, dict) else {"value": g}
            data["github"] = github_obj
            data["sources_ok"].append("github")
        except Exception as e:
            data["sources_failed"].append({"source": "github", "error": str(e)})

    # News (Hacker News via Algolia)
    try:
        data["news"] = await fetch_news(limit=news_limit)
        data["sources_ok"].append("news")
    except Exception as e:
        data["sources_failed"].append({"source": "news", "error": str(e)})

    # Exchange rates (Frankfurter/ECB) - no API key
    try:
        base = os.getenv("EXCHANGE_BASE", "EUR")
        ex = await fetch_exchange_rates(base=base)
        if ex.get("ok"):
            exchange_obj: dict[str, Any] = {
                "base": ex.get("base"),
                "rates": ex.get("rates"),
                "observed_at": ex.get("observed_at"),
            }
            if debug:
                exchange_obj["raw"] = ex
            data["exchange"] = exchange_obj
            data["sources_ok"].append("exchange")
        else:
            data["sources_failed"].append({"source": "exchange", "error": ex.get("error", "unknown")})
    except Exception as e:
        data["sources_failed"].append({"source": "exchange", "error": str(e)})

    # Trending (TMDB) - optional API key
    tmdb_key = os.getenv("TMDB_API_KEY")
    if not tmdb_key:
        data["sources_skipped"].append(
            {"source": "trending", "reason": "Missing required env vars: TMDB_API_KEY"}
        )
        data["trending"] = []
    else:
        try:
            t = await fetch_trending(api_key=tmdb_key, limit=5)
            if t.get("ok"):
                data["trending"] = t.get("items", [])
                data["sources_ok"].append("trending")
            else:
                data["sources_failed"].append({"source": "trending", "error": t.get("error", "unknown")})
        except Exception as e:
            data["sources_failed"].append({"source": "trending", "error": str(e)})

    return data
