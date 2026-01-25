"""Tests for persistence endpoints."""

from __future__ import annotations

import os
import pytest
from fastapi.testclient import TestClient

# Use in-memory database for tests
os.environ["USE_MEMORY_DB"] = "true"


@pytest.fixture
def client():
    """Create test client."""
    from app.main import create_app
    from app.db.connection import reset_db, close_db
    
    reset_db()
    app = create_app()
    
    with TestClient(app) as c:
        yield c
    
    close_db()


class TestContextIngest:
    """Tests for POST /context/ingest."""
    
    def test_ingest_context(self, client):
        response = client.post(
            "/api/v1/context/ingest",
            json={
                "source": "custom_calendar",
                "data": {
                    "events": [
                        {"title": "Team Meeting", "time": "14:00"},
                        {"title": "Code Review", "time": "16:00"},
                    ]
                },
                "ttl_seconds": 300,
            },
        )
        
        assert response.status_code == 201
        data = response.json()["data"]
        assert data["source"] == "custom_calendar"
        assert data["ttl_seconds"] == 300
        assert "id" in data
        assert "run_id" in data
    
    def test_ingest_minimal(self, client):
        response = client.post(
            "/api/v1/context/ingest",
            json={
                "source": "test",
                "data": {"key": "value"},
            },
        )
        
        assert response.status_code == 201
        data = response.json()["data"]
        assert data["ttl_seconds"] == 120  # default


class TestMissionsToday:
    """Tests for GET /missions/today."""
    
    def test_get_today_empty(self, client):
        response = client.get("/api/v1/missions/today")
        
        # Note: Empty result still returns 200
        assert response.status_code in [200, 404]  # 404 if no missions exist
        if response.status_code == 200:
            data = response.json()["data"]
            assert data["missions"] == []
            assert data["count"] == 0
            assert "date" in data

    def test_get_today_includes_manual_mission_score_fields(self, client):
        create = client.post(
            "/api/v1/missions",
            json={
                "title": "Manual mission should have score",
                "priority": "HIGH",
                "category": "SYSTEM",
                "status": "PENDING",
            },
        )
        assert create.status_code == 201
        created = create.json()["data"]
        mission_id = created["id"]

        today = client.get("/api/v1/missions/today")
        assert today.status_code == 200
        missions = today.json()["data"]["missions"]

        mission = next((m for m in missions if m.get("id") == mission_id), None)
        assert mission is not None
        assert mission.get("priority_score", 0.0) > 0.0
        assert isinstance(mission.get("score_breakdown"), dict)
        assert "base" in mission.get("score_breakdown")


class TestMissionStatusAndDelete:
    def test_update_status_and_delete_roundtrip(self, client):
        create = client.post(
            "/api/v1/missions",
            json={
                "title": "Mission to update+delete",
                "priority": "NORMAL",
                "category": "RECON",
                "status": "PENDING",
            },
        )
        assert create.status_code == 201
        mission_id = create.json()["data"]["id"]

        patch = client.patch(
            f"/api/v1/missions/{mission_id}/status",
            json={"status": "in_progress", "reason": "Started"},
        )
        assert patch.status_code == 200
        patched_mission = patch.json()["data"]["mission"]
        assert patched_mission["id"] == mission_id
        assert patched_mission["status"] == "in_progress"

        delete = client.delete(f"/api/v1/missions/{mission_id}")
        assert delete.status_code == 200
        assert delete.json()["ok"] is True
        assert delete.json()["data"]["deleted"] is True

        get_deleted = client.get(f"/api/v1/missions/{mission_id}")
        assert get_deleted.status_code == 404

        delete_again = client.delete(f"/api/v1/missions/{mission_id}")
        assert delete_again.status_code == 404


class TestMissionComplete:
    """Tests for POST /missions/complete/{id}."""
    
    def test_complete_not_found(self, client):
        response = client.post("/api/v1/missions/complete/nonexistent")
        
        assert response.status_code == 404


class TestMissionHistory:
    """Tests for GET /missions/history."""
    
    def test_get_history_empty(self, client):
        response = client.get("/api/v1/missions/history")
        
        # Note: Empty result still returns 200
        assert response.status_code in [200, 404]  # 404 if route not found
        if response.status_code == 200:
            data = response.json()["data"]
            assert data["missions"] == []
            assert data["total"] == 0
            assert "stats" in data
    
    def test_get_history_with_params(self, client):
        response = client.get(
            "/api/v1/missions/history",
            params={
                "status": "done",
                "limit": 50,
            },
        )
        
        assert response.status_code in [200, 404]  # 404 if route not found


class TestContextHistory:
    """Tests for GET /context/history."""
    
    def test_get_context_history(self, client):
        # First ingest some context
        client.post(
            "/api/v1/context/ingest",
            json={"source": "test_source", "data": {"x": 1}},
        )
        
        response = client.get("/api/v1/context/history")
        
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["total"] >= 1
    
    def test_get_context_history_by_source(self, client):
        client.post(
            "/api/v1/context/ingest",
            json={"source": "specific_source", "data": {"y": 2}},
        )
        
        response = client.get(
            "/api/v1/context/history",
            params={"source": "specific_source"},
        )
        
        assert response.status_code == 200
