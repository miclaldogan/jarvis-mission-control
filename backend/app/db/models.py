"""SQLite database models for persistent storage.

Implements:
- Mission: Task records with CRUD operations
- ContextSnapshot: Historical context data
- UserPreference: User settings and preferences
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any, Literal, Optional
import json


Status = Literal["open", "in_progress", "done", "snoozed", "cancelled"]
Priority = Literal["P1", "P2", "P3", "P4"]


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _utc_now_iso() -> str:
    return _utc_now().isoformat().replace("+00:00", "Z")


@dataclass
class Mission:
    """Mission/Task entity for persistent storage."""
    
    id: str
    title: str
    priority: Priority = "P3"
    status: Status = "open"
    tags: list[str] = field(default_factory=list)
    why: str = ""
    due_at: Optional[str] = None
    completed_at: Optional[str] = None
    created_at: str = field(default_factory=_utc_now_iso)
    updated_at: str = field(default_factory=_utc_now_iso)
    evidence: dict[str, Any] = field(default_factory=dict)
    actions: list[dict[str, str]] = field(default_factory=list)
    priority_score: float = 0.0
    score_breakdown: dict[str, float] = field(default_factory=dict)
    reasons: list[str] = field(default_factory=list)
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Mission:
        """Create Mission from dictionary."""
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})
    
    def mark_complete(self) -> None:
        """Mark mission as completed with timestamp."""
        self.status = "done"
        self.completed_at = _utc_now_iso()
        self.updated_at = _utc_now_iso()
    
    def mark_in_progress(self) -> None:
        """Mark mission as in progress."""
        self.status = "in_progress"
        self.updated_at = _utc_now_iso()
    
    def snooze(self, until: Optional[str] = None) -> None:
        """Snooze mission, optionally until a specific time."""
        self.status = "snoozed"
        if until:
            self.due_at = until
        self.updated_at = _utc_now_iso()


@dataclass
class ContextSnapshot:
    """Historical context data snapshot."""
    
    id: str
    run_id: str
    source: str  # weather, github, news, calendar, etc.
    data: dict[str, Any] = field(default_factory=dict)
    ingested_at: str = field(default_factory=_utc_now_iso)
    ttl_seconds: int = 120
    is_synthetic: bool = False
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ContextSnapshot:
        """Create ContextSnapshot from dictionary."""
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})
    
    def is_expired(self) -> bool:
        """Check if snapshot has expired based on TTL."""
        ingested = datetime.fromisoformat(self.ingested_at.replace("Z", "+00:00"))
        age_seconds = (_utc_now() - ingested).total_seconds()
        return age_seconds > self.ttl_seconds


@dataclass
class UserPreference:
    """User preferences and settings."""
    
    id: str = "default"
    energy_level: str = "medium"  # low, medium, high
    focus_tags: list[str] = field(default_factory=list)
    blocked_tags: list[str] = field(default_factory=list)
    work_hours_start: int = 9  # 24-hour format
    work_hours_end: int = 18
    timezone: str = "UTC"
    notification_enabled: bool = True
    theme: str = "dark"
    created_at: str = field(default_factory=_utc_now_iso)
    updated_at: str = field(default_factory=_utc_now_iso)
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> UserPreference:
        """Create UserPreference from dictionary."""
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})
    
    def update(self, **kwargs: Any) -> None:
        """Update preferences with new values."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = _utc_now_iso()


# SQL Schema for SQLite (for reference and migrations)
SQL_SCHEMA = """
-- Missions table
CREATE TABLE IF NOT EXISTS missions (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    priority TEXT DEFAULT 'P3',
    status TEXT DEFAULT 'open',
    tags TEXT DEFAULT '[]',  -- JSON array
    why TEXT DEFAULT '',
    due_at TEXT,
    completed_at TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    evidence TEXT DEFAULT '{}',  -- JSON object
    actions TEXT DEFAULT '[]',  -- JSON array
    priority_score REAL DEFAULT 0.0,
    score_breakdown TEXT DEFAULT '{}',  -- JSON object
    reasons TEXT DEFAULT '[]'  -- JSON array
);

-- Context snapshots table
CREATE TABLE IF NOT EXISTS context_snapshots (
    id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL,
    source TEXT NOT NULL,
    data TEXT DEFAULT '{}',  -- JSON object
    ingested_at TEXT NOT NULL,
    ttl_seconds INTEGER DEFAULT 120,
    is_synthetic INTEGER DEFAULT 0
);

-- User preferences table
CREATE TABLE IF NOT EXISTS user_preferences (
    id TEXT PRIMARY KEY DEFAULT 'default',
    energy_level TEXT DEFAULT 'medium',
    focus_tags TEXT DEFAULT '[]',  -- JSON array
    blocked_tags TEXT DEFAULT '[]',  -- JSON array
    work_hours_start INTEGER DEFAULT 9,
    work_hours_end INTEGER DEFAULT 18,
    timezone TEXT DEFAULT 'UTC',
    notification_enabled INTEGER DEFAULT 1,
    theme TEXT DEFAULT 'dark',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_missions_status ON missions(status);
CREATE INDEX IF NOT EXISTS idx_missions_priority ON missions(priority);
CREATE INDEX IF NOT EXISTS idx_missions_due_at ON missions(due_at);
CREATE INDEX IF NOT EXISTS idx_missions_created_at ON missions(created_at);
CREATE INDEX IF NOT EXISTS idx_context_run_id ON context_snapshots(run_id);
CREATE INDEX IF NOT EXISTS idx_context_source ON context_snapshots(source);
CREATE INDEX IF NOT EXISTS idx_context_ingested_at ON context_snapshots(ingested_at);
"""
