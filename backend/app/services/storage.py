"""
In-memory storage for missions and their history.

This is a temporary solution until database integration.
All data is lost on server restart.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional
from collections import defaultdict


# Global in-memory stores
_missions: dict[str, dict[str, Any]] = {}
_mission_history: dict[str, list[dict[str, Any]]] = defaultdict(list)


def store_mission(mission: dict[str, Any]) -> None:
    """Store a mission in memory."""
    mission_id = mission.get("id")
    if not mission_id:
        raise ValueError("Mission must have an 'id' field")
    
    _missions[mission_id] = mission.copy()
    
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


def clear_all() -> None:
    """Clear all stored missions and history (for testing)."""
    _missions.clear()
    _mission_history.clear()
