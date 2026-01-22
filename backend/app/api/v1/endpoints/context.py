from __future__ import annotations

import os
import time

from fastapi import APIRouter, Query, Request
from fastapi.responses import JSONResponse

from app.http_envelope import err, ok
from app.services.context import build_context_snapshot
from app.cache import get_json, set_json  # in-memory cache (works without redis)

router = APIRouter()


@router.get("/context")
async def get_context(
    request: Request,
    debug: bool = Query(False),
    refresh: bool = Query(False),
):
    """
    Return latest aggregated context snapshot.

    Cache:
      - Short TTL cache for GET /api/v1/context
      - Cache key varies by debug flag
      - refresh=true bypasses cache

    Partial success:
      - If one source fails but another succeeds -> 200 with failed list.
      - If all sources fail -> 502.
    """
    start = time.perf_counter()

    ttl_seconds = int(os.getenv("CACHE_TTL_SECONDS", "120"))
    cache_key = f"context:v1:debug={int(debug)}"

    def _headers(x_cache: str, compute_ms: int) -> dict[str, str]:
        return {
            "X-Cache": x_cache,
            "X-Compute-Time-ms": str(compute_ms),
            "X-Cache-Key": cache_key,
            "Cache-Control": f"public, max-age={ttl_seconds}",
        }

    # 1) Try cache unless refresh
    if not refresh:
        cached = get_json(cache_key)
        if cached is not None:
            compute_ms = int((time.perf_counter() - start) * 1000)

            # cached objeyi mutate etmeyelim; response için kopya üretelim
            data = dict(cached)
            data["cache"] = "HIT"

            return JSONResponse(
                ok(request, data),
                status_code=200,
                headers=_headers("HIT", compute_ms),
            )

    # 2) Build snapshot (cache MISS)
    data = await build_context_snapshot(debug=debug)

    if len(data.get("sources_ok") or []) == 0:
        compute_ms = int((time.perf_counter() - start) * 1000)
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
        return JSONResponse(
            payload,
            status_code=status,
            headers=_headers("MISS", compute_ms),
        )

    # 3) Save to cache + return
    compute_ms = int((time.perf_counter() - start) * 1000)

    data["cache"] = "MISS"
    set_json(cache_key, data)  # TTL env var: CACHE_TTL_SECONDS

    return JSONResponse(
        ok(request, data),
        status_code=200,
        headers=_headers("MISS", compute_ms),
    )
