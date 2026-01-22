from __future__ import annotations

import os
import time

from fastapi.testclient import TestClient

from app.main import create_app


def test_synthetic_tasks_rate_limited(redis_client, monkeypatch):
    # Deterministic + non-flaky: long window so we don't cross boundary.
    monkeypatch.setenv("REDIS_URL", os.getenv("REDIS_URL", "redis://localhost:6379/0"))
    monkeypatch.setenv("SYNTHETIC_RATELIMIT_PER_MIN", "2")
    monkeypatch.setenv("SYNTHETIC_RATELIMIT_WINDOW_SECONDS", "3600")

    client_ip = "1.2.3.4"
    client_id = f"ip:{client_ip}"
    window_seconds = 3600
    window_id = int(time.time()) // window_seconds
    redis_client.delete(f"ratelimit:synthetic:{client_id}:{window_id}")

    app = create_app()

    headers = {"X-Forwarded-For": client_ip}
    params = {"n": 100000, "seed": 42}

    with TestClient(app) as client:
        r1 = client.get("/api/v1/synthetic/tasks", params=params, headers=headers)
        assert r1.status_code == 200

        r2 = client.get("/api/v1/synthetic/tasks", params=params, headers=headers)
        assert r2.status_code == 200

        r3 = client.get("/api/v1/synthetic/tasks", params=params, headers=headers)
        assert r3.status_code == 429
        assert r3.headers.get("X-Request-Id")
        assert r3.headers.get("Retry-After")

        body = r3.json()
        assert body["ok"] is False
        assert body["error"]["code"] == "rate_limited"
        assert body["error"]["details"]["limit"] == 2
        assert body["error"]["details"]["window_seconds"] == 3600
        assert body["meta"]["request_id"] == r3.headers["X-Request-Id"]
