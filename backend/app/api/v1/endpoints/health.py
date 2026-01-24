from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Request
from redis.asyncio import Redis

from app.http_envelope import ok
from app.settings import get_settings

router = APIRouter()


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


async def _check_redis(redis: Redis) -> dict[str, Any]:
    """Check Redis connectivity and health."""
    try:
        await asyncio.wait_for(redis.ping(), timeout=2.0)
        return {"status": "healthy", "latency_ms": "< 2000"}
    except asyncio.TimeoutError:
        return {"status": "timeout", "error": "Redis ping timeout"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}


async def _check_weather_api() -> dict[str, Any]:
    """Check weather API availability (graceful degradation)."""
    try:
        # We don't actually call external API here to avoid rate limits
        # Just indicate that the service can handle failures gracefully
        return {"status": "not_checked", "note": "Graceful degradation enabled"}
    except Exception as e:
        return {"status": "degraded", "error": str(e)}


async def _check_github_api() -> dict[str, Any]:
    """Check GitHub API availability (graceful degradation)."""
    try:
        return {"status": "not_checked", "note": "Graceful degradation enabled"}
    except Exception as e:
        return {"status": "degraded", "error": str(e)}


@router.get("/health")
async def health(request: Request):
    """
    Health check endpoint with dependency status.
    
    Returns overall system health and individual dependency checks.
    Useful for load balancers, monitoring systems, and debugging.
    """
    settings = get_settings()
    redis: Redis = request.app.state.redis
    
    # Run all checks concurrently
    redis_health, weather_health, github_health = await asyncio.gather(
        _check_redis(redis),
        _check_weather_api(),
        _check_github_api(),
        return_exceptions=True
    )
    
    # Handle exceptions in health checks
    if isinstance(redis_health, Exception):
        redis_health = {"status": "error", "error": str(redis_health)}
    if isinstance(weather_health, Exception):
        weather_health = {"status": "error", "error": str(weather_health)}
    if isinstance(github_health, Exception):
        github_health = {"status": "error", "error": str(github_health)}
    
    # Determine overall status
    critical_deps_healthy = redis_health.get("status") in ["healthy", "not_checked"]
    overall_status = "healthy" if critical_deps_healthy else "degraded"
    
    return ok(
        request,
        {
            "status": overall_status,
            "service": "backend",
            "version": settings.app_version,
            "time": _now_iso(),
            "dependencies": {
                "redis": redis_health,
                "weather_api": weather_health,
                "github_api": github_health,
            },
            "features": {
                "graceful_degradation": True,
                "request_tracking": True,
                "caching": True,
            },
        },
    )
