"""
Mission Priority Scoring System with Explainability

Calculates priority scores based on multiple factors:
- Deadline urgency (40%)
- Context match (30%)
- Energy fit (20%)
- User preference (10%)
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional


class PriorityScore:
    """Priority score breakdown for explainability"""
    
    def __init__(
        self,
        deadline: float = 0.0,
        context: float = 0.0,
        energy: float = 0.0,
        preference: float = 0.0,
    ):
        self.deadline = max(0.0, min(1.0, deadline))
        self.context = max(0.0, min(1.0, context))
        self.energy = max(0.0, min(1.0, energy))
        self.preference = max(0.0, min(1.0, preference))
    
    @property
    def total(self) -> float:
        """Weighted sum of all components"""
        return (
            self.deadline * 0.4 +
            self.context * 0.3 +
            self.energy * 0.2 +
            self.preference * 0.1
        )
    
    @property
    def priority_level(self) -> str:
        """Convert numeric score to P1-P4"""
        if self.total >= 0.8:
            return "P1"
        elif self.total >= 0.6:
            return "P2"
        elif self.total >= 0.4:
            return "P3"
        else:
            return "P4"
    
    def to_dict(self) -> dict[str, Any]:
        """Serialize for API response"""
        return {
            "total": round(self.total, 3),
            "priority": self.priority_level,
            "breakdown": {
                "deadline": round(self.deadline, 3),
                "context": round(self.context, 3),
                "energy": round(self.energy, 3),
                "preference": round(self.preference, 3),
            },
            "reasons": self.generate_reasons(),
        }
    
    def generate_reasons(self) -> list[str]:
        """Generate human-readable reason strings"""
        reasons = []
        
        if self.deadline > 0.7:
            reasons.append(f"🔴 Urgent deadline (+{self.deadline:.2f})")
        elif self.deadline > 0.4:
            reasons.append(f"🟡 Approaching deadline (+{self.deadline:.2f})")
        elif self.deadline > 0:
            reasons.append(f"🟢 Flexible deadline (+{self.deadline:.2f})")
        
        if self.context > 0.6:
            reasons.append(f"✅ High context match (+{self.context:.2f})")
        elif self.context > 0.3:
            reasons.append(f"➡️ Moderate context match (+{self.context:.2f})")
        
        if self.energy > 0.5:
            reasons.append(f"⚡ Good energy fit (+{self.energy:.2f})")
        elif self.energy < 0.3:
            reasons.append(f"⚠️ Low energy fit (+{self.energy:.2f})")
        
        if self.preference > 0.5:
            reasons.append(f"💙 User preference (+{self.preference:.2f})")
        
        return reasons


def calculate_deadline_score(due_at: Optional[str]) -> float:
    """
    Calculate urgency score based on deadline.
    
    Returns:
        1.0 - Very urgent (< 2 hours)
        0.8 - Urgent (2-6 hours)
        0.6 - Soon (6-24 hours)
        0.4 - This week (1-7 days)
        0.2 - Later (> 7 days)
        0.0 - No deadline
    """
    if not due_at:
        return 0.0
    
    try:
        deadline = datetime.fromisoformat(due_at.replace("Z", "+00:00"))
        now = datetime.now(timezone.utc)
        hours_until = (deadline - now).total_seconds() / 3600
        
        if hours_until < 0:
            return 1.0  # Overdue!
        elif hours_until < 2:
            return 0.95
        elif hours_until < 6:
            return 0.8
        elif hours_until < 24:
            return 0.6
        elif hours_until < 168:  # 7 days
            return 0.4
        else:
            return 0.2
    except Exception:
        return 0.0


def calculate_context_score(
    tags: list[str],
    context: dict[str, Any],
) -> float:
    """
    Calculate context match score based on current conditions.
    
    High scores when:
    - Weather tags match current weather
    - GitHub tags match high workload
    - News tags when breaking news available
    """
    if not tags:
        return 0.3  # Default moderate score
    
    if context is None:
        context = {}
    
    score = 0.0
    
    # Weather context
    weather = context.get("weather") or {}
    condition = (weather.get("condition") or "").lower()
    
    if "weather" in tags:
        if condition in ("rain", "snow", "storm"):
            score += 0.35  # High match for bad weather tasks
        else:
            score += 0.15  # Lower match for good weather
    
    # GitHub context
    github = context.get("github") or {}
    open_prs = github.get("open_prs", 0) or 0
    open_issues = github.get("open_issues", 0) or 0
    
    if "github" in tags:
        if open_prs >= 5 or open_issues >= 15:
            score += 0.35  # High match when backlog is high
        elif open_prs > 0 or open_issues > 0:
            score += 0.20
        else:
            score += 0.10
    
    # Planning/routine tasks have moderate baseline
    if "planning" in tags or "routine" in tags:
        score += 0.20
    
    # Delivery/critical tags boost
    if "delivery" in tags or "critical" in tags:
        score += 0.25
    
    return min(1.0, score)


def calculate_energy_score(
    tags: list[str],
    energy_level: Optional[str] = None,
) -> float:
    """
    Calculate energy fit score.
    
    - High energy: Complex/planning tasks score higher
    - Low energy: Routine/simple tasks score higher
    - Medium/unknown: Neutral scores
    """
    if energy_level == "high":
        # Favor complex tasks
        if any(tag in tags for tag in ["planning", "github", "delivery"]):
            return 0.8
        else:
            return 0.5
    
    elif energy_level == "low":
        # Favor simple tasks
        if any(tag in tags for tag in ["routine", "awareness"]):
            return 0.7
        else:
            return 0.3
    
    else:
        # Neutral
        return 0.5


def calculate_preference_score(
    tags: list[str],
    preferences: Optional[dict[str, Any]] = None,
) -> float:
    """
    Calculate user preference score.
    
    Based on preferred task categories.
    """
    if not preferences:
        return 0.5  # Neutral
    
    preferred_tags = preferences.get("preferred_tags", [])
    
    if not preferred_tags:
        return 0.5
    
    # Check tag overlap
    overlap = len(set(tags) & set(preferred_tags))
    
    if overlap >= 2:
        return 0.9
    elif overlap == 1:
        return 0.7
    else:
        return 0.3


def calculate_mission_score(
    *,
    due_at: Optional[str],
    tags: list[str],
    context: dict[str, Any],
    preferences: Optional[dict[str, Any]] = None,
) -> PriorityScore:
    """
    Calculate complete priority score with breakdown.
    
    Returns PriorityScore object with all components.
    """
    energy_level = preferences.get("energy_level") if preferences else None
    
    return PriorityScore(
        deadline=calculate_deadline_score(due_at),
        context=calculate_context_score(tags, context),
        energy=calculate_energy_score(tags, energy_level),
        preference=calculate_preference_score(tags, preferences),
    )
