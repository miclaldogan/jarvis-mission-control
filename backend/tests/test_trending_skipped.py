from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import create_app
import app.api.v1.endpoints.context as context_endpoint



def test_trending_skipped_when_no_key(monkeypatch):
    """Deterministic smoke test: missing TMDB key => sources_skipped, endpoint returns 200."""
    monkeypatch.delenv("TMDB_API_KEY", raising=False)

    async def fake_build_context_snapshot(
        *,
        debug: bool = False,
        news_limit: int = 5,
        city: str = None,
        news_mode: str | None = None,
        **_: object,
    ):
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
            # IMPORTANT: at least one OK source so endpoint returns 200 (not 502)
            "sources_ok": ["exchange"],
            "sources_failed": [],
            "sources_skipped": [
                {"source": "trending", "reason": "Missing required env var: TMDB_API_KEY"},
            ],
        }

    monkeypatch.setattr(context_endpoint, "build_context_snapshot", fake_build_context_snapshot)

    app = create_app()
    with TestClient(app, raise_server_exceptions=False) as client:
        r = client.get("/api/v1/context?refresh=true")
        assert r.status_code == 200

        payload = r.json()
        assert payload.get("ok") is True

        data = payload.get("data") or {}
        skipped = data.get("sources_skipped") or []
        assert any(x.get("source") == "trending" for x in skipped), skipped


def test_context_partial_success_returns_200(monkeypatch):
    """
    Deterministic smoke test:
    - One source OK
    - One source FAILED
    -> endpoint must still return 200 (partial success)
    """

    async def fake_build_context_snapshot(
        *,
        debug: bool = False,
        news_limit: int = 5,
        city: str = None,
        news_mode: str | None = None,
        **_: object,
    ):
        return {
            "context_id": "ctx_test_partial",
            "observed_at": "2026-01-01T00:00:00Z",
            "fetched_at": "2026-01-01T00:00:00Z",
            "weather": None,
            "github": None,
            "news": [],
            "exchange": {"base": "EUR", "rates": {"USD": 1.0}, "observed_at": "2026-01-01"},
            "traffic": None,
            "trending": [],
            "calendar": {"events_today": 0},
            "sources_ok": ["exchange"],
            "sources_failed": [{"source": "news", "error": "boom"}],
            "sources_skipped": [],
        }

    monkeypatch.setattr(context_endpoint, "build_context_snapshot", fake_build_context_snapshot)

    app = create_app()
    with TestClient(app, raise_server_exceptions=False) as client:
        r = client.get("/api/v1/context?refresh=true")
        assert r.status_code == 200

        payload = r.json()
        assert payload.get("ok") is True

        data = payload.get("data") or {}
        failed = data.get("sources_failed") or []
        assert any(x.get("source") == "news" for x in failed), failed

        ok_list = data.get("sources_ok") or []
        assert "exchange" in ok_list
