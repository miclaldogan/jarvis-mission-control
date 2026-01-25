"""
Hybrid storage for missions, runs, and their history.

Uses SQLite for persistent storage with in-memory cache for fast reads.
Data survives container restarts.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Optional
from collections import defaultdict

from app.db.connection import get_db, init_db


# Initialize DB on module load
_db_initialized = False


def _ensure_db() -> None:
    """Ensure database is initialized."""
    global _db_initialized
    if not _db_initialized:
        init_db()
        _db_initialized = True


# In-memory caches for fast reads (synced with DB)
_missions: dict[str, dict[str, Any]] = {}
_mission_history: dict[str, list[dict[str, Any]]] = defaultdict(list)
_runs: dict[str, dict[str, Any]] = {}
_run_list: list[str] = []  # Ordered list of run IDs


def _load_from_db() -> None:
    """Load missions from SQLite into memory cache."""
    global _missions, _mission_history
    _ensure_db()
    
    try:
        conn = get_db()
        cursor = conn.execute("""
            SELECT id, title, priority, status, tags, why, due_at, completed_at,
                   created_at, updated_at, evidence, priority_score, score_breakdown, reasons
            FROM missions
            ORDER BY created_at DESC
        """)
        
        for row in cursor.fetchall():
            mission = {
                "id": row["id"],
                "title": row["title"],
                "priority": row["priority"],
                "status": row["status"],
                "tags": json.loads(row["tags"]) if row["tags"] else [],
                "why": row["why"] or "",
                "due_at": row["due_at"],
                "completed_at": row["completed_at"],
                "created_at": row["created_at"],
                "updated_at": row["updated_at"],
                "evidence": json.loads(row["evidence"]) if row["evidence"] else {},
                "priority_score": row["priority_score"] or 0.0,
                "score_breakdown": json.loads(row["score_breakdown"]) if row["score_breakdown"] else {},
                "reasons": json.loads(row["reasons"]) if row["reasons"] else [],
            }
            _missions[mission["id"]] = mission
    except Exception as e:
        import logging
        logging.getLogger(__name__).warning(f"Failed to load missions from DB: {e}")


# Load from DB on module import
_load_from_db()


def store_mission(mission: dict[str, Any]) -> None:
    """Store a mission in SQLite and memory cache."""
    mission_id = mission.get("id")
    if not mission_id:
        raise ValueError("Mission must have an 'id' field")
    
    _ensure_db()
    
    # Store in memory cache
    _missions[mission_id] = mission.copy()
    
    # Persist to SQLite
    try:
        conn = get_db()
        conn.execute("""
            INSERT OR REPLACE INTO missions 
            (id, title, priority, status, tags, why, due_at, completed_at,
             created_at, updated_at, evidence, priority_score, score_breakdown, reasons)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            mission_id,
            mission.get("title", ""),
            mission.get("priority", "P3"),
            mission.get("status", "open"),
            json.dumps(mission.get("tags", [])),
            mission.get("why", ""),
            mission.get("due_at"),
            mission.get("completed_at"),
            mission.get("created_at", datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")),
            mission.get("updated_at", datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")),
            json.dumps(mission.get("evidence", {})),
            mission.get("priority_score", 0.0),
            json.dumps(mission.get("score_breakdown", {})),
            json.dumps(mission.get("reasons", [])),
        ))
        conn.commit()
    except Exception as e:
        import logging
        logging.getLogger(__name__).warning(f"Failed to persist mission to DB: {e}")
    
    # Add creation event to history
    add_history_event(
        mission_id=mission_id,
        event_type="created",
        reason=mission.get("why", "Mission generated"),
        data={
            "priority": mission.get("priority"),
            "priority_score": mission.get("priority_score"),
            "tags": mission.get("tags", []),
            "due_at": mission.get("due_at"),
        },
    )


def get_mission(mission_id: str) -> Optional[dict[str, Any]]:
    """Retrieve a mission by ID."""
    return _missions.get(mission_id)


def get_all_missions() -> list[dict[str, Any]]:
    """Get all stored missions."""
    return list(_missions.values())


def update_mission_status(mission_id: str, new_status: str, reason: str = "") -> bool:
    """Update mission status and record in history."""
    mission = _missions.get(mission_id)
    if not mission:
        return False
    
    old_status = mission.get("status")
    mission["status"] = new_status
    mission["updated_at"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    
    add_history_event(
        mission_id=mission_id,
        event_type="status_changed",
        reason=reason or f"Status changed from {old_status} to {new_status}",
        data={"old_status": old_status, "new_status": new_status},
    )
    
    return True


def update_mission_priority(
    mission_id: str, new_priority: str, new_score: float, reason: str = ""
) -> bool:
    """Update mission priority and record in history."""
    mission = _missions.get(mission_id)
    if not mission:
        return False
    
    old_priority = mission.get("priority")
    old_score = mission.get("priority_score")
    
    mission["priority"] = new_priority
    mission["priority_score"] = new_score
    mission["updated_at"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    
    add_history_event(
        mission_id=mission_id,
        event_type="priority_changed",
        reason=reason or f"Priority recalculated: {old_priority} ({old_score:.2f}) → {new_priority} ({new_score:.2f})",
        data={
            "old_priority": old_priority,
            "new_priority": new_priority,
            "old_score": old_score,
            "new_score": new_score,
        },
    )
    
    return True


def add_history_event(
    mission_id: str, event_type: str, reason: str, data: Optional[dict[str, Any]] = None
) -> None:
    """Add a history event for a mission."""
    event = {
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "event_type": event_type,
        "reason": reason,
        "data": data or {},
    }
    _mission_history[mission_id].append(event)


def get_mission_history(mission_id: str) -> list[dict[str, Any]]:
    """Get history for a specific mission."""
    return _mission_history.get(mission_id, [])


def store_run(run: dict[str, Any]) -> None:
    """Store a mission run."""
    run_id = run["run_id"]
    _runs[run_id] = run
    if run_id not in _run_list:
        _run_list.insert(0, run_id)  # Most recent first


def get_run(run_id: str) -> dict[str, Any] | None:
    """Get a specific run by ID."""
    return _runs.get(run_id)


def get_all_runs(limit: int = 50) -> list[dict[str, Any]]:
    """Get all runs, most recent first."""
    return [_runs[rid] for rid in _run_list[:limit] if rid in _runs]


def get_runs_for_mission(mission_id: str, limit: int = 10) -> list[dict[str, Any]]:
    """Get all runs for a specific mission."""
    return [
        _runs[rid]
        for rid in _run_list
        if rid in _runs and _runs[rid]["mission_id"] == mission_id
    ][:limit]


def clear_all() -> None:
    """Clear all stored missions and history (for testing)."""
    _missions.clear()
    _mission_history.clear()
    _runs.clear()
    _run_list.clear()
