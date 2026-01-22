import os
import json
import redis
from typing import Optional

REDIS_URL = os.getenv("REDIS_URL")
DEFAULT_TTL = int(os.getenv("CACHE_TTL_SECONDS", "120"))

_redis: Optional[redis.Redis] = None


def get_redis() -> Optional[redis.Redis]:
    global _redis
    if _redis is None and REDIS_URL:
        _redis = redis.from_url(REDIS_URL, decode_responses=True)
    return _redis


def cache_get(key: str):
    r = get_redis()
    if not r:
        return None
    val = r.get(key)
    return json.loads(val) if val else None


def cache_set(key: str, value: dict, ttl: int = DEFAULT_TTL):
    r = get_redis()
    if not r:
        return
    r.setex(key, ttl, json.dumps(value))
