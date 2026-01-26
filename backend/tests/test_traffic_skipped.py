import pytest
from app.services.context import build_context_snapshot


@pytest.mark.anyio
async def test_traffic_skipped_when_missing_api_key(monkeypatch):
    monkeypatch.delenv("TRAFFIC_API_KEY", raising=False)

    data = await build_context_snapshot(debug=False)
    skipped = data.get("sources_skipped", [])
    assert any(x.get("source") == "traffic" for x in skipped), skipped
