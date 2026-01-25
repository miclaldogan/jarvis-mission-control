"""
Rule Engine - The Decision Layer of JARVIS

Declarative rule system that transforms signals into actions.
Rules are JSON-configurable and support complex conditions.

Rule Structure:
{
    "id": "rule_001",
    "name": "PR Overload Guard",
    "description": "Creates task when PR queue is full",
    "enabled": true,
    "priority": 1,
    "conditions": [
        {"signal": "github.open_prs", "operator": ">=", "value": 5}
    ],
    "condition_logic": "AND",  # or "OR"
    "action": {
        "type": "create_mission",
        "template": "pr_review_block"
    },
    "cooldown_seconds": 300
}
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Optional
import re

from app.services.signal_engine import Signal, SignalType, SignalSeverity


class Operator(str, Enum):
    EQ = "=="
    NE = "!="
    GT = ">"
    GTE = ">="
    LT = "<"
    LTE = "<="
    IN = "in"
    NOT_IN = "not_in"
    CONTAINS = "contains"
    MATCHES = "matches"  # regex


class ActionType(str, Enum):
    CREATE_MISSION = "create_mission"
    UPDATE_STATE = "update_state"
    SEND_ALERT = "send_alert"
    LOG = "log"


@dataclass
class Condition:
    """A single condition to evaluate."""
    signal_source: str  # e.g., "github", "weather"
    metric: str  # e.g., "open_prs", "temp_c"
    operator: Operator
    value: Any
    
    def evaluate(self, context: dict[str, Any], signals: list[Signal]) -> bool:
        """Evaluate this condition against context and signals."""
        # First try to find in signals
        for sig in signals:
            if sig.source == self.signal_source and sig.metric == self.metric:
                return self._compare(sig.value)
        
        # Fall back to context lookup
        source_data = context.get(self.signal_source) or {}
        actual_value = source_data.get(self.metric)
        
        if actual_value is None:
            return False
        
        return self._compare(actual_value)
    
    def _compare(self, actual: Any) -> bool:
        """Compare actual value against expected using operator."""
        try:
            if self.operator == Operator.EQ:
                return actual == self.value
            elif self.operator == Operator.NE:
                return actual != self.value
            elif self.operator == Operator.GT:
                return actual > self.value
            elif self.operator == Operator.GTE:
                return actual >= self.value
            elif self.operator == Operator.LT:
                return actual < self.value
            elif self.operator == Operator.LTE:
                return actual <= self.value
            elif self.operator == Operator.IN:
                return actual in self.value
            elif self.operator == Operator.NOT_IN:
                return actual not in self.value
            elif self.operator == Operator.CONTAINS:
                return self.value in str(actual).lower()
            elif self.operator == Operator.MATCHES:
                return bool(re.match(self.value, str(actual)))
        except Exception:
            return False
        return False


@dataclass
class Action:
    """An action to execute when rule fires."""
    type: ActionType
    template: Optional[str] = None
    params: dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "type": self.type.value,
            "template": self.template,
            "params": self.params,
        }


@dataclass
class Rule:
    """A complete rule with conditions and actions."""
    id: str
    name: str
    description: str
    conditions: list[Condition]
    action: Action
    condition_logic: str = "AND"  # "AND" or "OR"
    enabled: bool = True
    priority: int = 5  # 1 = highest
    cooldown_seconds: int = 300
    last_fired: Optional[float] = None
    fire_count: int = 0
    
    def can_fire(self) -> bool:
        """Check if rule can fire (cooldown elapsed)."""
        if not self.enabled:
            return False
        if self.last_fired is None:
            return True
        return time.time() - self.last_fired >= self.cooldown_seconds
    
    def evaluate(self, context: dict[str, Any], signals: list[Signal]) -> bool:
        """Evaluate all conditions."""
        if not self.can_fire():
            return False
        
        if not self.conditions:
            return True
        
        results = [c.evaluate(context, signals) for c in self.conditions]
        
        if self.condition_logic == "OR":
            return any(results)
        return all(results)
    
    def mark_fired(self) -> None:
        """Mark rule as fired."""
        self.last_fired = time.time()
        self.fire_count += 1
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "enabled": self.enabled,
            "priority": self.priority,
            "condition_logic": self.condition_logic,
            "cooldown_seconds": self.cooldown_seconds,
            "fire_count": self.fire_count,
            "last_fired": self.last_fired,
        }


@dataclass
class RuleResult:
    """Result of a rule evaluation."""
    rule: Rule
    fired: bool
    action: Optional[Action]
    signals_matched: list[Signal]
    evaluated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"))
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "rule_id": self.rule.id,
            "rule_name": self.rule.name,
            "fired": self.fired,
            "action": self.action.to_dict() if self.action else None,
            "signals_matched": [s.id for s in self.signals_matched],
            "evaluated_at": self.evaluated_at,
        }


# ═══════════════════════════════════════════════════════════════════════════
# DEFAULT RULE DEFINITIONS
# ═══════════════════════════════════════════════════════════════════════════

DEFAULT_RULES: list[Rule] = [
    # GitHub Rules
    Rule(
        id="rule_github_pr_overload",
        name="PR Overload Guard",
        description="PR kuyruğu dolduğunda review görevi oluştur",
        conditions=[
            Condition("github", "open_prs", Operator.GTE, 5),
        ],
        action=Action(ActionType.CREATE_MISSION, "pr_review_block"),
        priority=1,
        cooldown_seconds=600,
    ),
    Rule(
        id="rule_github_pr_critical",
        name="PR Critical Alert",
        description="PR sayısı kritik seviyede",
        conditions=[
            Condition("github", "open_prs", Operator.GTE, 10),
        ],
        action=Action(ActionType.CREATE_MISSION, "pr_emergency"),
        priority=1,
        cooldown_seconds=300,
    ),
    Rule(
        id="rule_github_issue_spike",
        name="Issue Spike Detector",
        description="Issue sayısında ani artış algılandı",
        conditions=[
            Condition("github", "open_issues", Operator.GTE, 15),
        ],
        action=Action(ActionType.CREATE_MISSION, "issue_triage"),
        priority=2,
        cooldown_seconds=900,
    ),
    
    # Weather Rules
    Rule(
        id="rule_weather_rain",
        name="Rain Alert",
        description="Yağmur durumunda iç mekan planlaması",
        conditions=[
            Condition("weather", "condition", Operator.CONTAINS, "rain"),
        ],
        action=Action(ActionType.CREATE_MISSION, "indoor_shift"),
        priority=3,
        cooldown_seconds=3600,
    ),
    Rule(
        id="rule_weather_storm",
        name="Storm Alert",
        description="Fırtına uyarısı",
        conditions=[
            Condition("weather", "condition", Operator.CONTAINS, "storm"),
        ],
        action=Action(ActionType.CREATE_MISSION, "storm_prep"),
        priority=1,
        cooldown_seconds=1800,
    ),
    Rule(
        id="rule_weather_cold",
        name="Cold Weather Alert",
        description="Soğuk hava uyarısı",
        conditions=[
            Condition("weather", "temp_c", Operator.LTE, 5),
        ],
        action=Action(ActionType.CREATE_MISSION, "cold_alert"),
        priority=3,
        cooldown_seconds=7200,
    ),
    Rule(
        id="rule_weather_heat",
        name="Heat Alert",
        description="Sıcak hava uyarısı",
        conditions=[
            Condition("weather", "temp_c", Operator.GTE, 35),
        ],
        action=Action(ActionType.CREATE_MISSION, "heat_alert"),
        priority=2,
        cooldown_seconds=3600,
    ),
    
    # Calendar Rules
    Rule(
        id="rule_calendar_overload",
        name="Calendar Overload",
        description="Takvim aşırı yoğun",
        conditions=[
            Condition("calendar", "events_today", Operator.GTE, 6),
        ],
        action=Action(ActionType.CREATE_MISSION, "focus_protection"),
        priority=2,
        cooldown_seconds=7200,
    ),
    
    # Exchange Rules
    Rule(
        id="rule_exchange_volatility",
        name="Exchange Volatility",
        description="Döviz kurunda ani değişim",
        conditions=[
            Condition("exchange", "volatility", Operator.GTE, 2.5),
        ],
        action=Action(ActionType.CREATE_MISSION, "finance_check"),
        priority=2,
        cooldown_seconds=1800,
    ),
]


# ═══════════════════════════════════════════════════════════════════════════
# MISSION TEMPLATES
# ═══════════════════════════════════════════════════════════════════════════

MISSION_TEMPLATES: dict[str, dict[str, Any]] = {
    "pr_review_block": {
        "title": "PR Review Bloğu: 45dk ayır",
        "priority": "P1",
        "category": "dev",
        "energy_cost": "high",
        "duration_minutes": 45,
        "tags": ["github", "code-review", "critical"],
        "why": "PR kuyruğu dolu. Review gecikmesi merge conflict ve deployment riski oluşturuyor.",
    },
    "pr_emergency": {
        "title": "🚨 Acil PR Temizliği",
        "priority": "P1",
        "category": "dev",
        "energy_cost": "high",
        "duration_minutes": 60,
        "tags": ["github", "emergency", "critical"],
        "why": "PR sayısı kritik seviyede! Acil müdahale gerekiyor.",
    },
    "issue_triage": {
        "title": "Issue Triage Oturumu",
        "priority": "P2",
        "category": "dev",
        "energy_cost": "medium",
        "duration_minutes": 30,
        "tags": ["github", "triage", "maintenance"],
        "why": "Issue backlog büyüyor. Önceliklendirme ve etiketleme gerekli.",
    },
    "indoor_shift": {
        "title": "Dış Mekan Planlarını Güncelle",
        "priority": "P3",
        "category": "admin",
        "energy_cost": "low",
        "duration_minutes": 10,
        "tags": ["weather", "planning"],
        "why": "Yağış bekleniyor. Dış aktiviteleri iç mekana taşı.",
    },
    "storm_prep": {
        "title": "⛈️ Fırtına Hazırlığı",
        "priority": "P2",
        "category": "admin",
        "energy_cost": "medium",
        "duration_minutes": 15,
        "tags": ["weather", "emergency"],
        "why": "Fırtına uyarısı. Dış planları iptal et, güvenli kal.",
    },
    "cold_alert": {
        "title": "Soğuk Hava: Kalın Giyinmeyi Unutma",
        "priority": "P4",
        "category": "health",
        "energy_cost": "low",
        "duration_minutes": 5,
        "tags": ["weather", "health"],
        "why": "Sıcaklık düşük. Kalın giyinmeyi ve dışarıda uzun kalmamayı unutma.",
    },
    "heat_alert": {
        "title": "🥵 Sıcak Hava: Bol Su İç",
        "priority": "P3",
        "category": "health",
        "energy_cost": "low",
        "duration_minutes": 5,
        "tags": ["weather", "health", "hydration"],
        "why": "Sıcaklık çok yüksek. Öğle saatlerinde dışarı çıkmaktan kaçın, bol su iç.",
    },
    "focus_protection": {
        "title": "🛡️ Odaklanma Koruma Bloğu",
        "priority": "P2",
        "category": "work",
        "energy_cost": "low",
        "duration_minutes": 30,
        "tags": ["calendar", "focus", "protection"],
        "why": "Takvim çok yoğun. Odaklanma için koruma bloğu şart.",
    },
    "finance_check": {
        "title": "💰 Finansal Kontrol",
        "priority": "P2",
        "category": "admin",
        "energy_cost": "medium",
        "duration_minutes": 15,
        "tags": ["exchange", "finance", "risk"],
        "why": "Döviz kurunda volatilite. Finansal pozisyonları gözden geçir.",
    },
}


class RuleEngine:
    """
    Evaluates rules against context and signals.
    Produces mission creation actions.
    """
    
    def __init__(self):
        self.rules: list[Rule] = list(DEFAULT_RULES)
        self.templates = dict(MISSION_TEMPLATES)
        self._evaluation_count = 0
    
    def add_rule(self, rule: Rule) -> None:
        """Add a new rule."""
        self.rules.append(rule)
        # Keep sorted by priority
        self.rules.sort(key=lambda r: r.priority)
    
    def remove_rule(self, rule_id: str) -> bool:
        """Remove a rule by ID."""
        for i, rule in enumerate(self.rules):
            if rule.id == rule_id:
                self.rules.pop(i)
                return True
        return False
    
    def enable_rule(self, rule_id: str) -> bool:
        """Enable a rule."""
        for rule in self.rules:
            if rule.id == rule_id:
                rule.enabled = True
                return True
        return False
    
    def disable_rule(self, rule_id: str) -> bool:
        """Disable a rule."""
        for rule in self.rules:
            if rule.id == rule_id:
                rule.enabled = False
                return True
        return False
    
    def evaluate(
        self,
        context: dict[str, Any],
        signals: list[Signal],
    ) -> list[RuleResult]:
        """
        Evaluate all rules against context and signals.
        Returns list of results (including non-fired rules for transparency).
        """
        self._evaluation_count += 1
        results: list[RuleResult] = []
        
        for rule in self.rules:
            # Find matching signals for this rule
            matching_signals = [
                s for s in signals
                if any(
                    c.signal_source == s.source and c.metric == s.metric
                    for c in rule.conditions
                )
            ]
            
            fired = rule.evaluate(context, signals)
            
            if fired:
                rule.mark_fired()
            
            results.append(RuleResult(
                rule=rule,
                fired=fired,
                action=rule.action if fired else None,
                signals_matched=matching_signals if fired else [],
            ))
        
        return results
    
    def get_fired_actions(
        self,
        context: dict[str, Any],
        signals: list[Signal],
    ) -> list[tuple[Rule, Action]]:
        """Get only the fired rule actions."""
        results = self.evaluate(context, signals)
        return [(r.rule, r.action) for r in results if r.fired and r.action]
    
    def get_template(self, template_name: str) -> Optional[dict[str, Any]]:
        """Get a mission template by name."""
        return self.templates.get(template_name)
    
    def get_status(self) -> dict[str, Any]:
        """Get engine status."""
        return {
            "total_rules": len(self.rules),
            "enabled_rules": sum(1 for r in self.rules if r.enabled),
            "total_evaluations": self._evaluation_count,
            "rules": [r.to_dict() for r in self.rules],
        }


# Singleton instance
_rule_engine: Optional[RuleEngine] = None


def get_rule_engine() -> RuleEngine:
    global _rule_engine
    if _rule_engine is None:
        _rule_engine = RuleEngine()
    return _rule_engine


def evaluate_rules(context: dict[str, Any], signals: list[Signal]) -> list[RuleResult]:
    """Convenience function to evaluate rules."""
    return get_rule_engine().evaluate(context, signals)
