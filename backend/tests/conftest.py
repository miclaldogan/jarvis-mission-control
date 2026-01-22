from __future__ import annotations

import os

import pytest
from redis import Redis


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
