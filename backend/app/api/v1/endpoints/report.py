from __future__ import annotations

import time
from datetime import datetime, timedelta, timezone
import random
from typing import Literal

from fastapi import APIRouter, Query, Request
from fastapi.responses import JSONResponse
from redis.asyncio import Redis

from app.cache import cache_key_mission_load, get_json, set_json
from app.http_envelope import err, ok
from app.metrics import inc_cache_hit, inc_cache_miss
from app.settings import get_settings
from app.services.context import build_context_snapshot
from app.services.missions import generate_missions

router = APIRouter()


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _bucket_count(window: str, bucket: str) -> int:
    days = 7 if window == "7d" else 30
    if bucket == "day":
        return days
    return days * 24


def _series_start(window: str) -> datetime:
    days = 7 if window == "7d" else 30
    return datetime.now(timezone.utc) - timedelta(days=days)


def _compute_series(*, window: str, bucket: str, seed: int) -> list[dict[str, int | str]]:
    rng = random.Random(seed)
    count = _bucket_count(window, bucket)
    start = _series_start(window)
    step = timedelta(days=1) if bucket == "day" else timedelta(hours=1)

    out: list[dict[str, int | str]] = []
    base = 10 if window == "7d" else 25

    # A small, bounded amount of work so compute time is non-trivial but safe.
    work_factor = 2000 if bucket == "day" else 400

    for i in range(count):
        ts = (start + step * i).replace(minute=0, second=0, microsecond=0)

        acc = 0
        for _ in range(work_factor):
            acc ^= rng.randint(0, 2**31 - 1)

        missions_total = base + (acc % 30)
        missions_completed = int(missions_total * (0.35 + (acc % 25) / 100.0))
        out.append(
            {
                "ts": ts.isoformat().replace("+00:00", "Z"),
                "missions_total": missions_total,
                "missions_completed": missions_completed,
            }
        )

    return out


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

    context = await build_context_snapshot(debug=False)
    missions = generate_missions(context=context, limit=10, seed=42)
    series = _compute_series(window=window, bucket=bucket, seed=42)

    data = {
        "context": context,
        "missions": missions,
        "metrics": {
            "window": window,
            "bucket": bucket,
            "series": series,
        },
    }

    response = JSONResponse(ok(request, data), status_code=200)

    compute_ms = int((time.perf_counter() - start) * 1000)
    response.headers["X-Compute-Time-ms"] = str(compute_ms)

    return response


@router.get("/reports/mission-load")
async def mission_load(
    request: Request,
    window: str = Query("30d"),
    bucket: Literal["hour", "day"] = Query("hour"),
    seed: int | None = Query(None, description="Deterministic seed (enables caching)"),
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

    settings = get_settings()
    redis: Redis = request.app.state.redis

    cache_enabled = seed is not None
    used_seed = seed if seed is not None else 42

    start = time.perf_counter()
    cache_key = cache_key_mission_load(window=window, bucket=bucket, seed=used_seed)

    cached = None
    if cache_enabled:
        cached = await get_json(redis, cache_key)

    if cached is not None:
        inc_cache_hit()
        data = cached["data"]
        response = JSONResponse(ok(request, data), status_code=200)
        response.headers["X-Cache"] = "HIT"
        response.headers["X-Cache-Key"] = cache_key
        response.headers["Cache-Control"] = f"public, max-age={settings.cache_ttl_seconds}"
    else:
        inc_cache_miss()
        series = _compute_series(window=window, bucket=bucket, seed=used_seed)
        data = {
            "window": window,
            "bucket": bucket,
            "seed": used_seed if cache_enabled else None,
            "generated_at": _now_iso(),
            "series": series,
        }

        if cache_enabled:
            await set_json(redis, cache_key, {"data": data}, ttl_seconds=settings.cache_ttl_seconds)

        response = JSONResponse(ok(request, data), status_code=200)
        response.headers["X-Cache"] = "MISS"
        if cache_enabled:
            response.headers["X-Cache-Key"] = cache_key
            response.headers["Cache-Control"] = f"public, max-age={settings.cache_ttl_seconds}"

    compute_ms = int((time.perf_counter() - start) * 1000)
    response.headers["X-Compute-Time-ms"] = str(compute_ms)
    return response
