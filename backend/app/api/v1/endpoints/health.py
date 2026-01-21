from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Request

from app.http_envelope import ok
from app.settings import get_settings

router = APIRouter()


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


@router.get("/health")
async def health(request: Request):
    settings = get_settings()
    return ok(
        request,
        {
            "status": "ok",
            "service": "backend",
            "version": settings.app_version,
            "time": _now_iso(),
        },
    )
