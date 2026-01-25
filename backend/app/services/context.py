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
from app.services.ingestion.traffic import fetch_traffic_eta_minutes


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _missing(*names: str) -> list[str]:
    out: list[str] = []
    for name in names:
        if not os.getenv(name):
            out.append(name)
    return out


async def build_context_snapshot(
    *,
    debug: bool = False,
    news_limit: int = 5,
    city: str = None,
    news_mode: str = "front_page",
) -> dict[str, Any]:
    """Aggregate multiple external sources into a single normalized context dict.

    Contract notes:
    - Always returns a normalized schema.
    - Exposes source health lists (ok/failed/skipped) to support UI resilience.
    - Raw payloads are included only when debug=true.
    
    Args:
        debug: Include raw API responses in output
        news_limit: Maximum number of news articles to return
        city: City name for weather (Istanbul, Ankara, Izmir, Antalya)
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
        "exchange": None,
        "traffic": None,
        "trending": [],
        "calendar": {"events_today": 0},
        "sources_ok": [],
        "sources_failed": [],
        "sources_skipped": [],
        # Freshness tracking: when each source was last updated
        "freshness": {},
    }

    # Weather
    missing_weather = _missing("WEATHER_LAT", "WEATHER_LON")
    if missing_weather:
        data["sources_skipped"].append(
            {
                "source": "weather",
                "reason": f"Missing required env vars: {', '.join(missing_weather)}",
            }
        )
    else:
        try:
            fetch_time = _now_iso()
            w = await fetch_weather(city=city)
            weather_obj: dict[str, Any] = {
                "city": w.get("city") if isinstance(w, dict) else os.getenv("WEATHER_CITY", "Unknown"),
                "lat": os.getenv("WEATHER_LAT"),
                "lon": os.getenv("WEATHER_LON"),
                "tz": os.getenv("WEATHER_TZ"),
                "temp_c": w.get("temp_c") if isinstance(w, dict) else None,
                "condition": w.get("condition") if isinstance(w, dict) else None,
            }
            if debug:
                weather_obj["raw"] = w if isinstance(w, dict) else {"value": w}
            data["weather"] = weather_obj
            data["sources_ok"].append("weather")
            data["freshness"]["weather_updated_at"] = fetch_time
        except Exception as e:
            data["sources_failed"].append({"source": "weather", "error": str(e)})

    # GitHub
    missing_github = _missing("GITHUB_OWNER", "GITHUB_REPO")
    if missing_github:
        data["sources_skipped"].append(
            {
                "source": "github",
                "reason": f"Missing required env vars: {', '.join(missing_github)}",
            }
        )
    else:
        try:
            fetch_time = _now_iso()
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
            data["freshness"]["github_updated_at"] = fetch_time
        except Exception as e:
            # UI expectation: show the configured repo immediately on first load.
            # Even if GitHub ingestion fails (rate limit/network), return a minimal
            # object so the repo/link is visible while still reporting the failure.
            data["github"] = {
                "owner": os.getenv("GITHUB_OWNER"),
                "repo": os.getenv("GITHUB_REPO"),
                "open_issues": 0,
                "open_prs": 0,
                "status": "failed",
                "error": str(e),
            }
            data["sources_failed"].append({"source": "github", "error": str(e)})

    # News (Hacker News via Algolia)
    try:
        fetch_time = _now_iso()
        data["news"] = await fetch_news(limit=news_limit, mode=news_mode)
        data["sources_ok"].append("news")
        data["freshness"]["news_updated_at"] = fetch_time
    except Exception as e:
        data["sources_failed"].append({"source": "news", "error": str(e)})

    # Exchange rates (Frankfurter/ECB) - no API key required
    try:
        fetch_time = _now_iso()
        base = os.getenv("EXCHANGE_BASE", "TRY")
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
            data["freshness"]["exchange_updated_at"] = fetch_time
        else:
            data["sources_failed"].append({"source": "exchange", "error": ex.get("error", "unknown")})
    except Exception as e:
        data["sources_failed"].append({"source": "exchange", "error": str(e)})

    # Trending (TMDB API)
    tmdb_key = os.getenv("TMDB_API_KEY")
    if not tmdb_key:
        data["sources_skipped"].append(
            {
                "source": "trending",
                "reason": "Missing required env var: TMDB_API_KEY",
            }
        )
    else:
        try:
            fetch_time = _now_iso()
            trending_result = await fetch_trending(api_key=tmdb_key, limit=5)
            if trending_result.get("ok"):
                data["trending"] = trending_result.get("items", [])
                data["sources_ok"].append("trending")
                data["freshness"]["trending_updated_at"] = fetch_time
            else:
                data["sources_failed"].append(
                    {"source": "trending", "error": trending_result.get("error", "unknown")}
                )
        except Exception as e:
            data["sources_failed"].append({"source": "trending", "error": str(e)})
    
    # Traffic / Commute ETA (OpenRouteService)
    traffic_key = os.getenv("TRAFFIC_API_KEY")
    if not traffic_key:
        data["sources_skipped"].append(
            {
                "source": "traffic",
                "reason": "Missing required env var: TRAFFIC_API_KEY",
            }
        )
    else:
        # coords are required (we keep this check here so we can show clear reason)
        missing_coords = _missing("TRAFFIC_ORIGIN_LAT", "TRAFFIC_ORIGIN_LON", "TRAFFIC_DEST_LAT", "TRAFFIC_DEST_LON")
        if missing_coords:
            data["sources_skipped"].append(
                {
                    "source": "traffic",
                    "reason": f"Missing required env vars: {', '.join(missing_coords)}",
                }
            )
        else:
            try:
                fetch_time = _now_iso()
                t = await fetch_traffic_eta_minutes(timeout_s=10.0)
                if t.get("ok"):
                    traffic_obj: dict[str, Any] = t["data"]
                    if debug:
                        traffic_obj["raw"] = t
                    data["traffic"] = traffic_obj
                    data["sources_ok"].append("traffic")
                    data["freshness"]["traffic_updated_at"] = fetch_time
                else:
                    # If adapter returned a skip_reason, treat as skipped (not failed)
                    data["sources_skipped"].append(
                        {"source": "traffic", "reason": f"Skipped: {t.get('skip_reason', 'unknown')}"}
                    )
            except Exception as e:
                data["sources_failed"].append({"source": "traffic", "error": str(e)})
    return data
