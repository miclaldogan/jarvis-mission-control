from __future__ import annotations

import time
from typing import Optional

from redis.asyncio import Redis


_LOCAL_COUNTERS: dict[str, tuple[int, int]] = {}
# value: (count, expires_at_unix)


def _now_unix() -> int:
    return int(time.time())


def _window_id(now_unix: int, window_seconds: int) -> int:
    return now_unix // window_seconds


def _window_reset_in(now_unix: int, window_seconds: int) -> int:
    wid = _window_id(now_unix, window_seconds)
    reset_at = (wid + 1) * window_seconds
    return max(1, reset_at - now_unix)


def synthetic_client_id(*, x_forwarded_for: Optional[str], client_host: Optional[str], x_api_key: Optional[str]) -> str:
    if x_api_key:
        return f"key:{x_api_key.strip()}"

    ip = ""
    if x_forwarded_for:
        # X-Forwarded-For: client, proxy1, proxy2
        ip = x_forwarded_for.split(",", 1)[0].strip()

    if not ip:
        ip = (client_host or "unknown").strip()

    return f"ip:{ip}"


def synthetic_rate_limit_key(*, client_id: str, window_seconds: int, now_unix: Optional[int] = None) -> str:
    now = _now_unix() if now_unix is None else int(now_unix)
    wid = _window_id(now, window_seconds)
    return f"ratelimit:synthetic:{client_id}:{wid}"


async def fixed_window_allow(
    *,
    redis: Optional[Redis],
    key: str,
    limit: int,
    window_seconds: int,
    now_unix: Optional[int] = None,
) -> tuple[bool, int, int]:
    """Returns (allowed, count, retry_after_seconds).

    Uses Redis if available, otherwise falls back to an in-memory counter.
    """

    now = _now_unix() if now_unix is None else int(now_unix)

    if limit <= 0:
        return True, 0, 0

    if window_seconds <= 0:
        # Defensive: treat invalid window as "no rate limit"
        return True, 0, 0

    if redis is not None:
        try:
            count = int(await redis.incr(key))
            if count == 1:
                await redis.expire(key, window_seconds)

            if count <= limit:
                return True, count, 0

            return False, count, _window_reset_in(now, window_seconds)
        except Exception:
            # Fall back to in-memory below
            pass

    expires_at = now + window_seconds

    stored = _LOCAL_COUNTERS.get(key)
    if stored is None:
        count = 1
        _LOCAL_COUNTERS[key] = (count, expires_at)
    else:
        prev_count, prev_expires_at = stored
        if prev_expires_at <= now:
            count = 1
            _LOCAL_COUNTERS[key] = (count, expires_at)
        else:
            count = prev_count + 1
            _LOCAL_COUNTERS[key] = (count, prev_expires_at)

    if count <= limit:
        return True, count, 0

    return False, count, _window_reset_in(now, window_seconds)
