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

        request_id = res.headers.get("X-Request-Id")
        assert isinstance(request_id, str)
        assert request_id

        body = res.json()
        assert body["ok"] is True
        assert body["data"]["service"] == "backend"
        assert isinstance(body["data"]["version"], str)
        assert body["data"]["version"]
        assert body["meta"]["request_id"] == request_id

        assert res.headers.get("X-Content-Type-Options") == "nosniff"
        assert res.headers.get("X-Frame-Options") == "DENY"
        assert res.headers.get("Referrer-Policy") == "no-referrer"
        assert isinstance(res.headers.get("Permissions-Policy"), str)
        assert res.headers.get("Permissions-Policy")


def test_health_echoes_client_request_id():
    os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")
    app = create_app()

    with TestClient(app) as client:
        res = client.get("/api/v1/health", headers={"X-Request-Id": "req_test_123"})
        assert res.status_code == 200
        assert res.headers.get("X-Request-Id") == "req_test_123"
        assert res.json()["meta"]["request_id"] == "req_test_123"


def test_cors_preflight_allows_local_frontend_origin():
    os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")
    # Allow default origins from settings (includes http://localhost:3000)
    app = create_app()

    with TestClient(app) as client:
        res = client.options(
            "/api/v1/health",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
            },
        )
        assert res.status_code in {200, 204}
        assert res.headers.get("access-control-allow-origin") == "http://localhost:3000"
