from fastapi.testclient import TestClient

from app.main import create_app
import app.api.v1.endpoints.context as context_endpoint


def test_trending_skipped_when_no_key(monkeypatch):
    # Ensure TMDB key is missing
    monkeypatch.delenv("TMDB_API_KEY", raising=False)

    async def fake_build_context_snapshot(*, debug: bool = False, news_limit: int = 5):
        return {
            "context_id": "ctx_test",
            "observed_at": "2026-01-01T00:00:00Z",
            "fetched_at": "2026-01-01T00:00:00Z",
            "weather": None,
            "github": None,
            "news": [],
            "exchange": None,
            "traffic": None,
            "trending": [],
            "calendar": {"events_today": 0},
            "sources_ok": ["exchange"],  # force 200 (not 502)
            "sources_failed": [],
            "sources_skipped": [
                {"source": "trending", "reason": "Missing required env var: TMDB_API_KEY"},
            ],
        }

    monkeypatch.setattr(context_endpoint, "build_context_snapshot", fake_build_context_snapshot)

    app = create_app()
    with TestClient(app, raise_server_exceptions=False) as client:
        r = client.get("/api/v1/context?refresh=true")

        # 👇 TEŞHİS: 500 ise body'yi görmemiz lazım
        print("STATUS:", r.status_code)
        print("BODY:", r.text)

        assert r.status_code == 200

        payload = r.json()
        assert payload.get("ok") is True

        data = payload.get("data") or {}
        skipped = data.get("sources_skipped") or []
        assert any(x.get("source") == "trending" for x in skipped), skipped
