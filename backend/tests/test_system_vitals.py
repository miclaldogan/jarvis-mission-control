from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_system_vitals_returns_200():
    r = client.get("/api/v1/system/vitals")
    assert r.status_code == 200


def test_system_vitals_shape():
    payload = client.get("/api/v1/system/vitals").json()
    assert payload["ok"] is True
    data = payload["data"]
    for k in ["cpu", "memory", "disk", "network", "timestamp"]:
        assert k in data


def test_system_vitals_ranges():
    data = client.get("/api/v1/system/vitals").json()["data"]
    for k in ["cpu", "memory", "disk", "network"]:
        v = data[k]
        assert isinstance(v, (int, float))
        assert 0.0 <= float(v) <= 100.0
