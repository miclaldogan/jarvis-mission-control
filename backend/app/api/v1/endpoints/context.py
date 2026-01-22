from __future__ import annotations

from fastapi import APIRouter, Query, Request
from fastapi.responses import JSONResponse

from app.http_envelope import err, ok
from app.services.context import build_context_snapshot

router = APIRouter()

@router.get("/context")
async def get_context(request: Request, debug: bool = Query(False)):
    """
    Return latest aggregated context snapshot.

    Partial success:
      - If one source fails but another succeeds -> 200 with failed list.
      - If all sources fail -> 502.
    """
    data = await build_context_snapshot(debug=debug)

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

    return JSONResponse(ok(request, data), status_code=200)
