from __future__ import annotations

import time
from datetime import datetime, timedelta, timezone
import random
from typing import Literal, Optional, Any

from fastapi import APIRouter, Query, Request
from fastapi.responses import JSONResponse
from redis.asyncio import Redis

from app.cache import (
    cache_key_mission_load,
    cache_key_priority_distribution,
    cache_key_category_breakdown,
    get_json,
    set_json,
)
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
    """
    Deterministic series generator for mission load report.
    Compute is bounded but non-trivial to support cache proof demos.
    """
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


def _compute_priority_distribution(*, window: str, buckets: int, seed: int) -> dict[str, Any]:
    """
    Compute-heavy-ish histogram over synthetic priorities.
    buckets: number of histogram bins, e.g. 10/50/100
    """
    rng = random.Random(seed)

    # Work size depends on window to make 30d typically heavier than 7d.
    n = 140_000 if window == "30d" else 90_000
    hist = [0] * buckets

    # bounded work to keep endpoint safe
    extra_work = 700 if window == "30d" else 450

    for _ in range(n):
        p = rng.random()  # 0..1
        idx = int(p * buckets)
        if idx >= buckets:
            idx = buckets - 1
        hist[idx] += 1

        # small deterministic workload
        acc = 0
        for _ in range(extra_work // 70):
            acc ^= rng.randint(0, 2**31 - 1)

    bins = []
    for i, c in enumerate(hist):
        lo = i / buckets
        hi = (i + 1) / buckets
        bins.append({"range": [lo, hi], "count": c})

    top_bins = sorted(bins, key=lambda x: x["count"], reverse=True)[:10]

    return {
        "total_samples": n,
        "buckets": buckets,
        "bins": bins,
        "top_bins": top_bins,
    }


def _compute_category_breakdown(*, window: str, seed: int, top_n: int) -> dict[str, Any]:
    """
    Compute-heavy-ish aggregation over synthetic categories.
    Returns top_n by count with avg_priority + avg_energy.
    """
    rng = random.Random(seed)

    categories = ["bugfix", "research", "meeting", "admin", "study", "health", "coding", "review"]
    n = 140_000 if window == "30d" else 90_000

    stats: dict[str, dict[str, float]] = {
        c: {"count": 0.0, "sum_priority": 0.0, "sum_energy": 0.0} for c in categories
    }

    extra_work = 800 if window == "30d" else 520

    for _ in range(n):
        c = rng.choice(categories)
        p = rng.random()
        e = rng.random()

        s = stats[c]
        s["count"] += 1.0
        s["sum_priority"] += p
        s["sum_energy"] += e

        # deterministic extra work (bounded)
        acc = 0
        for _ in range(extra_work // 80):
            acc ^= rng.randint(0, 2**31 - 1)

    rows = []
    for c, s in stats.items():
        cnt = int(s["count"])
        if cnt <= 0:
            continue
        rows.append(
            {
                "category": c,
                "count": cnt,
                "avg_priority": round(s["sum_priority"] / cnt, 4),
                "avg_energy": round(s["sum_energy"] / cnt, 4),
            }
        )

    rows.sort(key=lambda r: r["count"], reverse=True)

    return {
        "total_samples": n,
        "top_n": top_n,
        "items": rows[:top_n],
    }


# (Optional legacy route - kept as-is; not required for #105)
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
    seed: Optional[int] = Query(None, description="Deterministic seed (enables caching)"),
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


@router.get("/reports/priority-distribution")
async def priority_distribution(
    request: Request,
    window: str = Query("30d"),
    buckets: int = Query(50, ge=5, le=200, description="Histogram bucket count (e.g., 10/50/100)"),
    seed: Optional[int] = Query(None, description="Deterministic seed (enables caching)"),
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
    cache_key = cache_key_priority_distribution(window=window, buckets=buckets, seed=used_seed)

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
        computed = _compute_priority_distribution(window=window, buckets=buckets, seed=used_seed)
        data = {
            "window": window,
            "seed": used_seed if cache_enabled else None,
            "generated_at": _now_iso(),
            **computed,
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


@router.get("/reports/category-breakdown")
async def category_breakdown(
    request: Request,
    window: str = Query("30d"),
    top_n: int = Query(10, ge=3, le=50, description="Return top N categories"),
    seed: Optional[int] = Query(None, description="Deterministic seed (enables caching)"),
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
    cache_key = cache_key_category_breakdown(window=window, seed=used_seed, top_n=top_n)

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
        computed = _compute_category_breakdown(window=window, seed=used_seed, top_n=top_n)
        data = {
            "window": window,
            "seed": used_seed if cache_enabled else None,
            "generated_at": _now_iso(),
            **computed,
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
