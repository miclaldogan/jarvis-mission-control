from __future__ import annotations

import os

from fastapi.testclient import TestClient

from app.main import create_app


def test_health_200_and_version_present():
    os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")
    app = create_app()

    with TestClient(app) as client:
        res = client.get("/api/v1/health")
        assert res.status_code == 200

        body = res.json()
        assert body["ok"] is True
        assert body["data"]["service"] == "backend"
        assert isinstance(body["data"]["version"], str)
        assert body["data"]["version"]
