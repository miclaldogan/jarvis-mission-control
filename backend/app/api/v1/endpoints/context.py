from __future__ import annotations

import time
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Query, Request
from fastapi.responses import JSONResponse

from app.cache import get_json, set_json
from app.http_envelope import err, ok
from app.metrics import inc_cache_hit, inc_cache_miss
from app.settings import get_settings
from app.services.context import build_context_snapshot


router = APIRouter()


def _context_cache_key(request: Request) -> str:
    items = sorted([(k, v) for (k, v) in request.query_params.multi_items() if k != "refresh"])
    if items:
        query = "&".join([f"{k}={v}" for k, v in items])
    else:
        query = ""
    return f"cache:v1:context:path={request.url.path}:q={query}"


@router.get("/context")
async def get_context(
    request: Request,
    debug: bool = Query(False),
    refresh: bool = Query(False),
    city: str = Query(None, description="City name for weather (Istanbul, Ankara, Izmir, Antalya)"),
):
    """
    Return latest aggregated context snapshot.

    Partial success:
      - If one source fails but another succeeds -> 200 with failed list.
      - If all sources fail -> 502.

    Cache:
      - Short TTL Redis cache with cache proof headers.
      - If Redis is not configured, the endpoint still works (cache BYPASS).
    """
    start = time.perf_counter()

    settings = get_settings()
    redis = getattr(request.app.state, "redis", None)
    cache_key = _context_cache_key(request)

    # Cache read (only if Redis exists and refresh is false)
    if (redis is not None) and (not refresh):
        cached = await get_json(redis, cache_key)
        if cached is not None:
            inc_cache_hit()
            data = cached.get("data")
            response = JSONResponse(ok(request, data), status_code=200)
            response.headers["X-Cache"] = "HIT"
            response.headers["X-Cache-Key"] = cache_key
            response.headers["Cache-Control"] = f"public, max-age={settings.cache_ttl_seconds}"
            compute_ms = int((time.perf_counter() - start) * 1000)
            response.headers["X-Compute-Time-ms"] = str(compute_ms)
            return response

    inc_cache_miss()

    # Build fresh snapshot
    data = await build_context_snapshot(debug=debug, city=city)

    # All failed -> 502 (do NOT cache failures)
    if len(data.get("sources_ok") or []) == 0:
        payload, status = err(
            request,
            code="UPSTREAM_FAILED",
            message="All context sources failed",
            status_code=502,
            details={
                "sources_failed": data.get("sources_failed"),
                "sources_skipped": data.get("sources_skipped"),
            },
        )
        return JSONResponse(payload, status_code=status)

    # Cache write (only if Redis exists)
    if redis is not None:
        await set_json(redis, cache_key, {"data": data}, ttl_seconds=settings.cache_ttl_seconds)

    response = JSONResponse(ok(request, data), status_code=200)
    response.headers["X-Cache"] = "MISS" if redis is not None else "BYPASS"
    response.headers["X-Cache-Key"] = cache_key
    response.headers["Cache-Control"] = f"public, max-age={settings.cache_ttl_seconds}"
    compute_ms = int((time.perf_counter() - start) * 1000)
    response.headers["X-Compute-Time-ms"] = str(compute_ms)
    return response


@router.get("/context/health")
async def get_context_health(request: Request):
    """
    Return context health analysis with freshness, anomalies, and summary.
    
    This endpoint analyzes the current context to provide:
    - Data freshness (how old each source is)
    - Anomaly detection (spikes, risks, unusual patterns)
    - Context summary (risk level, energy level, focus score)
    """
    start = time.perf_counter()
    
    # Get latest context
    context = await build_context_snapshot(debug=False)
    
    # Calculate freshness (minutes since update)
    now = datetime.now(timezone.utc)
    freshness_data: dict[str, Any] = {}
    freshness_raw = context.get("freshness", {})
    
    for key, timestamp_str in freshness_raw.items():
        try:
            # Parse ISO timestamp
            ts = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
            age_minutes = (now - ts).total_seconds() / 60
            source_name = key.replace("_updated_at", "")
            freshness_data[source_name] = {
                "last_updated": timestamp_str,
                "age_minutes": round(age_minutes, 1),
                "status": "fresh" if age_minutes < 10 else "stale" if age_minutes < 30 else "old"
            }
        except (ValueError, AttributeError):
            pass
    
    # Detect anomalies
    anomalies: list[dict[str, Any]] = []
    
    # GitHub issues spike
    github = context.get("github")
    if github and github.get("open_issues"):
        issue_count = github.get("open_issues", 0)
        if issue_count > 20:  # Simple threshold
            anomalies.append({
                "source": "github",
                "type": "spike",
                "message": f"High number of open issues: {issue_count}",
                "severity": "warning" if issue_count < 50 else "critical",
            })
    
    # Weather risk detection
    weather = context.get("weather")
    if weather:
        condition = (weather.get("condition") or "").lower()
        if "rain" in condition or "storm" in condition:
            anomalies.append({
                "source": "weather",
                "type": "risk",
                "message": f"Weather risk: {condition.title()} expected",
                "severity": "warning" if "rain" in condition else "critical",
            })
        elif "snow" in condition:
            anomalies.append({
                "source": "weather",
                "type": "risk",
                "message": f"Weather risk: {condition.title()} expected",
                "severity": "critical",
            })
    
    # Exchange volatility (if rates changed significantly)
    exchange = context.get("exchange")
    if exchange and exchange.get("rates"):
        rates = exchange.get("rates", {})
        usd_rate = rates.get("USD", 0)
        eur_rate = rates.get("EUR", 0)
        
        # Simple volatility check (would be better with historical data)
        if usd_rate > 35 or eur_rate > 38:  # Example thresholds for TRY
            anomalies.append({
                "source": "exchange",
                "type": "volatility",
                "message": f"Exchange rates high: USD={usd_rate:.2f}, EUR={eur_rate:.2f}",
                "severity": "info",
            })
    
    # Calculate context summary
    risk_level = "low"
    if len([a for a in anomalies if a["severity"] == "critical"]) > 0:
        risk_level = "high"
    elif len([a for a in anomalies if a["severity"] == "warning"]) > 0:
        risk_level = "medium"
    
    # Energy level based on weather
    energy_level = "medium"
    if weather:
        temp = weather.get("temp_c", 20)
        condition = (weather.get("condition") or "").lower()
        if "sunny" in condition or "clear" in condition:
            energy_level = "high"
        elif temp < 5 or temp > 35 or "rain" in condition or "storm" in condition:
            energy_level = "low"
    
    # Focus score (0-1): higher = better focus conditions
    focus_score = 0.7  # Default
    if risk_level == "low" and energy_level == "high":
        focus_score = 0.9
    elif risk_level == "high" or energy_level == "low":
        focus_score = 0.4
    
    summary = {
        "risk_level": risk_level,
        "energy_level": energy_level,
        "focus_score": round(focus_score, 2),
        "overall_health": "good" if focus_score > 0.7 else "fair" if focus_score > 0.5 else "poor"
    }
    
    data = {
        "context_id": context.get("context_id"),
        "observed_at": context.get("observed_at"),
        "freshness": freshness_data,
        "anomalies": anomalies,
        "anomaly_count": len(anomalies),
        "summary": summary,
        "sources_status": {
            "ok": context.get("sources_ok", []),
            "failed": [s["source"] for s in context.get("sources_failed", [])],
            "skipped": [s["source"] for s in context.get("sources_skipped", [])],
        }
    }
    
    response = JSONResponse(ok(request, data), status_code=200)
    compute_ms = int((time.perf_counter() - start) * 1000)
    response.headers["X-Compute-Time-ms"] = str(compute_ms)
    return response
