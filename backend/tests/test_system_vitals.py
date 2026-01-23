import importlib

import pytest
from fastapi.testclient import TestClient

from app.main import create_app

client = TestClient(create_app())


def test_system_vitals_success():
    # Skip if psutil isn't available in this environment
    try:
        importlib.import_module("psutil")
    except ModuleNotFoundError:
        pytest.skip("psutil not installed; success metrics test skipped")

    r = client.get("/api/v1/system/vitals")
    assert r.status_code == 200

    body = r.json()
    assert body["ok"] is True

    data = body["data"]
    assert "cpu" in data
    assert "memory" in data
    assert "network" in data
    assert "disk" in data


def test_system_vitals_psutil_missing(monkeypatch):
    original = importlib.import_module

    def fake_import(name, *args, **kwargs):
        if name == "psutil":
            raise ModuleNotFoundError("No module named 'psutil'")
        return original(name, *args, **kwargs)

    monkeypatch.setattr(importlib, "import_module", fake_import)

    r = client.get("/api/v1/system/vitals")
    assert r.status_code == 503

    body = r.json()
    assert body["ok"] is False
    assert body["error"]["code"] == "psutil_missing"
