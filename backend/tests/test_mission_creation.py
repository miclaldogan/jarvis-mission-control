"""
Test suite for POST /api/v1/missions endpoint.
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import create_app


@pytest.fixture
def client():
    app = create_app()
    return TestClient(app)


def test_create_mission_success(client):
    """Test successful mission creation with valid data."""
    payload = {
        "title": "Test mission for unit tests",
        "priority": "HIGH",
        "category": "SYSTEM",
        "status": "PENDING"
    }
    
    response = client.post("/api/v1/missions", json=payload)
    
    assert response.status_code == 201
    data = response.json()
    
    assert data["ok"] is True
    assert "data" in data
    
    mission = data["data"]
    assert mission["title"] == payload["title"]
    assert mission["priority"] == payload["priority"]
    assert mission["category"] == payload["category"]
    assert mission["status"] == payload["status"]
    assert mission["id"].startswith("msn_")
    assert "created_at" in mission
    assert "X-Compute-Time-ms" in response.headers


def test_create_mission_default_status(client):
    """Test mission creation with default status (PENDING)."""
    payload = {
        "title": "Test mission without status",
        "priority": "NORMAL",
        "category": "RECON"
    }
    
    response = client.post("/api/v1/missions", json=payload)
    
    assert response.status_code == 201
    data = response.json()
    mission = data["data"]
    
    assert mission["status"] == "PENDING"


def test_create_mission_invalid_priority(client):
    """Test validation error for invalid priority."""
    payload = {
        "title": "Test mission",
        "priority": "INVALID_PRIORITY",
        "category": "SYSTEM"
    }
    
    response = client.post("/api/v1/missions", json=payload)
    
    assert response.status_code == 422  # Validation error


def test_create_mission_missing_title(client):
    """Test validation error for missing title."""
    payload = {
        "priority": "HIGH",
        "category": "SYSTEM"
    }
    
    response = client.post("/api/v1/missions", json=payload)
    
    assert response.status_code == 422


def test_create_mission_empty_title(client):
    """Test validation error for empty title."""
    payload = {
        "title": "",
        "priority": "HIGH",
        "category": "SYSTEM"
    }
    
    response = client.post("/api/v1/missions", json=payload)
    
    assert response.status_code == 422


def test_create_mission_title_too_long(client):
    """Test validation error for title exceeding 200 characters."""
    payload = {
        "title": "x" * 201,
        "priority": "HIGH",
        "category": "SYSTEM"
    }
    
    response = client.post("/api/v1/missions", json=payload)
    
    assert response.status_code == 422


def test_create_mission_all_categories(client):
    """Test mission creation with all valid categories."""
    categories = ["SYSTEM", "RECON", "ENCRYPTION", "DEFENSE"]
    
    for category in categories:
        payload = {
            "title": f"Test {category} mission",
            "priority": "NORMAL",
            "category": category
        }
        
        response = client.post("/api/v1/missions", json=payload)
        
        assert response.status_code == 201
        data = response.json()
        assert data["data"]["category"] == category


def test_create_mission_all_priorities(client):
    """Test mission creation with all valid priorities."""
    priorities = ["CRITICAL", "HIGH", "NORMAL", "LOW"]
    
    for priority in priorities:
        payload = {
            "title": f"Test {priority} mission",
            "priority": priority,
            "category": "SYSTEM"
        }
        
        response = client.post("/api/v1/missions", json=payload)
        
        assert response.status_code == 201
        data = response.json()
        assert data["data"]["priority"] == priority


def test_create_mission_unique_ids(client):
    """Test that each created mission gets a unique ID."""
    payload = {
        "title": "Test mission",
        "priority": "NORMAL",
        "category": "SYSTEM"
    }
    
    response1 = client.post("/api/v1/missions", json=payload)
    response2 = client.post("/api/v1/missions", json=payload)
    
    assert response1.status_code == 201
    assert response2.status_code == 201
    
    id1 = response1.json()["data"]["id"]
    id2 = response2.json()["data"]["id"]
    
    assert id1 != id2
    assert id1.startswith("msn_")
    assert id2.startswith("msn_")
