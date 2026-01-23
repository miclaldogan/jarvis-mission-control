from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest
from redis import Redis


# Ensure `import app...` works regardless of pytest rootdir.
BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))


@pytest.fixture(scope="session")
def redis_url() -> str:
    return os.getenv("REDIS_URL", "redis://localhost:6379/0")


@pytest.fixture(scope="session")
def redis_client(redis_url: str) -> Redis:
    client = Redis.from_url(redis_url, decode_responses=True)
    try:
        client.ping()
    except Exception as exc:
        pytest.skip(f"Redis not available at {redis_url}: {exc}")
    return client


@pytest.fixture(autouse=True)
def _clear_rate_limit_keys(redis_url: str):
    """Keep tests deterministic by clearing Redis-backed rate-limit counters.

    This is best-effort and should not cause skips/failures if Redis is absent.
    """

    client = Redis.from_url(redis_url, decode_responses=True)
    try:
        client.ping()
    except Exception:
        return

    keys = client.keys("ratelimit:synthetic:*")
    if keys:
        client.delete(*keys)

