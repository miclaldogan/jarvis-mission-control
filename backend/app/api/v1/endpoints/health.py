from __future__ import annotations

import time
from datetime import datetime, timezone

from fastapi import APIRouter, Request

from app.http_envelope import ok
from app.settings import get_settings

router = APIRouter()

# Track startup time for uptime calculation
_startup_time = time.time()


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


async def _check_redis(request: Request) -> str:
    """Check Redis connectivity. Returns 'connected' or 'disconnected'."""
    try:
        redis = getattr(request.app.state, "redis", None)
        if redis is not None:
            await redis.ping()
            return "connected"
        return "disconnected"
    except Exception:
        return "disconnected"


@router.get("/health")
async def health(request: Request):
    settings = get_settings()
    redis_status = await _check_redis(request)
    uptime_seconds = int(time.time() - _startup_time)
    
    return ok(
        request,
        {
            "status": "ok",
            "service": "backend",
            "version": settings.app_version,
            "time": _now_iso(),
            "redis": redis_status,
            "uptime": uptime_seconds,
        },
    )
