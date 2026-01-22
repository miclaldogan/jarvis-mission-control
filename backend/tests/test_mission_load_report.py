from __future__ import annotations

import os

from fastapi.testclient import TestClient

from app.cache import cache_key_mission_load
from app.main import create_app


def test_mission_load_report_cache_proof(redis_client):
    os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")
    app = create_app()

    cache_key = cache_key_mission_load(window="7d", bucket="day", seed=42)
    redis_client.delete(cache_key)

    with TestClient(app) as client:
        r1 = client.get("/api/v1/reports/mission-load?window=7d&bucket=day&seed=42")
        assert r1.status_code == 200
        assert r1.headers.get("X-Cache") == "MISS"
        assert r1.headers.get("X-Cache-Key") == cache_key
        assert r1.headers.get("X-Compute-Time-ms")

        r2 = client.get("/api/v1/reports/mission-load?window=7d&bucket=day&seed=42")
        assert r2.status_code == 200
        assert r2.headers.get("X-Cache") == "HIT"
        assert r2.headers.get("X-Cache-Key") == cache_key
        assert r2.headers.get("X-Compute-Time-ms")

        body = r2.json()
        assert body["ok"] is True
        assert body["data"]["window"] == "7d"
        assert body["data"]["bucket"] == "day"
        assert isinstance(body["data"]["series"], list)
        assert len(body["data"]["series"]) == 7
