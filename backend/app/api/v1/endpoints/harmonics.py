"""System Harmonics Endpoint - Real-time health, risk & energy indices.

Provides the "wow" System Harmonics panel data:
- Source health with freshness tracking
- Anomaly detection flags
- 3 key indices: Stability, Risk, Energy Fit
"""

from __future__ import annotations

import time
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from app.http_envelope import ok
from app.services.context import build_context_snapshot
from app.services.harmonics import compute_harmonics, get_cached_harmonics
from app.metrics import get_cache_stats


router = APIRouter()


@router.get("/system/harmonics")
async def get_system_harmonics(request: Request, refresh: bool = False):
    """Get System Harmonics - health indices, anomalies, source freshness.
    
    Returns:
    - source_health: Per-source status, freshness, TTL
    - anomalies: Detected flags (github_spike, weather_risk, etc.)
    - indices: stability (0-100), risk (0-100), energy_fit (0-100)
    - summary: Overall system health status
    
    Query params:
    - refresh: Force fresh context fetch (default: use cached)
    """
    start = time.perf_counter()
    
    # Check cache first (unless refresh requested)
    if not refresh:
        cached = get_cached_harmonics()
        if cached is not None:
            response = JSONResponse(ok(request, cached), status_code=200)
            response.headers["X-Harmonics-Cache"] = "HIT"
            compute_ms = int((time.perf_counter() - start) * 1000)
            response.headers["X-Compute-Time-ms"] = str(compute_ms)
            return response
    
    # Build fresh context
    context = await build_context_snapshot(debug=False)
    
    # Get cache stats for stability calculation
    cache_stats = get_cache_stats()
    
    # Compute harmonics
    harmonics = await compute_harmonics(context, cache_stats)
    
    response = JSONResponse(ok(request, harmonics), status_code=200)
    response.headers["X-Harmonics-Cache"] = "MISS"
    compute_ms = int((time.perf_counter() - start) * 1000)
    response.headers["X-Compute-Time-ms"] = str(compute_ms)
    return response


@router.get("/system/harmonics/history")
async def get_harmonics_history(request: Request, limit: int = 10):
    """Get historical harmonics data for trending graphs.
    
    Returns last N harmonics snapshots with timestamps.
    """
    from app.services.harmonics import _context_history
    
    history = list(_context_history)[-limit:]
    
    # Compute summary for each historical point
    history_data = []
    for h in history:
        history_data.append({
            "timestamp": h.get("timestamp"),
            "github_issues": h.get("github_issues", 0),
            "calendar_events": h.get("calendar_events", 0),
            "weather_condition": h.get("weather_condition"),
            "weather_temp": h.get("weather_temp"),
        })
    
    return JSONResponse(ok(request, {
        "history": history_data,
        "count": len(history_data),
    }), status_code=200)
