from __future__ import annotations

from fastapi.responses import JSONResponse
from fastapi import APIRouter, Request

from app.http_envelope import err

router = APIRouter()


@router.get("/context")
async def get_context(request: Request):
    payload, status = err(
        request,
        code="NOT_FOUND",
        message="No context available yet",
        status_code=404,
        details={"hint": "Context ingestion is not implemented in sprint 1."},
    )
    return JSONResponse(payload, status_code=status)
