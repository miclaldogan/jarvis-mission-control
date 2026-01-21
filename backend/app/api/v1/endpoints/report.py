from __future__ import annotations

import time
from typing import Literal

from fastapi import APIRouter, Query, Request
from fastapi.responses import JSONResponse

from app.http_envelope import err, ok
from app.settings import get_settings

router = APIRouter()


@router.get("/report")
async def report(
    request: Request,
    window: str = Query("30d"),
    bucket: Literal["hour", "day"] = Query("hour"),
):
    if window not in ("7d", "30d"):
        payload, status = err(
            request,
            code="INVALID_PARAMS",
            message="window must be 7d or 30d",
            status_code=400,
            details={"window": window},
        )
        return JSONResponse(payload, status_code=status)

    start = time.perf_counter()

    _ = get_settings()  # keeps version/env available for future use

    data = {
        "context": {
            "context_id": "ctx_placeholder",
            "observed_at": "2026-01-21T09:00:00Z",
            "weather": {"city": "Istanbul", "temp_c": 7, "condition": "rain"},
            "github": {"open_issues": 12, "open_prs": 4},
            "news": [{"title": "Example headline", "url": "https://example.com"}],
        },
        "missions": [
            {
                "id": "msn_001",
                "title": "Bugün yağmur var: dışarı planını 18:00 sonrası yap",
                "priority": "P2",
                "status": "open",
                "due_at": None,
                "tags": ["weather", "planning"],
                "why": "Yağmur 14:00–17:00 arası yoğun görünüyor.",
                "actions": [
                    {"label": "Hava detayına git", "type": "link", "target": "/ui/context#weather"}
                ],
                "evidence": {"sources": ["weather"], "confidence": 0.78},
            }
        ],
        "metrics": {
            "window": window,
            "bucket": bucket,
            "series": [
                {"ts": "2026-01-20T00:00:00Z", "missions_total": 12, "missions_completed": 5}
            ],
        },
    }

    response = JSONResponse(ok(request, data), status_code=200)

    compute_ms = int((time.perf_counter() - start) * 1000)
    response.headers["X-Compute-Time-ms"] = str(compute_ms)

    return response
