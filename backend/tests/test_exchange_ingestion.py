import pytest

from app.services.ingestion.exchange import fetch_exchange_rates


@pytest.mark.anyio
async def test_fetch_exchange_rates_success(monkeypatch):
    class FakeResp:
        def raise_for_status(self):
            return None

        def json(self):
            return {"base": "EUR", "date": "2026-01-01", "rates": {"USD": 1.1}}

    class FakeClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def get(self, url, params=None):
            return FakeResp()

    # Patch httpx.AsyncClient in the module under test
    import app.services.ingestion.exchange as ex_mod
    monkeypatch.setattr(ex_mod.httpx, "AsyncClient", lambda timeout=None: FakeClient())

    out = await fetch_exchange_rates(base="EUR", timeout_seconds=1)

    assert out["ok"] is True
    assert out["base"] == "EUR"
    assert out["observed_at"] == "2026-01-01"
    assert out["rates"]["USD"] == 1.1
    assert isinstance(out["elapsed_ms"], int)


@pytest.mark.anyio
async def test_fetch_exchange_rates_failure(monkeypatch):
    class FakeClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def get(self, url, params=None):
            raise RuntimeError("boom")

    import app.services.ingestion.exchange as ex_mod
    monkeypatch.setattr(ex_mod.httpx, "AsyncClient", lambda timeout=None: FakeClient())

    out = await fetch_exchange_rates(base="EUR", timeout_seconds=1)

    assert out["ok"] is False
    assert "error" in out
    assert isinstance(out["elapsed_ms"], int)
