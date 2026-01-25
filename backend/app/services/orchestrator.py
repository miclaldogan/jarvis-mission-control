"""
Mission Orchestrator - The Coordination Layer of JARVIS

Manages the complete mission lifecycle:
- Auto-generation from signals and rules
- Priority management and deduplication
- System state machine (CALM → ACTIVE → OVERLOAD → RECOVERY)
- Cognitive load and system pressure tracking

System States:
- CALM: Low activity, focus on optimization
- ACTIVE: Normal activity, productivity tasks
- OVERLOAD: High pressure, load shedding
- RECOVERY: Post-overload, stabilization
"""

from __future__ import annotations

import time
import uuid
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

from app.services.signal_engine import Signal, SignalType, SignalSeverity, get_signal_engine
from app.services.rule_engine import Rule, Action, ActionType, RuleResult, get_rule_engine


class SystemState(str, Enum):
    CALM = "calm"
    ACTIVE = "active"
    OVERLOAD = "overload"
    RECOVERY = "recovery"


@dataclass
class SystemMetrics:
    """Real-time system metrics."""
    # Task metrics
    task_count: int = 0
    optimal_task_count: int = 8
    
    # Pressure metrics (0-1 scale)
    cpu_load: float = 0.0
    memory_load: float = 0.0
    network_load: float = 0.0
    queue_pressure: float = 0.0
    
    # Derived indices
    cognitive_load: float = 0.0  # task_count / optimal_task_count
    system_pressure: float = 0.0  # weighted avg of loads
    
    def compute_cognitive_load(self) -> float:
        """Compute cognitive load index."""
        if self.optimal_task_count <= 0:
            return 1.0
        self.cognitive_load = min(1.0, self.task_count / self.optimal_task_count)
        return self.cognitive_load
    
    def compute_system_pressure(self) -> float:
        """Compute overall system pressure."""
        # Weighted average: CPU 30%, Memory 25%, Network 20%, Queue 25%
        self.system_pressure = (
            self.cpu_load * 0.30 +
            self.memory_load * 0.25 +
            self.network_load * 0.20 +
            self.queue_pressure * 0.25
        )
        return self.system_pressure
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "task_count": self.task_count,
            "optimal_task_count": self.optimal_task_count,
            "cognitive_load": round(self.cognitive_load, 3),
            "system_pressure": round(self.system_pressure, 3),
            "breakdown": {
                "cpu_load": round(self.cpu_load, 3),
                "memory_load": round(self.memory_load, 3),
                "network_load": round(self.network_load, 3),
                "queue_pressure": round(self.queue_pressure, 3),
            },
        }


@dataclass
class AutoMission:
    """A mission generated automatically by the orchestrator."""
    id: str
    title: str
    priority: str  # P1-P4
    category: str
    energy_cost: str
    duration_minutes: int
    tags: list[str]
    why: str
    
    # Auto-generation metadata
    source_rule_id: str
    source_rule_name: str
    trigger_signals: list[str]
    system_state: SystemState
    
    # Explainability chain
    decision_chain: list[dict[str, Any]]
    confidence: float
    
    # Lifecycle
    status: str = "pending"  # pending, active, completed, dismissed
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"))
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "priority": self.priority,
            "category": self.category,
            "energy_cost": self.energy_cost,
            "duration_minutes": self.duration_minutes,
            "tags": self.tags,
            "why": self.why,
            "auto_generated": True,
            "source": {
                "rule_id": self.source_rule_id,
                "rule_name": self.source_rule_name,
                "trigger_signals": self.trigger_signals,
                "system_state": self.system_state.value,
            },
            "explainability": {
                "decision_chain": self.decision_chain,
                "confidence": self.confidence,
            },
            "status": self.status,
            "created_at": self.created_at,
        }


class MissionOrchestrator:
    """
    Central coordination for autonomous mission management.
    
    Responsibilities:
    - Monitor context changes
    - Detect signals
    - Evaluate rules
    - Generate missions
    - Manage system state
    - Track cognitive load
    """
    
    def __init__(self):
        self._state = SystemState.CALM
        self._metrics = SystemMetrics()
        self._pending_missions: deque[AutoMission] = deque(maxlen=50)
        self._completed_missions: deque[AutoMission] = deque(maxlen=100)
        self._dismissed_missions: deque[AutoMission] = deque(maxlen=50)
        
        self._state_history: deque[tuple[float, SystemState]] = deque(maxlen=100)
        self._last_context: Optional[dict[str, Any]] = None
        self._cycle_count = 0
        
        # State transition thresholds
        self.state_thresholds = {
            "overload_pressure": 0.7,
            "overload_cognitive": 0.9,
            "active_pressure": 0.3,
            "calm_pressure": 0.2,
            "recovery_duration": 300,  # 5 minutes in recovery before calm
        }
        
        self._recovery_start: Optional[float] = None
    
    @property
    def state(self) -> SystemState:
        return self._state
    
    @property
    def metrics(self) -> SystemMetrics:
        return self._metrics
    
    def _compute_state(self) -> SystemState:
        """Determine system state based on metrics."""
        pressure = self._metrics.system_pressure
        cognitive = self._metrics.cognitive_load
        
        # Check for overload
        if (pressure >= self.state_thresholds["overload_pressure"] or
            cognitive >= self.state_thresholds["overload_cognitive"]):
            self._recovery_start = None
            return SystemState.OVERLOAD
        
        # Check for recovery (after overload)
        if self._state == SystemState.OVERLOAD:
            self._recovery_start = time.time()
            return SystemState.RECOVERY
        
        # Check for recovery completion
        if self._state == SystemState.RECOVERY:
            if self._recovery_start:
                elapsed = time.time() - self._recovery_start
                if elapsed >= self.state_thresholds["recovery_duration"]:
                    self._recovery_start = None
                    return SystemState.CALM
            return SystemState.RECOVERY
        
        # Check for active vs calm
        if pressure >= self.state_thresholds["active_pressure"]:
            return SystemState.ACTIVE
        
        return SystemState.CALM
    
    def _update_state(self) -> bool:
        """Update system state and return True if changed."""
        new_state = self._compute_state()
        if new_state != self._state:
            self._state_history.append((time.time(), self._state))
            self._state = new_state
            return True
        return False
    
    def update_metrics(
        self,
        task_count: Optional[int] = None,
        cpu_load: Optional[float] = None,
        memory_load: Optional[float] = None,
        network_load: Optional[float] = None,
        queue_pressure: Optional[float] = None,
    ) -> None:
        """Update system metrics."""
        if task_count is not None:
            self._metrics.task_count = task_count
        if cpu_load is not None:
            self._metrics.cpu_load = min(1.0, max(0.0, cpu_load))
        if memory_load is not None:
            self._metrics.memory_load = min(1.0, max(0.0, memory_load))
        if network_load is not None:
            self._metrics.network_load = min(1.0, max(0.0, network_load))
        if queue_pressure is not None:
            self._metrics.queue_pressure = min(1.0, max(0.0, queue_pressure))
        
        self._metrics.compute_cognitive_load()
        self._metrics.compute_system_pressure()
        self._update_state()
    
    def process_context(self, context: dict[str, Any]) -> dict[str, Any]:
        """
        Main processing cycle.
        
        1. Analyze context for signals
        2. Evaluate rules against signals
        3. Generate missions from fired rules
        4. Update metrics and state
        
        Returns processing result with signals, rules fired, and new missions.
        """
        self._cycle_count += 1
        cycle_start = time.time()
        
        # Step 1: Signal Detection
        signal_engine = get_signal_engine()
        signals = signal_engine.analyze_context(context)
        
        # Step 2: Rule Evaluation
        rule_engine = get_rule_engine()
        rule_results = rule_engine.evaluate(context, signals)
        fired_rules = [r for r in rule_results if r.fired]
        
        # Step 3: Mission Generation
        new_missions = []
        for result in fired_rules:
            mission = self._create_mission(result, signals, context)
            if mission and not self._is_duplicate(mission):
                self._pending_missions.append(mission)
                new_missions.append(mission)
        
        # Step 4: Update metrics
        self._metrics.task_count = len(self._pending_missions)
        self._metrics.queue_pressure = len(self._pending_missions) / 50  # maxlen
        self._metrics.compute_cognitive_load()
        self._metrics.compute_system_pressure()
        
        # Step 5: State transition
        state_changed = self._update_state()
        
        # Store context
        self._last_context = context
        
        processing_time_ms = (time.time() - cycle_start) * 1000
        
        return {
            "cycle": self._cycle_count,
            "processing_time_ms": round(processing_time_ms, 2),
            "signals_detected": len(signals),
            "signals": [s.to_dict() for s in signals],
            "rules_evaluated": len(rule_results),
            "rules_fired": len(fired_rules),
            "fired_rule_ids": [r.rule.id for r in fired_rules],
            "missions_generated": len(new_missions),
            "new_missions": [m.to_dict() for m in new_missions],
            "system_state": self._state.value,
            "state_changed": state_changed,
            "metrics": self._metrics.to_dict(),
        }
    
    def _create_mission(
        self,
        rule_result: RuleResult,
        signals: list[Signal],
        context: dict[str, Any],
    ) -> Optional[AutoMission]:
        """Create a mission from a fired rule."""
        action = rule_result.action
        if not action or action.type != ActionType.CREATE_MISSION:
            return None
        
        template_name = action.template
        rule_engine = get_rule_engine()
        template = rule_engine.get_template(template_name)
        
        if not template:
            return None
        
        # Build decision chain for explainability
        decision_chain = [
            {
                "step": "context_observation",
                "description": f"Context'ten {len(signals)} sinyal tespit edildi",
            },
            {
                "step": "signal_detection",
                "signals": [s.message for s in rule_result.signals_matched[:3]],
            },
            {
                "step": "rule_evaluation",
                "rule_id": rule_result.rule.id,
                "rule_name": rule_result.rule.name,
            },
            {
                "step": "mission_generation",
                "template": template_name,
                "system_state": self._state.value,
            },
        ]
        
        # Adjust priority based on system state
        priority = template.get("priority", "P3")
        if self._state == SystemState.OVERLOAD:
            # In overload, only allow P1 tasks
            if priority not in ["P1"]:
                decision_chain.append({
                    "step": "state_filter",
                    "action": "mission_suppressed",
                    "reason": "System in OVERLOAD state, only P1 tasks allowed",
                })
                return None
        
        mission_id = f"auto_{uuid.uuid4().hex[:8]}"
        
        return AutoMission(
            id=mission_id,
            title=template.get("title", "Auto-generated Task"),
            priority=priority,
            category=template.get("category", "admin"),
            energy_cost=template.get("energy_cost", "medium"),
            duration_minutes=template.get("duration_minutes", 15),
            tags=template.get("tags", []),
            why=template.get("why", "Otomatik oluşturuldu"),
            source_rule_id=rule_result.rule.id,
            source_rule_name=rule_result.rule.name,
            trigger_signals=[s.id for s in rule_result.signals_matched],
            system_state=self._state,
            decision_chain=decision_chain,
            confidence=self._compute_confidence(rule_result, signals),
        )
    
    def _compute_confidence(self, rule_result: RuleResult, signals: list[Signal]) -> float:
        """Compute confidence score for a mission."""
        # Base confidence from rule priority (lower priority = higher confidence)
        base = 1.0 - (rule_result.rule.priority - 1) * 0.1
        
        # Boost from signal severity
        severity_boost = 0
        for sig in rule_result.signals_matched:
            if sig.severity == SignalSeverity.CRITICAL:
                severity_boost += 0.15
            elif sig.severity == SignalSeverity.HIGH:
                severity_boost += 0.1
            elif sig.severity == SignalSeverity.MEDIUM:
                severity_boost += 0.05
        
        # Multiple signals = higher confidence
        signal_boost = min(0.1, len(rule_result.signals_matched) * 0.03)
        
        return min(1.0, base + severity_boost + signal_boost)
    
    def _is_duplicate(self, new_mission: AutoMission) -> bool:
        """Check if a similar mission already exists."""
        for mission in self._pending_missions:
            if (mission.source_rule_id == new_mission.source_rule_id and
                mission.status == "pending"):
                return True
        return False
    
    def get_pending_missions(self) -> list[AutoMission]:
        """Get all pending missions."""
        return [m for m in self._pending_missions if m.status == "pending"]
    
    def complete_mission(self, mission_id: str) -> bool:
        """Mark a mission as completed."""
        for mission in self._pending_missions:
            if mission.id == mission_id:
                mission.status = "completed"
                self._completed_missions.append(mission)
                return True
        return False
    
    def dismiss_mission(self, mission_id: str) -> bool:
        """Dismiss a mission."""
        for mission in self._pending_missions:
            if mission.id == mission_id:
                mission.status = "dismissed"
                self._dismissed_missions.append(mission)
                return True
        return False
    
    def get_status(self) -> dict[str, Any]:
        """Get orchestrator status."""
        return {
            "state": self._state.value,
            "state_description": self._get_state_description(),
            "metrics": self._metrics.to_dict(),
            "pending_missions": len([m for m in self._pending_missions if m.status == "pending"]),
            "completed_missions": len(self._completed_missions),
            "dismissed_missions": len(self._dismissed_missions),
            "total_cycles": self._cycle_count,
            "state_history": [
                {"timestamp": ts, "state": s.value}
                for ts, s in list(self._state_history)[-10:]
            ],
        }
    
    def _get_state_description(self) -> str:
        """Get human-readable state description."""
        descriptions = {
            SystemState.CALM: "Sistem sakin. Optimizasyon görevleri önerilir.",
            SystemState.ACTIVE: "Normal aktivite. Verimlilik görevleri önerilir.",
            SystemState.OVERLOAD: "⚠️ Sistem yoğun! Sadece kritik görevler kabul ediliyor.",
            SystemState.RECOVERY: "Sistem toparlanıyor. Stabilizasyon görevleri önerilir.",
        }
        return descriptions.get(self._state, "Bilinmeyen durum")


# Singleton instance
_orchestrator: Optional[MissionOrchestrator] = None


def get_orchestrator() -> MissionOrchestrator:
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = MissionOrchestrator()
    return _orchestrator


def process_context(context: dict[str, Any]) -> dict[str, Any]:
    """Convenience function to process context."""
    return get_orchestrator().process_context(context)
