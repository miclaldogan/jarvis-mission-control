from __future__ import annotations

import os
import time

from fastapi.testclient import TestClient

from app.cache import cache_key_synthetic_tasks
from app.main import create_app


def test_synthetic_tasks_cache_proof_headers(redis_client):
    os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")
    app = create_app()

    n = 100000
    seed = int(time.time()) % 2_000_000_000
    sample_size = 50
    cache_key = cache_key_synthetic_tasks(n=n, seed=seed, sample_size=sample_size)
    redis_client.delete(cache_key)

    with TestClient(app) as client:
        res1 = client.get("/api/v1/synthetic/tasks", params={"n": n, "seed": seed})
        assert res1.status_code == 200
        assert res1.headers.get("X-Cache") == "MISS"
        assert "X-Compute-Time-ms" in res1.headers

        res2 = client.get("/api/v1/synthetic/tasks", params={"n": n, "seed": seed})
        assert res2.status_code == 200
        assert res2.headers.get("X-Cache") == "HIT"
        assert "X-Compute-Time-ms" in res2.headers


def test_synthetic_tasks_seed_change_causes_miss(redis_client):
    os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")
    app = create_app()

    n = 100000
    seed1 = (int(time.time()) % 2_000_000_000) + 1
    seed2 = seed1 + 1

    with TestClient(app) as client:
        res1 = client.get("/api/v1/synthetic/tasks", params={"n": n, "seed": seed1})
        assert res1.status_code == 200

        # Prime cache for seed1
        res1b = client.get("/api/v1/synthetic/tasks", params={"n": n, "seed": seed1})
        assert res1b.status_code == 200
        assert res1b.headers.get("X-Cache") == "HIT"

        # Different seed should not hit seed1 cache
        res2 = client.get("/api/v1/synthetic/tasks", params={"n": n, "seed": seed2})
        assert res2.status_code == 200
        assert res2.headers.get("X-Cache") == "MISS"
