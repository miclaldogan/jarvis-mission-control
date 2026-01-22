from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app


def _clear_context_cache(client) -> None:
    keys = client.keys("cache:v1:context:*")
    if keys:
        client.delete(*keys)


def test_context_cache_proof_headers_and_refresh(redis_client, monkeypatch):
    async def fake_build_context_snapshot(*, debug: bool = False, news_limit: int = 5):
        base = {
            "context_id": "ctx_test",
            "observed_at": "2026-01-01T00:00:00Z",
            "fetched_at": "2026-01-01T00:00:00Z",
            "weather": None,
            "github": None,
            "news": [],
            "calendar": {"events_today": 0},
            "sources_ok": ["news"],
            "sources_failed": [],
            "sources_skipped": [],
        }
        if debug:
            base["debug"] = True
        return base

    import app.api.v1.endpoints.context as context_ep

    monkeypatch.setattr(context_ep, "build_context_snapshot", fake_build_context_snapshot)
    _clear_context_cache(redis_client)

    with TestClient(app) as client:
        r1 = client.get("/api/v1/context")
        assert r1.status_code == 200
        assert r1.headers.get("X-Cache") == "MISS"
        assert r1.headers.get("X-Cache-Key")

        r2 = client.get("/api/v1/context")
        assert r2.status_code == 200
        assert r2.headers.get("X-Cache") == "HIT"
        assert r2.headers.get("X-Cache-Key") == r1.headers.get("X-Cache-Key")

        # refresh=true bypasses cache read and forces compute (but updates same cache key)
        r3 = client.get("/api/v1/context?refresh=true")
        assert r3.status_code == 200
        assert r3.headers.get("X-Cache") == "MISS"
        assert r3.headers.get("X-Cache-Key") == r1.headers.get("X-Cache-Key")

        # debug=true should use a different cache key
        r4 = client.get("/api/v1/context?debug=true")
        assert r4.status_code == 200
        assert r4.headers.get("X-Cache") == "MISS"
        assert r4.headers.get("X-Cache-Key") != r1.headers.get("X-Cache-Key")

        r5 = client.get("/api/v1/context?debug=true")
        assert r5.status_code == 200
        assert r5.headers.get("X-Cache") == "HIT"

