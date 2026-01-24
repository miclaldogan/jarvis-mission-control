"""Additional Mission & Context Endpoints.

Implements Issue #83:
- POST /api/v1/context/ingest - Manual context push
- GET /api/v1/missions/today - Today's missions
- POST /api/v1/missions/complete/{id} - Mark mission complete
- GET /api/v1/missions/history - Historical data
"""

from __future__ import annotations

import time
import uuid
from datetime import datetime, timezone
from typing import Any, List, Literal, Optional

from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from app.http_envelope import ok
from app.db import init_db
from app.db.models import Mission, ContextSnapshot
from app.db.repository import MissionRepository, ContextRepository


router = APIRouter()


# Initialize database on module load
init_db()


# ============================================================================
# Request/Response Models
# ============================================================================

class ContextIngestRequest(BaseModel):
    """Request body for manual context ingestion."""
    source: str = Field(..., description="Context source name (e.g., 'calendar', 'custom')")
    data: dict[str, Any] = Field(..., description="Context data payload")
    ttl_seconds: int = Field(120, ge=60, le=86400, description="TTL in seconds (1min - 24h)")
    regenerate_missions: bool = Field(False, description="Trigger mission regeneration")


class ContextIngestResponse(BaseModel):
    """Response for context ingestion."""
    id: str
    run_id: str
    source: str
    ingested_at: str
    ttl_seconds: int
    message: str


class MissionCompleteRequest(BaseModel):
    """Optional request body for completion."""
    notes: Optional[str] = Field(None, max_length=500, description="Completion notes")


class MissionCompleteResponse(BaseModel):
    """Response for mission completion."""
    id: str
    title: str
    status: str
    completed_at: str
    message: str


class MissionHistoryResponse(BaseModel):
    """Response for mission history."""
    missions: List[dict[str, Any]]
    total: int
    stats: dict[str, Any]


class TodayMissionsResponse(BaseModel):
    """Response for today's missions."""
    missions: List[dict[str, Any]]
    count: int
    date: str


# ============================================================================
# Helper Functions
# ============================================================================

def _utc_now_iso() -> str:
    """Get current UTC timestamp in ISO format."""
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _today_date() -> str:
    """Get today's date in YYYY-MM-DD format."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _generate_run_id() -> str:
    """Generate unique run ID."""
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    short_uuid = uuid.uuid4().hex[:6]
    return f"run_{timestamp}_{short_uuid}"


# ============================================================================
# Endpoints
# ============================================================================

@router.post("/context/ingest", response_model=ContextIngestResponse)
async def ingest_context(request: Request, body: ContextIngestRequest):
    """
    Manually push context data from custom sources.
    
    Use this endpoint to:
    - Inject custom context (e.g., from external systems)
    - Override or supplement automatic context ingestion
    - Test mission generation with specific context
    
    Args:
        source: Name of the context source (e.g., 'calendar', 'custom_api')
        data: Context payload (any valid JSON object)
        ttl_seconds: How long to keep this context (default 120s)
        regenerate_missions: Trigger immediate mission regeneration
    
    Returns:
        Created context snapshot with ID and timestamps
    """
    start = time.perf_counter()
    
    run_id = _generate_run_id()
    snapshot_id = f"ctx_{uuid.uuid4().hex[:12]}"
    
    snapshot = ContextSnapshot(
        id=snapshot_id,
        run_id=run_id,
        source=body.source,
        data=body.data,
        ingested_at=_utc_now_iso(),
        ttl_seconds=body.ttl_seconds,
        is_synthetic=False,
    )
    
    # Persist to database
    ContextRepository.create(snapshot)
    
    # TODO: If regenerate_missions is True, trigger mission generation
    # This would integrate with the existing /missions/generate endpoint
    
    response_data = ContextIngestResponse(
        id=snapshot.id,
        run_id=snapshot.run_id,
        source=snapshot.source,
        ingested_at=snapshot.ingested_at,
        ttl_seconds=snapshot.ttl_seconds,
        message=f"Context ingested successfully from '{body.source}'"
    )
    
    response = JSONResponse(ok(request, response_data.model_dump()), status_code=201)
    compute_ms = int((time.perf_counter() - start) * 1000)
    response.headers["X-Compute-Time-ms"] = str(compute_ms)
    return response


@router.get("/missions/today", response_model=TodayMissionsResponse)
async def get_today_missions(request: Request):
    """
    Get missions for today.
    
    Returns all missions that are:
    - Created today
    - Due today
    - Open with no due date (ongoing tasks)
    
    Sorted by priority score (highest first), then by due date.
    """
    start = time.perf_counter()
    
    missions = MissionRepository.get_today()
    
    response_data = TodayMissionsResponse(
        missions=[m.to_dict() for m in missions],
        count=len(missions),
        date=_today_date(),
    )
    
    response = JSONResponse(ok(request, response_data.model_dump()))
    compute_ms = int((time.perf_counter() - start) * 1000)
    response.headers["X-Compute-Time-ms"] = str(compute_ms)
    return response


@router.post("/missions/complete/{mission_id}", response_model=MissionCompleteResponse)
async def complete_mission(
    request: Request,
    mission_id: str,
    body: Optional[MissionCompleteRequest] = None,
):
    """
    Mark a mission as completed.
    
    Updates the mission status to 'done' and records the completion timestamp.
    Optionally accepts completion notes.
    
    Args:
        mission_id: The ID of the mission to complete
        notes: Optional completion notes or summary
    
    Returns:
        Updated mission object with completion timestamp
    
    Raises:
        404: Mission not found
        400: Mission already completed
    """
    start = time.perf_counter()
    
    # Get existing mission
    mission = MissionRepository.get_by_id(mission_id)
    
    if not mission:
        raise HTTPException(status_code=404, detail=f"Mission '{mission_id}' not found")
    
    if mission.status == "done":
        raise HTTPException(status_code=400, detail="Mission already completed")
    
    # Mark as complete
    completed_mission = MissionRepository.complete(mission_id)
    
    if not completed_mission:
        raise HTTPException(status_code=500, detail="Failed to complete mission")
    
    response_data = MissionCompleteResponse(
        id=completed_mission.id,
        title=completed_mission.title,
        status=completed_mission.status,
        completed_at=completed_mission.completed_at or _utc_now_iso(),
        message=f"Mission '{completed_mission.title}' marked as complete"
    )
    
    response = JSONResponse(ok(request, response_data.model_dump()))
    compute_ms = int((time.perf_counter() - start) * 1000)
    response.headers["X-Compute-Time-ms"] = str(compute_ms)
    return response


@router.get("/missions/history", response_model=MissionHistoryResponse)
async def get_mission_history(
    request: Request,
    start_date: Optional[str] = Query(None, description="Start date (ISO format)"),
    end_date: Optional[str] = Query(None, description="End date (ISO format)"),
    status: str = Query("done", description="Filter by status"),
    limit: int = Query(100, ge=1, le=1000, description="Max results"),
    format: Literal["json", "csv"] = Query("json", description="Response format"),
):
    """
    Get historical mission data.
    
    Returns completed missions with optional date range filtering.
    Includes aggregated statistics for the queried period.
    
    Args:
        start_date: Filter missions completed after this date
        end_date: Filter missions completed before this date
        status: Filter by status (default: 'done')
        limit: Maximum number of results (default: 100)
        format: Response format ('json' or 'csv')
    
    Returns:
        List of missions with completion stats
    """
    start = time.perf_counter()
    
    # Get missions
    missions = MissionRepository.get_history(
        start_date=start_date,
        end_date=end_date,
        status=status,
        limit=limit,
    )
    
    # Get stats for the same period
    stats = MissionRepository.get_completion_stats(
        start_date=start_date,
        end_date=end_date,
    )
    
    response_data = MissionHistoryResponse(
        missions=[m.to_dict() for m in missions],
        total=len(missions),
        stats=stats,
    )
    
    # Handle CSV format
    if format == "csv":
        import csv
        import io
        
        output = io.StringIO()
        if missions:
            writer = csv.DictWriter(output, fieldnames=missions[0].to_dict().keys())
            writer.writeheader()
            for m in missions:
                writer.writerow(m.to_dict())
        
        csv_content = output.getvalue()
        return JSONResponse(
            content={"csv": csv_content, "total": len(missions)},
            headers={
                "Content-Type": "application/json",
                "X-Compute-Time-ms": str(int((time.perf_counter() - start) * 1000)),
            },
        )
    
    response = JSONResponse(ok(request, response_data.model_dump()))
    compute_ms = int((time.perf_counter() - start) * 1000)
    response.headers["X-Compute-Time-ms"] = str(compute_ms)
    return response


@router.get("/context/history")
async def get_context_history(
    request: Request,
    source: Optional[str] = Query(None, description="Filter by source"),
    start_date: Optional[str] = Query(None, description="Start date (ISO format)"),
    end_date: Optional[str] = Query(None, description="End date (ISO format)"),
    limit: int = Query(100, ge=1, le=1000, description="Max results"),
):
    """
    Get historical context snapshots.
    
    Returns past context data for analysis and debugging.
    """
    start = time.perf_counter()
    
    snapshots = ContextRepository.get_history(
        source=source,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
    )
    
    response_data = {
        "snapshots": [s.to_dict() for s in snapshots],
        "total": len(snapshots),
    }
    
    response = JSONResponse(ok(request, response_data))
    compute_ms = int((time.perf_counter() - start) * 1000)
    response.headers["X-Compute-Time-ms"] = str(compute_ms)
    return response
