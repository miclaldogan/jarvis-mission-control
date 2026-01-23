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
