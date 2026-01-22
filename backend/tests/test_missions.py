from __future__ import annotations

import os

from fastapi.testclient import TestClient

from app.main import create_app


def test_missions_generate_accepts_explicit_context_and_returns_missions():
    os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")
    app = create_app()

    body = {
        "context": {
            "context_id": "ctx_test",
            "observed_at": "2026-01-22T00:00:00Z",
            "weather": {"condition": "rain", "temp_c": 8, "city": "Istanbul"},
            "github": {"open_prs": 6, "open_issues": 12},
            "news": [{"title": "Example", "url": "https://example.com"}],
        },
        "preferences": {"energy_level": "medium", "time_of_day": "morning"},
        "limit": 12,
        "seed": 42,
    }

    with TestClient(app) as client:
        res = client.post("/api/v1/missions/generate", json=body)
        assert res.status_code == 200
        assert res.headers.get("X-Request-Id")
        assert res.headers.get("X-Compute-Time-ms")

        payload = res.json()
        assert payload["ok"] is True
        assert isinstance(payload["data"]["missions"], list)
        assert len(payload["data"]["missions"]) == 12

        first = payload["data"]["missions"][0]
        assert "id" in first
        assert "title" in first
        assert "priority" in first
        assert "why" in first
