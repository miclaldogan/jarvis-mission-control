from __future__ import annotations

from fastapi import APIRouter, Query, Request
from fastapi.responses import JSONResponse

from app.http_envelope import err, ok
from app.services.context import build_context_snapshot
from app.cache import cache_get, cache_set


router = APIRouter()


@router.get("/context")
async def get_context(request: Request, debug: bool = Query(False)):
    """
    Return latest aggregated context snapshot.

    Partial success:
      - If one source fails but another succeeds -> 200 with failed list.
      - If all sources fail -> 502.

    Cache:
      - Short TTL cache for non-debug requests.
    """
    cache_key = "context:v1"

    # 1) Cache READ (only when debug is false)
    if not debug:
        cached = cache_get(cache_key)
        if cached is not None:
            cached["cache"] = "HIT"
            return JSONResponse(ok(request, cached), status_code=200)

    # 2) Build fresh snapshot
    data = await build_context_snapshot(debug=debug)

    # 3) All failed -> 502 (do NOT cache failures)
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

    # 4) Cache WRITE (only when debug is false)
    if not debug:
        data_to_cache = dict(data)  # shallow copy
        data_to_cache.pop("cache", None)  # just in case
        cache_set(cache_key, data_to_cache)
        data["cache"] = "MISS"
    else:
        data["cache"] = "BYPASS"

    return JSONResponse(ok(request, data), status_code=200)
