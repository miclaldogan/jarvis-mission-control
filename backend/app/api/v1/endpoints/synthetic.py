from __future__ import annotations

import hashlib
import json
import random
import time
from typing import Optional

from fastapi import APIRouter, Query, Request
from fastapi.responses import JSONResponse
from redis.asyncio import Redis

from app.cache import cache_key_synthetic_tasks, get_json, set_json
from app.http_envelope import err, ok
from app.settings import get_settings

router = APIRouter()


def _preview_hash(n: int, seed: int, sample: list[dict]) -> str:
    payload = {
        "n": n,
        "seed": seed,
        "sample": sample,
    }
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return "sha256:" + hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _make_sample(n: int, seed: int, sample_size: int = 50) -> list[dict]:
    rng = random.Random(seed)
    priorities = ["P1", "P2", "P3", "P4"]
    size = min(sample_size, n)
    out: list[dict] = []
    for i in range(1, size + 1):
        out.append(
            {
                "id": f"tsk_{i:06d}",
                "title": f"Synthetic task #{i}",
                "priority": rng.choice(priorities),
            }
        )
    return out


@router.get("/synthetic/tasks")
async def synthetic_tasks(
    request: Request,
    n: int = Query(..., description="Number of tasks (100000 or 1000000)"),
    seed: Optional[int] = Query(None, description="Deterministic seed (enables caching)"),
):
    if n not in (100000, 1000000):
        payload, status = err(
            request,
            code="INVALID_PARAMS",
            message="n must be 100000 or 1000000",
            status_code=400,
            details={"n": n},
        )
        return JSONResponse(payload, status_code=status)

    settings = get_settings()
    redis: Redis = request.app.state.redis

    sample_size = 50
    cache_enabled = seed is not None
    used_seed = seed if seed is not None else random.randint(1, 2**31 - 1)

    start = time.perf_counter()
    cache_key = cache_key_synthetic_tasks(n=n, seed=used_seed, sample_size=sample_size)

    cached = None
    if cache_enabled:
        cached = await get_json(redis, cache_key)

    if cached is not None:
        data = cached["data"]
        response = JSONResponse(
            ok(request, data, extra_meta={"total": n}),
            status_code=200,
        )
        response.headers["X-Cache"] = "HIT"
        response.headers["X-Cache-Key"] = cache_key
        response.headers["Cache-Control"] = f"public, max-age={settings.cache_ttl_seconds}"
    else:
        sample = _make_sample(n=n, seed=used_seed, sample_size=sample_size)
        data = {
            "n": n,
            "seed": used_seed if cache_enabled else None,
            "sample": sample,
            "preview_hash": _preview_hash(n=n, seed=used_seed, sample=sample),
        }

        if cache_enabled:
            await set_json(
                redis,
                cache_key,
                {"data": data},
                ttl_seconds=settings.cache_ttl_seconds,
            )

        response = JSONResponse(
            ok(request, data, extra_meta={"total": n}),
            status_code=200,
        )
        response.headers["X-Cache"] = "MISS"
        if cache_enabled:
            response.headers["X-Cache-Key"] = cache_key
            response.headers["Cache-Control"] = f"public, max-age={settings.cache_ttl_seconds}"

    compute_ms = int((time.perf_counter() - start) * 1000)
    response.headers["X-Compute-Time-ms"] = str(compute_ms)

    return response
