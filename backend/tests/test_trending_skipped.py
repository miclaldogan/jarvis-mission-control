from fastapi.testclient import TestClient
from app.main import create_app


def test_trending_skipped_when_no_key(monkeypatch):
    monkeypatch.delenv("TMDB_API_KEY", raising=False)

    app = create_app()
    with TestClient(app) as client:
        r = client.get("/api/v1/context?refresh=true")
        assert r.status_code == 200
        data = r.json()["data"]

        assert "trending" in data
        assert data["trending"] == []

        skipped_sources = [x["source"] for x in data.get("sources_skipped", [])]
        assert "trending" in skipped_sources
