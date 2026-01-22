from fastapi.testclient import TestClient

from app.main import app


def test_context_cache_hit_miss(monkeypatch):
    # deterministic snapshot
    async def fake_build_context_snapshot(debug: bool = False):
        return {
            "fetched_at": "2026-01-01T00:00:00Z",
            "weather": None,
            "github": None,
            "news": [],
            "sources_ok": ["news"],
            "sources_failed": [],
            "sources_skipped": [],
        }

    # patch the function used by endpoint
    import app.api.v1.endpoints.context as context_ep
    monkeypatch.setattr(context_ep, "build_context_snapshot", fake_build_context_snapshot)

    client = TestClient(app)

    r1 = client.get("/api/v1/context")
    assert r1.status_code == 200
    assert r1.json()["data"]["cache"] == "MISS"

    r2 = client.get("/api/v1/context")
    assert r2.status_code == 200
    assert r2.json()["data"]["cache"] == "HIT"

    # refresh bypass should force MISS
    r3 = client.get("/api/v1/context?refresh=true")
    assert r3.status_code == 200
    assert r3.json()["data"]["cache"] == "MISS"
