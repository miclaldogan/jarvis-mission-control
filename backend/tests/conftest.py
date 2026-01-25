from __future__ import annotations

import os
import sys
from pathlib import Path
from urllib.parse import urlparse, urlunparse

import pytest
from redis import Redis


# Ensure `import app...` works regardless of pytest rootdir.
BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))


def _compute_isolated_redis_url() -> str:
    test_url = os.getenv("REDIS_TEST_URL")
    if test_url:
        return test_url

    base_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    parsed = urlparse(base_url)
    isolated = parsed._replace(path="/15")
    return urlunparse(isolated)


# IMPORTANT: Make sure the FastAPI app (imported by tests) connects to the same
# isolated Redis DB as the fixtures. This runs before `app.main` is imported.
os.environ["REDIS_URL"] = _compute_isolated_redis_url()


@pytest.fixture(scope="session")
def redis_url() -> str:
    """Redis URL used by tests.

    IMPORTANT: Tests often monkeypatch handlers that still write to Redis.
    If tests share the same Redis DB as the running app (db=0), they can
    poison the runtime cache (e.g., /api/v1/context). To keep tests isolated,
    default tests to db=15 unless explicitly overridden.
    """

    return os.getenv("REDIS_URL", "redis://localhost:6379/15")


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

    # Keep cache-related tests from leaking across test cases.
    cache_keys = client.keys("cache:v1:context:*")
    if cache_keys:
        client.delete(*cache_keys)

