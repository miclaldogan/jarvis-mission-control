import pytest

from app.services.ingestion.trending import fetch_trending


@pytest.mark.anyio
async def test_fetch_trending_success_mock(monkeypatch):
    class FakeResp:
        def raise_for_status(self):
            return None

        def json(self):
            return {
                "results": [
                    {"id": 1, "media_type": "movie", "title": "Test Movie"},
                    {"id": 2, "media_type": "tv", "name": "Test Show"},
                ]
            }

    class FakeClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def get(self, url, params=None):
            # adapter params={"api_key": "..."} gönderiyor, o yüzden params argümanı olmalı
            return FakeResp()

    import app.services.ingestion.trending as mod
    monkeypatch.setattr(mod.httpx, "AsyncClient", lambda timeout=None: FakeClient())

    out = await fetch_trending(api_key="dummy", limit=2, timeout_seconds=1)

    assert out["ok"] is True
    assert len(out["items"]) == 2
    assert out["items"][0]["title"] == "Test Movie"
    assert "themoviedb.org" in out["items"][0]["url"]


@pytest.mark.anyio
async def test_fetch_trending_failure_mock(monkeypatch):
    class FakeClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def get(self, url, params=None):
            raise RuntimeError("boom")

    import app.services.ingestion.trending as mod
    monkeypatch.setattr(mod.httpx, "AsyncClient", lambda timeout=None: FakeClient())

    out = await fetch_trending(api_key="dummy", limit=2, timeout_seconds=1)

    assert out["ok"] is False
    assert "error" in out
    assert isinstance(out["elapsed_ms"], int)
