from __future__ import annotations

import json
import time
from dataclasses import dataclass
from typing import Any, Optional

from redis.asyncio import Redis


@dataclass(frozen=True)
class CacheResult:
    hit: bool
    cache_key: str
    payload: Optional[dict[str, Any]]
    compute_time_ms: int


def cache_key_synthetic_tasks(*, n: int, seed: int, sample_size: int) -> str:
    return f"cache:v1:synthetic_tasks:n={n}:seed={seed}:sample={sample_size}"


def cache_key_report(*, window: str, bucket: str) -> str:
    return f"cache:v1:report:window={window}:bucket={bucket}"


def cache_key_mission_load(*, window: str, bucket: str, seed: int) -> str:
    return f"cache:v1:mission_load:window={window}:bucket={bucket}:seed={seed}"

def cache_key_priority_distribution(*, window: str, buckets: int, seed: int) -> str:
    return f"cache:v1:priority_distribution:window={window}:buckets={buckets}:seed={seed}"


def cache_key_category_breakdown(*, window: str, top_n: int, seed: int) -> str:
    return f"cache:v1:category_breakdown:window={window}:top_n={top_n}:seed={seed}"


# ✅ NEW (Issue #105): Priority distribution cache key
def cache_key_priority_distribution(*, window: str, buckets: int, seed: int) -> str:
    return f"cache:v1:priority_distribution:window={window}:buckets={buckets}:seed={seed}"


# ✅ NEW (Issue #105): Category breakdown cache key
def cache_key_category_breakdown(*, window: str, top_n: int, seed: int) -> str:
    return f"cache:v1:category_breakdown:window={window}:top_n={top_n}:seed={seed}"


async def get_json(redis: Redis, key: str) -> Optional[dict[str, Any]]:
    raw = await redis.get(key)
    if raw is None:
        return None
    return json.loads(raw)


async def set_json(redis: Redis, key: str, value: dict[str, Any], *, ttl_seconds: int) -> None:
    raw = json.dumps(value, separators=(",", ":"), ensure_ascii=False)
    await redis.set(key, raw, ex=ttl_seconds)


def now_ms() -> int:
    return int(time.perf_counter() * 1000)
