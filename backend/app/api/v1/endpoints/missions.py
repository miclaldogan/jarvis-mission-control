from __future__ import annotations

import time
from typing import Any, Literal, Optional

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from app.http_envelope import ok
from app.services.context import build_context_snapshot
from app.services.missions import generate_missions

router = APIRouter()


class Preferences(BaseModel):
    energy_level: Optional[Literal["low", "medium", "high"]] = None
    time_of_day: Optional[Literal["morning", "afternoon", "evening"]] = None


class MissionsGenerateRequest(BaseModel):
    context: Optional[dict[str, Any]] = None
    preferences: Optional[Preferences] = None
    limit: int = Field(15, ge=1, le=30)
    seed: Optional[int] = None


@router.post("/missions/generate")
async def missions_generate(request: Request, body: MissionsGenerateRequest):
    start = time.perf_counter()

    context = body.context
    if context is None:
        context = await build_context_snapshot(debug=False)

    missions = generate_missions(
        context=context,
        preferences=body.preferences.model_dump() if body.preferences else None,
        limit=body.limit,
        seed=body.seed,
    )

    data = {
        "context": {
            "context_id": context.get("context_id"),
            "observed_at": context.get("observed_at") or context.get("fetched_at"),
        },
        "missions": missions,
    }

    response = JSONResponse(ok(request, data), status_code=200)
    compute_ms = int((time.perf_counter() - start) * 1000)
    response.headers["X-Compute-Time-ms"] = str(compute_ms)
    return response
