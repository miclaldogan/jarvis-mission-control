from __future__ import annotations

import random
from datetime import datetime, timedelta, timezone
from typing import Any, Literal, Optional

from app.services.scoring import calculate_mission_score
from app.services.rule_packs import (
    evaluate_all_packs,
    find_scheduling_conflicts,
    GeneratedMission,
)


Priority = Literal["P1", "P2", "P3", "P4"]
Status = Literal["open", "done", "snoozed"]


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _iso_in_hours(hours: int) -> str:
    return (datetime.now(timezone.utc) + timedelta(hours=hours)).isoformat().replace(
        "+00:00", "Z"
    )


def _energy_bonus(energy_level: Optional[str]) -> float:
    if energy_level == "high":
        return 0.15
    if energy_level == "low":
        return -0.10
    return 0.0


def _priority_to_num(p: str) -> int:
    """Convert priority string to number for sorting."""
    return {"P1": 1, "P2": 2, "P3": 3, "P4": 4}.get(p, 5)


def generate_missions(
    *,
    context: dict[str, Any],
    preferences: Optional[dict[str, Any]] = None,
    limit: int = 15,
    seed: Optional[int] = None,
) -> list[dict[str, Any]]:
    """Generate a mission list using rule packs.

    Each mission has:
    - rule_pack: { pack, rule } showing exactly which pack/rule generated it
    - category, energy_cost, duration_minutes for taxonomy
    - scheduling.suggested_time, scheduling.conflicts for time hints
    """

    rng = random.Random(seed)
    preferences = preferences or {}
    context = context or {}
    
    # Get calendar events for conflict detection
    calendar = context.get("calendar") or {}
    calendar_events = calendar.get("events") or []

    # ═══════════════════════════════════════════════════════════════════
    # PHASE 1: Rule Pack Evaluation
    # ═══════════════════════════════════════════════════════════════════
    pack_missions = evaluate_all_packs(context, preferences)
    
    # Find scheduling conflicts
    find_scheduling_conflicts(pack_missions, calendar_events)
    
    # Convert GeneratedMission to dict format
    missions: list[dict[str, Any]] = []
    
    for idx, gm in enumerate(pack_missions, 1):
        # Calculate dynamic score for consistent scoring
        score = calculate_mission_score(
            due_at=gm.to_dict().get("deadline"),
            tags=gm.tags,
            context=context,
            preferences=preferences,
        )
        score_dict = score.to_dict()
        
        # Build comprehensive reasons including pack info
        reasons = [
            f"[{gm.pack_name}:{gm.rule_name}] {gm.why}",
            *score_dict["reasons"],
        ]
        
        missions.append({
            "id": f"msn_{idx:03d}",
            "title": gm.title,
            "priority": gm.priority,
            "priority_score": score_dict["total"],
            "score_breakdown": score_dict["breakdown"],
            "reasons": reasons,
            "status": "open",
            "due_at": gm.to_dict().get("deadline"),
            "tags": gm.tags,
            "why": gm.why,
            # New taxonomy fields
            "category": gm.category,
            "energy_cost": gm.energy_cost,
            "duration_minutes": gm.duration_minutes,
            # Rule pack traceability
            "rule_pack": {
                "pack": gm.pack_name,
                "rule": gm.rule_name,
            },
            # Scheduling hints
            "scheduling": {
                "suggested_time": gm.suggested_time,
                "conflicts": gm.conflicts,
            },
            "actions": [
                {"label": "Context detayına git", "type": "link", "target": "/context"}
            ],
            "evidence": {
                "sources": gm.sources,
                "confidence": gm.confidence,
            },
            "generated_at": _now_iso(),
        })

    # ═══════════════════════════════════════════════════════════════════
    # PHASE 2: Filler Tasks (if needed)
    # ═══════════════════════════════════════════════════════════════════
    filler_tasks = [
        {
            "title": "Bugünün 3 hedefini yaz",
            "priority": "P3",
            "category": "admin",
            "energy_cost": "low",
            "duration_minutes": 10,
            "tags": ["planning", "routine"],
            "why": "Günlük hedef belirleme odaklanmayı artırır.",
            "pack": "routine",
            "rule": "daily_goals",
        },
        {
            "title": "Inbox temizliği (10dk)",
            "priority": "P3",
            "category": "admin",
            "energy_cost": "low",
            "duration_minutes": 10,
            "tags": ["email", "routine"],
            "why": "Düzenli inbox temizliği zihin yorgunluğunu azaltır.",
            "pack": "routine",
            "rule": "inbox_zero",
        },
        {
            "title": "1 saat deep work bloğu ayır",
            "priority": "P2",
            "category": "work",
            "energy_cost": "high",
            "duration_minutes": 60,
            "tags": ["focus", "productivity"],
            "why": "Kesintisiz çalışma kaliteyi artırır. Optimum saat: 09:00-11:00.",
            "pack": "routine",
            "rule": "deep_work",
            "suggested_time": "09:00-10:00 veya 14:00-15:00",
        },
        {
            "title": "Kısa mola + su iç",
            "priority": "P4",
            "category": "health",
            "energy_cost": "low",
            "duration_minutes": 5,
            "tags": ["health", "break"],
            "why": "Düzenli mola ve hidrasyon performansı korur.",
            "pack": "routine",
            "rule": "hydration_break",
        },
        {
            "title": "Yarın için 1 risk notu",
            "priority": "P3",
            "category": "admin",
            "energy_cost": "low",
            "duration_minutes": 5,
            "tags": ["planning", "risk"],
            "why": "Proaktif risk notu, sürpriz engeller.",
            "pack": "routine",
            "rule": "risk_note",
        },
        {
            "title": "5dk germe egzersizi",
            "priority": "P4",
            "category": "health",
            "energy_cost": "low",
            "duration_minutes": 5,
            "tags": ["health", "stretch"],
            "why": "Masa başı çalışanlar için 2 saatte bir germe önerilir.",
            "pack": "routine",
            "rule": "stretch_break",
        },
        {
            "title": "Bir sonraki toplantıyı gözden geçir",
            "priority": "P3",
            "category": "work",
            "energy_cost": "low",
            "duration_minutes": 5,
            "tags": ["meeting", "prep"],
            "why": "Toplantı öncesi 5dk hazırlık, verimlilik artırır.",
            "pack": "routine",
            "rule": "meeting_prep",
        },
    ]

    used_fillers: set[str] = set()
    
    while len(missions) < limit and len(used_fillers) < len(filler_tasks):
        filler = rng.choice([f for f in filler_tasks if f["title"] not in used_fillers])
        used_fillers.add(filler["title"])
        
        idx = len(missions) + 1
        missions.append({
            "id": f"msn_{idx:03d}",
            "title": filler["title"],
            "priority": filler["priority"],
            "priority_score": 40.0,
            "score_breakdown": {"base": 40, "routine": 0},
            "reasons": [f"[{filler['pack']}:{filler['rule']}] {filler['why']}"],
            "status": "open",
            "due_at": None,
            "tags": filler["tags"],
            "why": filler["why"],
            "category": filler["category"],
            "energy_cost": filler["energy_cost"],
            "duration_minutes": filler["duration_minutes"],
            "rule_pack": {
                "pack": filler["pack"],
                "rule": filler["rule"],
            },
            "scheduling": {
                "suggested_time": filler.get("suggested_time"),
                "conflicts": [],
            },
            "actions": [{"label": "Lab'a git", "type": "link", "target": "/lab"}],
            "evidence": {
                "sources": ["synthetic"],
                "confidence": 0.5,
            },
            "generated_at": _now_iso(),
        })

    # ═══════════════════════════════════════════════════════════════════
    # PHASE 3: Sort by priority and return
    # ═══════════════════════════════════════════════════════════════════
    missions.sort(key=lambda m: (_priority_to_num(m["priority"]), -m.get("priority_score", 0)))

    return missions[:limit]
