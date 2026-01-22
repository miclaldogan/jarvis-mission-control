from __future__ import annotations

import time

from fastapi import APIRouter, Query, Request
from fastapi.responses import JSONResponse
from redis.asyncio import Redis

from app.cache import get_json, set_json
from app.http_envelope import err, ok
from app.metrics import inc_cache_hit, inc_cache_miss
from app.settings import get_settings
from app.services.context import build_context_snapshot


router = APIRouter()


def _context_cache_key(request: Request) -> str:
    # Include *all* query params (incl. debug) in the key.
    # Sort for stability so ordering differences don't cause cache misses.
    items = sorted(request.query_params.multi_items())
    query = "&".join([f"{k}={v}" for k, v in items])
    return f"cache:v1:context:path={request.url.path}:q={query}"


@router.get("/context")
async def get_context(request: Request, debug: bool = Query(False)):
    """
    Return latest aggregated context snapshot.

    Partial success:
      - If one source fails but another succeeds -> 200 with failed list.
      - If all sources fail -> 502.

    Cache:
      - Short TTL Redis cache with cache proof headers.
    """
    start = time.perf_counter()

    settings = get_settings()
    redis: Redis = request.app.state.redis
    cache_key = _context_cache_key(request)

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
    data = await build_context_snapshot(debug=debug)

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

    await set_json(redis, cache_key, {"data": data}, ttl_seconds=settings.cache_ttl_seconds)

    response = JSONResponse(ok(request, data), status_code=200)
    response.headers["X-Cache"] = "MISS"
    response.headers["X-Cache-Key"] = cache_key
    response.headers["Cache-Control"] = f"public, max-age={settings.cache_ttl_seconds}"
    compute_ms = int((time.perf_counter() - start) * 1000)
    response.headers["X-Compute-Time-ms"] = str(compute_ms)
    return response
