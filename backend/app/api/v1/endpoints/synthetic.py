from __future__ import annotations

import hashlib
import json
import random
import time
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Query, Request
from fastapi.responses import JSONResponse
from redis.asyncio import Redis

from app.cache import cache_key_synthetic_tasks, get_json, set_json
from app.http_envelope import err, ok
from app.metrics import inc_cache_hit, inc_cache_miss, inc_synthetic_generated, record_compute_time
from app.rate_limit import fixed_window_allow, synthetic_client_id, synthetic_rate_limit_key
from app.settings import get_settings
from app.db.connection import init_db, get_db_context

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
    """Generate realistic synthetic tasks with deterministic randomness."""
    rng = random.Random(seed)
    
    # Categories and templates for realistic tasks
    categories = ["SYSTEM", "RECON", "DEV", "PERSONAL", "HEALTH", "LEARNING", "WORK"]
    priorities = ["CRITICAL", "HIGH", "NORMAL", "LOW"]
    energy_levels = ["low", "medium", "high"]
    
    templates = {
        "SYSTEM": [
            "Update {} dependencies",
            "Patch security vulnerability in {}",
            "Monitor {} performance",
            "Configure {} firewall rules",
            "Backup {} database",
        ],
        "RECON": [
            "Research {} competitors",
            "Analyze {} market trends",
            "Survey {} user feedback",
            "Review {} documentation",
            "Investigate {} incident",
        ],
        "DEV": [
            "Fix bug #{}",
            "Implement feature #{}",
            "Review PR #{}",
            "Refactor {} module",
            "Write tests for {}",
            "Deploy {} to staging",
            "Debug {} performance issue",
        ],
        "PERSONAL": [
            "Call {} about {}",
            "Buy {} from {}",
            "Plan {} trip",
            "Schedule {} appointment",
            "Organize {} files",
        ],
        "HEALTH": [
            "Morning {} workout",
            "Prepare {} meal",
            "Take {} break",
            "Stretch for {} minutes",
            "Drink {} glasses of water",
        ],
        "LEARNING": [
            "Read chapter {} of {}",
            "Complete {} course module",
            "Practice {} for {} minutes",
            "Watch {} tutorial",
            "Study {} concepts",
        ],
        "WORK": [
            "Attend {} meeting",
            "Write {} report",
            "Send {} email",
            "Update {} spreadsheet",
            "Prepare {} presentation",
        ],
    }
    
    # Names/subjects for templates
    subjects = [
        "frontend", "backend", "API", "database", "cache", "auth", "UI", "UX",
        "security", "payment", "notification", "search", "analytics", "logging",
        "John", "Sarah", "team", "client", "manager", "vendor",
        "quarterly", "monthly", "weekly", "daily", "annual",
    ]
    
    size = min(sample_size, n)
    out: list[dict] = []
    
    for i in range(1, size + 1):
        category = rng.choice(categories)
        template = rng.choice(templates[category])
        
        # Fill template with random subjects or numbers
        placeholders = template.count("{}")
        if placeholders == 2:
            title = template.format(rng.choice(subjects), rng.choice(subjects))
        elif placeholders == 1:
            if "#" in template or "minutes" in template or "glasses" in template or "chapter" in template:
                title = template.format(rng.randint(1, 100))
            else:
                title = template.format(rng.choice(subjects))
        else:
            title = template
        
        # Deterministic deadline (0-7 days from seed base)
        deadline_days = rng.randint(0, 7)
        
        out.append(
            {
                "id": f"tsk_{i:06d}",
                "title": title,
                "category": category,
                "priority": rng.choice(priorities),
                "energy_cost": rng.choice(energy_levels),
                "deadline_days": deadline_days,
                "score": round(rng.random(), 2),
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
    redis: Optional[Redis] = getattr(request.app.state, "redis", None)

    limit = settings.synthetic_ratelimit_per_min
    window_seconds = settings.synthetic_ratelimit_window_seconds
    if (redis is not None) and limit > 0 and window_seconds > 0:
        client_id = synthetic_client_id(
            x_forwarded_for=request.headers.get("X-Forwarded-For"),
            client_host=getattr(request.client, "host", None),
            x_api_key=request.headers.get("X-Api-Key"),
        )
        rate_key = synthetic_rate_limit_key(client_id=client_id, window_seconds=window_seconds)
        allowed, _count, retry_after = await fixed_window_allow(
            redis=redis,
            key=rate_key,
            limit=limit,
            window_seconds=window_seconds,
        )
        if not allowed:
            payload, status = err(
                request,
                code="RATE_LIMITED",
                message="Too many requests",
                status_code=429,
                details={"limit": limit, "window_seconds": window_seconds},
            )
            response = JSONResponse(payload, status_code=status)
            response.headers["Retry-After"] = str(retry_after)
            return response

    sample_size = 50
    cache_enabled = seed is not None
    used_seed = seed if seed is not None else random.randint(1, 2**31 - 1)

    cache_possible = cache_enabled and (redis is not None)

    start = time.perf_counter()
    cache_key = cache_key_synthetic_tasks(n=n, seed=used_seed, sample_size=sample_size)

    cached = None
    if cache_possible:
        cached = await get_json(redis, cache_key)

    if cached is not None:
        inc_cache_hit()
        data = cached["data"]
        response = JSONResponse(
            ok(request, data, extra_meta={"total": n}),
            status_code=200,
        )
        response.headers["X-Cache"] = "HIT"
        response.headers["X-Cache-Key"] = cache_key
        response.headers["Cache-Control"] = f"public, max-age={settings.cache_ttl_seconds}"
    else:
        if cache_possible:
            inc_cache_miss()
        inc_synthetic_generated(n)
        sample = _make_sample(n=n, seed=used_seed, sample_size=sample_size)
        data = {
            "n": n,
            "seed": used_seed if cache_enabled else None,
            "sample": sample,
            "preview_hash": _preview_hash(n=n, seed=used_seed, sample=sample),
        }

        if cache_possible:
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
        response.headers["X-Cache"] = "MISS" if cache_possible else "BYPASS"
        if cache_possible:
            response.headers["X-Cache-Key"] = cache_key
            response.headers["Cache-Control"] = f"public, max-age={settings.cache_ttl_seconds}"

    compute_ms = int((time.perf_counter() - start) * 1000)
    response.headers["X-Compute-Time-ms"] = str(compute_ms)
    record_compute_time(compute_ms)

    return response


@router.post("/synthetic/tasks/persist")
async def synthetic_tasks_persist(
    request: Request,
    n: int = Query(..., description="Number of tasks to persist (100000 or 1000000)"),
    seed: Optional[int] = Query(None, description="Deterministic seed"),
):
    """Persist N synthetic tasks into SQLite for Simulation Lab.

    Writes to the `synthetic_tasks` table (not missions) so Mission Control UI isn't polluted.
    """
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
    redis: Optional[Redis] = getattr(request.app.state, "redis", None)

    # Optional rate limit (only if Redis is available)
    limit = settings.synthetic_ratelimit_per_min
    window_seconds = settings.synthetic_ratelimit_window_seconds
    if (redis is not None) and limit > 0 and window_seconds > 0:
        client_id = synthetic_client_id(
            x_forwarded_for=request.headers.get("X-Forwarded-For"),
            client_host=getattr(request.client, "host", None),
            x_api_key=request.headers.get("X-Api-Key"),
        )
        rate_key = synthetic_rate_limit_key(client_id=client_id, window_seconds=window_seconds)
        allowed, _count, retry_after = await fixed_window_allow(
            redis=redis,
            key=rate_key,
            limit=limit,
            window_seconds=window_seconds,
        )
        if not allowed:
            payload, status = err(
                request,
                code="RATE_LIMITED",
                message="Too many requests",
                status_code=429,
                details={"limit": limit, "window_seconds": window_seconds},
            )
            response = JSONResponse(payload, status_code=status)
            response.headers["Retry-After"] = str(retry_after)
            return response

    used_seed = seed if seed is not None else random.randint(1, 2**31 - 1)
    start = time.perf_counter()
    inc_synthetic_generated(n)

    # Ensure schema exists (including synthetic_tasks)
    init_db()

    rng = random.Random(used_seed)
    categories = ["SYSTEM", "RECON", "DEV", "PERSONAL", "HEALTH", "LEARNING", "WORK"]
    priorities = ["CRITICAL", "HIGH", "NORMAL", "LOW"]
    energy_levels = ["low", "medium", "high"]
    templates = {
        "SYSTEM": [
            "Update {} dependencies",
            "Patch security vulnerability in {}",
            "Monitor {} performance",
            "Configure {} firewall rules",
            "Backup {} database",
        ],
        "RECON": [
            "Research {} competitors",
            "Analyze {} market trends",
            "Survey {} user feedback",
            "Review {} documentation",
            "Investigate {} incident",
        ],
        "DEV": [
            "Fix bug #{}",
            "Implement feature #{}",
            "Review PR #{}",
            "Refactor {} module",
            "Write tests for {}",
            "Deploy {} to staging",
            "Debug {} performance issue",
        ],
        "PERSONAL": [
            "Call {} about {}",
            "Buy {} from {}",
            "Plan {} trip",
            "Schedule {} appointment",
            "Organize {} files",
        ],
        "HEALTH": [
            "Morning {} workout",
            "Prepare {} meal",
            "Take {} break",
            "Stretch for {} minutes",
            "Drink {} glasses of water",
        ],
        "LEARNING": [
            "Read chapter {} of {}",
            "Complete {} course module",
            "Practice {} for {} minutes",
            "Watch {} tutorial",
            "Study {} concepts",
        ],
        "WORK": [
            "Attend {} meeting",
            "Write {} report",
            "Send {} email",
            "Update {} spreadsheet",
            "Prepare {} presentation",
        ],
    }
    subjects = [
        "frontend",
        "backend",
        "API",
        "database",
        "cache",
        "auth",
        "UI",
        "UX",
        "security",
        "payment",
        "notification",
        "search",
        "analytics",
        "logging",
        "John",
        "Sarah",
        "team",
        "client",
        "manager",
        "vendor",
        "quarterly",
        "monthly",
        "weekly",
        "daily",
        "annual",
    ]

    created_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    def make_row(i: int) -> tuple:
        category = rng.choice(categories)
        template = rng.choice(templates[category])
        placeholders = template.count("{}")
        if placeholders == 2:
            title = template.format(rng.choice(subjects), rng.choice(subjects))
        elif placeholders == 1:
            if "#" in template or "minutes" in template or "glasses" in template or "chapter" in template:
                title = template.format(rng.randint(1, 100))
            else:
                title = template.format(rng.choice(subjects))
        else:
            title = template

        priority = rng.choice(priorities)
        energy_cost = rng.choice(energy_levels)
        deadline_days = rng.randint(0, 7)
        score = round(rng.random(), 2)
        task_id = f"syn_{used_seed}_{i:07d}"
        return (task_id, title, category, priority, energy_cost, deadline_days, score, used_seed, created_at)

    chunk_size = 5000
    inserted = 0

    with get_db_context() as conn:
        try:
            conn.execute("PRAGMA synchronous = NORMAL")
        except Exception:
            pass

        before = conn.total_changes
        for start_i in range(1, n + 1, chunk_size):
            end_i = min(n, start_i + chunk_size - 1)
            rows = [make_row(i) for i in range(start_i, end_i + 1)]
            conn.executemany(
                """
                INSERT OR IGNORE INTO synthetic_tasks (
                    id, title, category, priority, energy_cost, deadline_days, score, seed, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                rows,
            )
            conn.commit()
        after = conn.total_changes
        inserted = max(0, after - before)

    compute_ms = int((time.perf_counter() - start) * 1000)
    record_compute_time(compute_ms)

    data = {"n": n, "seed": used_seed, "inserted": inserted, "table": "synthetic_tasks"}
    response = JSONResponse(ok(request, data, extra_meta={"total": n}), status_code=200)
    response.headers["X-Compute-Time-ms"] = str(compute_ms)
    return response
