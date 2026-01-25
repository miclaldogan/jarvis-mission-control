"""
Brain API Endpoints - The Explainable AI Layer

Exposes the autonomous system's decision-making process:
- System state and metrics
- Signal detection results
- Rule evaluation results
- Auto-generated missions with full explainability
"""

from __future__ import annotations

import time
from datetime import datetime, timezone
from typing import Any, Optional

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from app.http_envelope import ok, err
from app.services.context import build_context_snapshot
from app.services.signal_engine import get_signal_engine, analyze_context as analyze_signals
from app.services.rule_engine import get_rule_engine, evaluate_rules
from app.services.orchestrator import get_orchestrator, process_context


router = APIRouter()


class ProcessContextRequest(BaseModel):
    """Request to process context through the brain."""
    context: Optional[dict[str, Any]] = None
    
    # Metric overrides for testing
    cpu_load: Optional[float] = Field(None, ge=0, le=1)
    memory_load: Optional[float] = Field(None, ge=0, le=1)
    network_load: Optional[float] = Field(None, ge=0, le=1)


class UpdateMetricsRequest(BaseModel):
    """Request to update system metrics."""
    task_count: Optional[int] = Field(None, ge=0)
    cpu_load: Optional[float] = Field(None, ge=0, le=1)
    memory_load: Optional[float] = Field(None, ge=0, le=1)
    network_load: Optional[float] = Field(None, ge=0, le=1)
    queue_pressure: Optional[float] = Field(None, ge=0, le=1)


class MissionActionRequest(BaseModel):
    """Request to complete or dismiss a mission."""
    mission_id: str


@router.get("/brain/status")
async def get_brain_status(request: Request):
    """
    Get the current brain status including:
    - System state (CALM/ACTIVE/OVERLOAD/RECOVERY)
    - Metrics (cognitive_load, system_pressure)
    - Pending missions count
    - Engine statuses
    """
    start = time.perf_counter()
    
    orchestrator = get_orchestrator()
    signal_engine = get_signal_engine()
    rule_engine = get_rule_engine()
    
    status = {
        "system": orchestrator.get_status(),
        "engines": {
            "signal_engine": signal_engine.get_status(),
            "rule_engine": rule_engine.get_status(),
        },
        "computed_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }
    
    response = JSONResponse(ok(request, status))
    response.headers["X-Compute-Time-ms"] = str(int((time.perf_counter() - start) * 1000))
    return response


@router.post("/brain/process")
async def process_brain(request: Request, body: ProcessContextRequest):
    """
    Main brain processing endpoint.
    
    Flow:
    1. Get or build context
    2. Detect signals from context
    3. Evaluate rules against signals
    4. Generate missions from fired rules
    5. Update system state
    
    Returns full explainability chain.
    """
    start = time.perf_counter()
    
    # Get context
    context = body.context
    if context is None:
        context = await build_context_snapshot(debug=False)
    
    # Update metrics if provided
    orchestrator = get_orchestrator()
    if any([body.cpu_load, body.memory_load, body.network_load]):
        orchestrator.update_metrics(
            cpu_load=body.cpu_load,
            memory_load=body.memory_load,
            network_load=body.network_load,
        )
    
    # Process context through brain
    result = process_context(context)
    
    # Add context summary
    result["context_summary"] = {
        "context_id": context.get("context_id"),
        "observed_at": context.get("observed_at"),
        "sources": {
            "weather": bool(context.get("weather")),
            "github": bool(context.get("github")),
            "news": bool(context.get("news")),
            "calendar": bool(context.get("calendar")),
            "exchange": bool(context.get("exchange")),
        },
    }
    
    response = JSONResponse(ok(request, result))
    response.headers["X-Compute-Time-ms"] = str(int((time.perf_counter() - start) * 1000))
    return response


@router.get("/brain/signals")
async def get_signals(request: Request):
    """
    Analyze current context for signals without generating missions.
    Useful for monitoring signal detection.
    """
    start = time.perf_counter()
    
    context = await build_context_snapshot(debug=False)
    signals = analyze_signals(context)
    
    result = {
        "context_id": context.get("context_id"),
        "signals_count": len(signals),
        "signals": [s.to_dict() for s in signals],
        "by_source": {},
        "by_type": {},
        "by_severity": {},
    }
    
    # Group signals
    for sig in signals:
        result["by_source"].setdefault(sig.source, []).append(sig.id)
        result["by_type"].setdefault(sig.type.value, []).append(sig.id)
        result["by_severity"].setdefault(sig.severity.value, []).append(sig.id)
    
    response = JSONResponse(ok(request, result))
    response.headers["X-Compute-Time-ms"] = str(int((time.perf_counter() - start) * 1000))
    return response


@router.get("/brain/rules")
async def get_rules(request: Request):
    """
    Get all rules and their current status.
    Shows which rules are enabled, their cooldowns, and fire counts.
    """
    rule_engine = get_rule_engine()
    
    result = {
        "total_rules": len(rule_engine.rules),
        "enabled_rules": sum(1 for r in rule_engine.rules if r.enabled),
        "rules": [r.to_dict() for r in rule_engine.rules],
        "templates": list(rule_engine.templates.keys()),
    }
    
    return JSONResponse(ok(request, result))


@router.post("/brain/rules/{rule_id}/enable")
async def enable_rule(request: Request, rule_id: str):
    """Enable a specific rule."""
    rule_engine = get_rule_engine()
    
    if rule_engine.enable_rule(rule_id):
        return JSONResponse(ok(request, {"rule_id": rule_id, "enabled": True}))
    
    return JSONResponse(
        *err(request, code="RULE_NOT_FOUND", message=f"Rule '{rule_id}' not found", status_code=404)
    )


@router.post("/brain/rules/{rule_id}/disable")
async def disable_rule(request: Request, rule_id: str):
    """Disable a specific rule."""
    rule_engine = get_rule_engine()
    
    if rule_engine.disable_rule(rule_id):
        return JSONResponse(ok(request, {"rule_id": rule_id, "enabled": False}))
    
    return JSONResponse(
        *err(request, code="RULE_NOT_FOUND", message=f"Rule '{rule_id}' not found", status_code=404)
    )


@router.get("/brain/missions/pending")
async def get_pending_missions(request: Request):
    """Get all pending auto-generated missions."""
    orchestrator = get_orchestrator()
    missions = orchestrator.get_pending_missions()
    
    result = {
        "count": len(missions),
        "missions": [m.to_dict() for m in missions],
        "system_state": orchestrator.state.value,
    }
    
    return JSONResponse(ok(request, result))


@router.post("/brain/missions/complete")
async def complete_mission(request: Request, body: MissionActionRequest):
    """Mark a mission as completed."""
    orchestrator = get_orchestrator()
    
    if orchestrator.complete_mission(body.mission_id):
        return JSONResponse(ok(request, {"mission_id": body.mission_id, "status": "completed"}))
    
    return JSONResponse(
        *err(request, code="MISSION_NOT_FOUND", message=f"Mission '{body.mission_id}' not found", status_code=404)
    )


@router.post("/brain/missions/dismiss")
async def dismiss_mission(request: Request, body: MissionActionRequest):
    """Dismiss a mission."""
    orchestrator = get_orchestrator()
    
    if orchestrator.dismiss_mission(body.mission_id):
        return JSONResponse(ok(request, {"mission_id": body.mission_id, "status": "dismissed"}))
    
    return JSONResponse(
        *err(request, code="MISSION_NOT_FOUND", message=f"Mission '{body.mission_id}' not found", status_code=404)
    )


@router.post("/brain/metrics")
async def update_metrics(request: Request, body: UpdateMetricsRequest):
    """
    Update system metrics manually.
    Useful for testing state transitions.
    """
    orchestrator = get_orchestrator()
    
    orchestrator.update_metrics(
        task_count=body.task_count,
        cpu_load=body.cpu_load,
        memory_load=body.memory_load,
        network_load=body.network_load,
        queue_pressure=body.queue_pressure,
    )
    
    return JSONResponse(ok(request, {
        "state": orchestrator.state.value,
        "metrics": orchestrator.metrics.to_dict(),
    }))


@router.get("/brain/explain/{mission_id}")
async def explain_mission(request: Request, mission_id: str):
    """
    Get full explainability chain for a specific mission.
    Shows exactly why this mission was generated.
    """
    orchestrator = get_orchestrator()
    
    # Search in pending, completed, and dismissed
    all_missions = list(orchestrator._pending_missions) + \
                   list(orchestrator._completed_missions) + \
                   list(orchestrator._dismissed_missions)
    
    for mission in all_missions:
        if mission.id == mission_id:
            return JSONResponse(ok(request, {
                "mission": mission.to_dict(),
                "explanation": {
                    "summary": f"Bu görev '{mission.source_rule_name}' kuralı tarafından oluşturuldu.",
                    "decision_chain": mission.decision_chain,
                    "confidence": mission.confidence,
                    "system_state_at_creation": mission.system_state.value,
                    "trigger_signals": mission.trigger_signals,
                },
            }))
    
    return JSONResponse(
        *err(request, code="MISSION_NOT_FOUND", message=f"Mission '{mission_id}' not found", status_code=404)
    )


@router.get("/brain/state-machine")
async def get_state_machine(request: Request):
    """
    Get state machine info including:
    - Current state
    - State descriptions
    - Transition rules
    - Recent state history
    """
    orchestrator = get_orchestrator()
    
    result = {
        "current_state": orchestrator.state.value,
        "description": orchestrator._get_state_description(),
        "states": {
            "calm": {
                "description": "Sistem sakin. Optimizasyon görevleri önerilir.",
                "task_types": ["optimization", "planning", "learning"],
            },
            "active": {
                "description": "Normal aktivite. Verimlilik görevleri önerilir.",
                "task_types": ["productivity", "execution", "communication"],
            },
            "overload": {
                "description": "⚠️ Sistem yoğun! Sadece kritik görevler kabul ediliyor.",
                "task_types": ["critical_only", "load_shedding"],
            },
            "recovery": {
                "description": "Sistem toparlanıyor. Stabilizasyon görevleri önerilir.",
                "task_types": ["stabilization", "cleanup", "rest"],
            },
        },
        "transitions": [
            {"from": "calm", "to": "active", "trigger": "pressure >= 0.3"},
            {"from": "active", "to": "overload", "trigger": "pressure >= 0.7 OR cognitive >= 0.9"},
            {"from": "overload", "to": "recovery", "trigger": "pressure < 0.7"},
            {"from": "recovery", "to": "calm", "trigger": "5 minutes elapsed"},
        ],
        "thresholds": orchestrator.state_thresholds,
        "recent_history": [
            {"timestamp": ts, "state": s.value}
            for ts, s in list(orchestrator._state_history)[-10:]
        ],
        "metrics": orchestrator.metrics.to_dict(),
    }
    
    return JSONResponse(ok(request, result))
