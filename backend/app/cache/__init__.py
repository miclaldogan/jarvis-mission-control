import os
import json
from typing import Any, Optional

import redis

# --- Redis connection ---
REDIS_URL = os.getenv("REDIS_URL")
DEFAULT_TTL = int(os.getenv("CACHE_TTL_SECONDS", "120"))

_redis: Optional[redis.Redis] = None


def get_redis() -> Optional[redis.Redis]:
    """
    Lazy Redis client. If REDIS_URL is not set, caching is disabled (graceful no-op).
    """
    global _redis
    if _redis is None and REDIS_URL:
        _redis = redis.from_url(REDIS_URL, decode_responses=True)
    return _redis


# --- Generic JSON helpers used by other modules (e.g., report.py) ---
def get_json(key: str) -> Optional[Any]:
    r = get_redis()
    if not r:
        return None
    val = r.get(key)
    return json.loads(val) if val else None


def set_json(key: str, value: Any, ttl: int = DEFAULT_TTL) -> None:
    r = get_redis()
    if not r:
        return
    r.setex(key, ttl, json.dumps(value))


# --- Key builders expected by report.py ---
def cache_key_mission_load(window: str, bucket: str) -> str:
    return f"report:mission-load:v1:window={window}:bucket={bucket}"


# --- Compatibility exports for context caching module (optional) ---
def cache_get(key: str):
    return get_json(key)


def cache_set(key: str, value: dict, ttl: int = DEFAULT_TTL):
    return set_json(key, value, ttl=ttl)

def cache_key_synthetic_tasks(n: int, seed: int) -> str:
    return f"synthetic:tasks:v1:n={n}:seed={seed}"
