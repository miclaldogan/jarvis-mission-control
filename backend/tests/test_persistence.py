"""Tests for database persistence layer."""

from __future__ import annotations

import os
import pytest
import tempfile

# Use in-memory database for tests
os.environ["USE_MEMORY_DB"] = "true"

from app.db.connection import init_db, reset_db, close_db
from app.db.models import Mission, ContextSnapshot, UserPreference
from app.db.repository import MissionRepository, ContextRepository, PreferenceRepository


@pytest.fixture(autouse=True)
def setup_db():
    """Reset database before each test."""
    reset_db()
    yield
    close_db()


class TestMission:
    """Test Mission model."""
    
    def test_create_mission(self):
        m = Mission(
            id="msn_001",
            title="Test Mission",
            priority="P1",
            status="open",
            tags=["test", "urgent"],
        )
        assert m.id == "msn_001"
        assert m.title == "Test Mission"
        assert m.priority == "P1"
        assert m.status == "open"
    
    def test_mission_to_dict(self):
        m = Mission(id="msn_002", title="Dict Test")
        d = m.to_dict()
        assert d["id"] == "msn_002"
        assert d["title"] == "Dict Test"
        assert "created_at" in d
    
    def test_mark_complete(self):
        m = Mission(id="msn_003", title="Complete Test", status="open")
        assert m.status == "open"
        assert m.completed_at is None
        
        m.mark_complete()
        
        assert m.status == "done"
        assert m.completed_at is not None


class TestMissionRepository:
    """Test MissionRepository operations."""
    
    def test_create_and_get(self):
        m = Mission(id="msn_repo_001", title="Repo Test", priority="P2")
        created = MissionRepository.create(m)
        
        assert created.id == "msn_repo_001"
        
        fetched = MissionRepository.get_by_id("msn_repo_001")
        assert fetched is not None
        assert fetched.title == "Repo Test"
        assert fetched.priority == "P2"
    
    def test_get_all(self):
        MissionRepository.create(Mission(id="m1", title="Mission 1"))
        MissionRepository.create(Mission(id="m2", title="Mission 2"))
        MissionRepository.create(Mission(id="m3", title="Mission 3"))
        
        missions = MissionRepository.get_all()
        assert len(missions) == 3
    
    def test_get_all_with_filter(self):
        MissionRepository.create(Mission(id="m1", title="Open 1", status="open"))
        MissionRepository.create(Mission(id="m2", title="Done 1", status="done"))
        MissionRepository.create(Mission(id="m3", title="Open 2", status="open"))
        
        open_missions = MissionRepository.get_all(status="open")
        assert len(open_missions) == 2
        
        done_missions = MissionRepository.get_all(status="done")
        assert len(done_missions) == 1
    
    def test_update(self):
        m = MissionRepository.create(Mission(id="upd1", title="Original"))
        m.title = "Updated"
        m.priority = "P1"
        
        updated = MissionRepository.update(m)
        assert updated.title == "Updated"
        
        fetched = MissionRepository.get_by_id("upd1")
        assert fetched.title == "Updated"
        assert fetched.priority == "P1"
    
    def test_complete(self):
        MissionRepository.create(Mission(id="cmp1", title="To Complete"))
        
        completed = MissionRepository.complete("cmp1")
        assert completed.status == "done"
        assert completed.completed_at is not None
    
    def test_delete(self):
        MissionRepository.create(Mission(id="del1", title="To Delete"))
        
        result = MissionRepository.delete("del1")
        assert result is True
        
        fetched = MissionRepository.get_by_id("del1")
        assert fetched is None
    
    def test_get_history(self):
        m1 = Mission(id="h1", title="Done 1", status="done")
        m1.mark_complete()
        MissionRepository.create(m1)
        
        m2 = Mission(id="h2", title="Done 2", status="done")
        m2.mark_complete()
        MissionRepository.create(m2)
        
        history = MissionRepository.get_history()
        assert len(history) == 2
    
    def test_completion_stats(self):
        MissionRepository.create(Mission(id="s1", status="open"))
        MissionRepository.create(Mission(id="s2", status="open"))
        MissionRepository.create(Mission(id="s3", status="done"))
        MissionRepository.create(Mission(id="s4", status="done"))
        MissionRepository.create(Mission(id="s5", status="done"))
        
        stats = MissionRepository.get_completion_stats()
        assert stats["total"] == 5
        assert stats["open"] == 2
        assert stats["done"] == 3
        assert stats["completion_rate"] == 60.0


class TestContextRepository:
    """Test ContextRepository operations."""
    
    def test_create_and_get(self):
        snapshot = ContextSnapshot(
            id="ctx_001",
            run_id="run_001",
            source="weather",
            data={"temp": 20, "condition": "sunny"},
        )
        created = ContextRepository.create(snapshot)
        assert created.id == "ctx_001"
        
        snapshots = ContextRepository.get_by_run_id("run_001")
        assert len(snapshots) == 1
        assert snapshots[0].source == "weather"
    
    def test_get_latest_by_source(self):
        ContextRepository.create(ContextSnapshot(
            id="ctx_old",
            run_id="run_1",
            source="github",
            data={"old": True},
        ))
        ContextRepository.create(ContextSnapshot(
            id="ctx_new",
            run_id="run_2",
            source="github",
            data={"new": True},
        ))
        
        latest = ContextRepository.get_latest_by_source("github")
        assert latest is not None
        assert latest.id == "ctx_new"


class TestPreferenceRepository:
    """Test PreferenceRepository operations."""
    
    def test_get_creates_default(self):
        pref = PreferenceRepository.get("new_user")
        assert pref is not None
        assert pref.id == "new_user"
        assert pref.energy_level == "medium"
    
    def test_save_and_get(self):
        pref = UserPreference(
            id="custom_user",
            energy_level="high",
            focus_tags=["work", "urgent"],
            theme="light",
        )
        PreferenceRepository.save(pref)
        
        fetched = PreferenceRepository.get("custom_user")
        assert fetched.energy_level == "high"
        assert fetched.focus_tags == ["work", "urgent"]
        assert fetched.theme == "light"
