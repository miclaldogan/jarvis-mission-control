from __future__ import annotations

import time
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Literal, Optional

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from app.http_envelope import ok
from app.services.context import build_context_snapshot
from app.services.missions import generate_missions
from app.services import storage

router = APIRouter()


# Mission enums for type safety
class Priority(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    NORMAL = "NORMAL"
    LOW = "LOW"


class Category(str, Enum):
    SYSTEM = "SYSTEM"
    RECON = "RECON"
    ENCRYPTION = "ENCRYPTION"
    DEFENSE = "DEFENSE"


class Status(str, Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


# Request/Response models
class CreateMissionRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, description="Mission title")
    priority: Priority = Field(..., description="Mission priority level")
    category: Category = Field(..., description="Mission category")
    status: Status = Field(Status.PENDING, description="Initial mission status")


class MissionResponse(BaseModel):
    id: str = Field(..., description="Unique mission ID")
    title: str
    priority: Priority
    category: Category
    status: Status
    created_at: str = Field(..., description="ISO 8601 timestamp")


class Preferences(BaseModel):
    energy_level: Optional[Literal["low", "medium", "high"]] = None
    time_of_day: Optional[Literal["morning", "afternoon", "evening"]] = None


class MissionsGenerateRequest(BaseModel):
    context: Optional[dict[str, Any]] = None
    preferences: Optional[Preferences] = None
    limit: int = Field(15, ge=1, le=30)
    seed: Optional[int] = None


@router.post("/missions")
async def create_mission(request: Request, body: CreateMissionRequest):
    """
    Create a single mission.
    
    Currently stores in-memory only (no database persistence).
    Returns the created mission with generated ID and timestamp.
    """
    start = time.perf_counter()
    
    # Generate unique mission ID
    mission_id = f"msn_{uuid.uuid4().hex[:12]}"
    
    # Create mission object
    mission = MissionResponse(
        id=mission_id,
        title=body.title,
        priority=body.priority,
        category=body.category,
        status=body.status,
        created_at=datetime.now(timezone.utc).isoformat()
    )
    
    # TODO: Store in database when persistence layer is ready
    # For now, just return the created mission
    
    response = JSONResponse(ok(request, mission.model_dump()), status_code=201)
    compute_ms = int((time.perf_counter() - start) * 1000)
    response.headers["X-Compute-Time-ms"] = str(compute_ms)
    return response


@router.post("/missions/generate")
async def missions_generate(request: Request, body: MissionsGenerateRequest):
    start = time.perf_counter()

    context = body.context
    if context is None:
        context = await build_context_snapshot(debug=False)

    missions = generate_missions(
        context=context,
        preferences=body.preferences.model_dump() if body.preferences else None,
        limit=body.limit,
        seed=body.seed,
    )
    
    # Store generated missions in memory
    for mission in missions:
        storage.store_mission(mission)

    data = {
        "context": {
            "context_id": context.get("context_id"),
            "observed_at": context.get("observed_at") or context.get("fetched_at"),
        },
        "missions": missions,
    }

    response = JSONResponse(ok(request, data), status_code=200)
    compute_ms = int((time.perf_counter() - start) * 1000)
    response.headers["X-Compute-Time-ms"] = str(compute_ms)
    return response


@router.get("/missions/{mission_id}")
async def get_mission_detail(request: Request, mission_id: str):
    """
    Get mission detail with full history.
    
    Returns the mission object plus a timeline of all state changes.
    Useful for debugging why a mission has certain priority or status.
    """
    start = time.perf_counter()
    
    mission = storage.get_mission(mission_id)
    if not mission:
        return JSONResponse(
            {
                "ok": False,
                "error": {
                    "code": "MISSION_NOT_FOUND",
                    "message": f"Mission with ID '{mission_id}' does not exist",
                },
                "meta": {
                    "request_id": request.headers.get("X-Request-ID", "unknown"),
                    "ts": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                },
            },
            status_code=404,
        )
    
    history = storage.get_mission_history(mission_id)
    
    data = {
        "mission": mission,
        "history": history,
        "history_count": len(history),
    }
    
    response = JSONResponse(ok(request, data), status_code=200)
    compute_ms = int((time.perf_counter() - start) * 1000)
    response.headers["X-Compute-Time-ms"] = str(compute_ms)
    return response


@router.patch("/missions/{mission_id}/status")
async def update_mission_status(
    request: Request, mission_id: str, body: dict[str, Any]
):
    """
    Update mission status (open → in_progress → done).
    
    Records the change in mission history.
    """
    start = time.perf_counter()
    
    new_status = body.get("status")
    reason = body.get("reason", "")
    
    if not new_status:
        return JSONResponse(
            {
                "ok": False,
                "error": {
                    "code": "MISSING_STATUS",
                    "message": "Request body must include 'status' field",
                },
                "meta": {
                    "request_id": request.headers.get("X-Request-ID", "unknown"),
                    "ts": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                },
            },
            status_code=400,
        )
    
    success = storage.update_mission_status(mission_id, new_status, reason)
    if not success:
        return JSONResponse(
            {
                "ok": False,
                "error": {
                    "code": "MISSION_NOT_FOUND",
                    "message": f"Mission with ID '{mission_id}' does not exist",
                },
                "meta": {
                    "request_id": request.headers.get("X-Request-ID", "unknown"),
                    "ts": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                },
            },
            status_code=404,
        )
    
    mission = storage.get_mission(mission_id)
    
    response = JSONResponse(ok(request, {"mission": mission}), status_code=200)
    compute_ms = int((time.perf_counter() - start) * 1000)
    response.headers["X-Compute-Time-ms"] = str(compute_ms)
    return response


@router.get("/missions/{mission_id}/audit")
async def get_mission_audit_log(request: Request, mission_id: str):
    """
    Get detailed audit log for a mission.
    
    Returns the complete history of changes with human-readable explanations.
    Useful for understanding why priority changed, who made updates, etc.
    """
    start = time.perf_counter()
    
    mission = storage.get_mission(mission_id)
    if not mission:
        return JSONResponse(
            {
                "ok": False,
                "error": {
                    "code": "MISSION_NOT_FOUND",
                    "message": f"Mission with ID '{mission_id}' does not exist",
                },
                "meta": {
                    "request_id": request.headers.get("X-Request-ID", "unknown"),
                    "ts": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                },
            },
            status_code=404,
        )
    
    history = storage.get_mission_history(mission_id)
    
    # Enrich audit log with categorization
    audit_entries = []
    for entry in history:
        event_type = entry.get("event_type", "")
        
        # Categorize events
        category = "other"
        triggered_by = "system"
        
        if event_type == "created":
            category = "lifecycle"
            triggered_by = "system"
        elif event_type == "status_changed":
            category = "lifecycle"
            triggered_by = "user"  # Assume user triggered status changes
        elif event_type == "priority_changed":
            category = "priority"
            triggered_by = "system"  # Usually system recalculates priority
        
        audit_entry = {
            "id": f"audit_{mission_id}_{len(audit_entries) + 1}",
            "mission_id": mission_id,
            "timestamp": entry.get("timestamp"),
            "event_type": event_type,
            "category": category,
            "reason": entry.get("reason", ""),
            "data": entry.get("data", {}),
            "triggered_by": triggered_by,
        }
        audit_entries.append(audit_entry)
    
    # Summary statistics
    event_types = {}
    for entry in audit_entries:
        event_type = entry["event_type"]
        event_types[event_type] = event_types.get(event_type, 0) + 1
    
    data = {
        "mission_id": mission_id,
        "mission_title": mission.get("title"),
        "audit_log": audit_entries,
        "total_events": len(audit_entries),
        "event_summary": event_types,
        "first_event": audit_entries[0]["timestamp"] if audit_entries else None,
        "last_event": audit_entries[-1]["timestamp"] if audit_entries else None,
    }
    
    response = JSONResponse(ok(request, data), status_code=200)
    compute_ms = int((time.perf_counter() - start) * 1000)
    response.headers["X-Compute-Time-ms"] = str(compute_ms)
    return response
