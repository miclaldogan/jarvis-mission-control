"""
Signal Engine - The Perception Layer of JARVIS

Detects anomalies, deltas, spikes, and threshold violations in context data.
Produces typed signals that feed into the Rule Engine.

Signal Types:
- SPIKE: Sudden increase (>150% of baseline)
- DROP: Sudden decrease (<50% of baseline)
- THRESHOLD: Value crossed a defined limit
- ANOMALY: Unusual pattern detected
- DELTA: Significant change from last observation
"""

from __future__ import annotations

import time
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Optional
import statistics


class SignalType(str, Enum):
    SPIKE = "spike"
    DROP = "drop"
    THRESHOLD = "threshold"
    ANOMALY = "anomaly"
    DELTA = "delta"
    STABLE = "stable"


class SignalSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class Signal:
    """A detected signal from context analysis."""
    id: str
    type: SignalType
    severity: SignalSeverity
    source: str  # e.g., "github", "weather", "exchange"
    metric: str  # e.g., "open_prs", "temp_c", "usd_try"
    value: float
    baseline: Optional[float]
    threshold: Optional[float]
    delta: Optional[float]
    message: str
    detected_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"))
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type.value,
            "severity": self.severity.value,
            "source": self.source,
            "metric": self.metric,
            "value": self.value,
            "baseline": self.baseline,
            "threshold": self.threshold,
            "delta": self.delta,
            "message": self.message,
            "detected_at": self.detected_at,
        }


class SignalEngine:
    """
    Analyzes context data streams and emits signals.
    
    Maintains rolling history for baseline calculation.
    Configurable thresholds per metric.
    """
    
    def __init__(self, history_size: int = 20):
        self.history_size = history_size
        self._history: dict[str, deque] = {}
        self._last_values: dict[str, float] = {}
        self._signal_count = 0
        
        # Configurable thresholds
        self.thresholds = {
            # GitHub
            "github.open_prs": {"warn": 5, "critical": 10},
            "github.open_issues": {"warn": 15, "critical": 30},
            
            # Weather
            "weather.temp_c": {"low": 5, "high": 35},
            "weather.humidity": {"warn": 85},
            
            # Exchange
            "exchange.usd_try": {"spike_pct": 3.0},  # 3% change
            "exchange.eur_try": {"spike_pct": 3.0},
            
            # Calendar
            "calendar.events_today": {"warn": 5, "overload": 8},
            
            # System
            "system.cpu_percent": {"warn": 70, "critical": 90},
            "system.memory_percent": {"warn": 80, "critical": 95},
            "system.task_queue": {"warn": 10, "critical": 20},
        }
        
        # Spike detection: >150% of baseline
        self.spike_multiplier = 1.5
        # Drop detection: <50% of baseline
        self.drop_multiplier = 0.5
    
    def _get_history(self, key: str) -> deque:
        if key not in self._history:
            self._history[key] = deque(maxlen=self.history_size)
        return self._history[key]
    
    def _record_value(self, key: str, value: float) -> None:
        history = self._get_history(key)
        history.append(value)
        self._last_values[key] = value
    
    def _get_baseline(self, key: str) -> Optional[float]:
        history = self._get_history(key)
        if len(history) < 3:
            return None
        return statistics.mean(history)
    
    def _get_std(self, key: str) -> Optional[float]:
        history = self._get_history(key)
        if len(history) < 3:
            return None
        try:
            return statistics.stdev(history)
        except statistics.StatisticsError:
            return None
    
    def _generate_signal_id(self) -> str:
        self._signal_count += 1
        ts = int(time.time() * 1000) % 100000
        return f"sig_{ts}_{self._signal_count:04d}"
    
    def analyze_context(self, context: dict[str, Any]) -> list[Signal]:
        """
        Analyze a context snapshot and emit signals.
        
        Returns list of detected signals.
        """
        signals: list[Signal] = []
        
        # Analyze each data source
        signals.extend(self._analyze_github(context.get("github") or {}))
        signals.extend(self._analyze_weather(context.get("weather") or {}))
        signals.extend(self._analyze_exchange(context.get("exchange") or {}))
        signals.extend(self._analyze_calendar(context.get("calendar") or {}))
        signals.extend(self._analyze_news(context.get("news") or []))
        
        return signals
    
    def _analyze_github(self, github: dict[str, Any]) -> list[Signal]:
        signals = []
        
        # Open PRs
        open_prs = github.get("open_prs")
        if isinstance(open_prs, (int, float)):
            key = "github.open_prs"
            baseline = self._get_baseline(key)
            self._record_value(key, open_prs)
            
            thresholds = self.thresholds.get(key, {})
            
            # Threshold check
            if open_prs >= thresholds.get("critical", 999):
                signals.append(Signal(
                    id=self._generate_signal_id(),
                    type=SignalType.THRESHOLD,
                    severity=SignalSeverity.CRITICAL,
                    source="github",
                    metric="open_prs",
                    value=open_prs,
                    baseline=baseline,
                    threshold=thresholds.get("critical"),
                    delta=open_prs - baseline if baseline else None,
                    message=f"🚨 PR kuyruğu kritik seviyede: {open_prs} açık PR",
                ))
            elif open_prs >= thresholds.get("warn", 999):
                signals.append(Signal(
                    id=self._generate_signal_id(),
                    type=SignalType.THRESHOLD,
                    severity=SignalSeverity.HIGH,
                    source="github",
                    metric="open_prs",
                    value=open_prs,
                    baseline=baseline,
                    threshold=thresholds.get("warn"),
                    delta=open_prs - baseline if baseline else None,
                    message=f"⚠️ PR kuyruğu dolmaya başladı: {open_prs} açık PR",
                ))
            
            # Spike check
            if baseline and open_prs > baseline * self.spike_multiplier:
                signals.append(Signal(
                    id=self._generate_signal_id(),
                    type=SignalType.SPIKE,
                    severity=SignalSeverity.MEDIUM,
                    source="github",
                    metric="open_prs",
                    value=open_prs,
                    baseline=baseline,
                    threshold=None,
                    delta=open_prs - baseline,
                    message=f"📈 GitHub aktivitesi artışı: {open_prs} PR (baseline: {baseline:.1f})",
                ))
        
        # Open Issues
        open_issues = github.get("open_issues")
        if isinstance(open_issues, (int, float)):
            key = "github.open_issues"
            baseline = self._get_baseline(key)
            self._record_value(key, open_issues)
            
            thresholds = self.thresholds.get(key, {})
            
            if open_issues >= thresholds.get("critical", 999):
                signals.append(Signal(
                    id=self._generate_signal_id(),
                    type=SignalType.THRESHOLD,
                    severity=SignalSeverity.CRITICAL,
                    source="github",
                    metric="open_issues",
                    value=open_issues,
                    baseline=baseline,
                    threshold=thresholds.get("critical"),
                    delta=open_issues - baseline if baseline else None,
                    message=f"🚨 Issue sayısı kritik: {open_issues} açık issue",
                ))
            elif open_issues >= thresholds.get("warn", 999):
                signals.append(Signal(
                    id=self._generate_signal_id(),
                    type=SignalType.THRESHOLD,
                    severity=SignalSeverity.MEDIUM,
                    source="github",
                    metric="open_issues",
                    value=open_issues,
                    baseline=baseline,
                    threshold=thresholds.get("warn"),
                    delta=open_issues - baseline if baseline else None,
                    message=f"⚠️ Issue backlog büyüyor: {open_issues} issue",
                ))
        
        return signals
    
    def _analyze_weather(self, weather: dict[str, Any]) -> list[Signal]:
        signals = []
        
        temp_c = weather.get("temp_c")
        if isinstance(temp_c, (int, float)):
            key = "weather.temp_c"
            baseline = self._get_baseline(key)
            self._record_value(key, temp_c)
            
            thresholds = self.thresholds.get(key, {})
            
            # Extreme cold
            if temp_c <= thresholds.get("low", -999):
                signals.append(Signal(
                    id=self._generate_signal_id(),
                    type=SignalType.THRESHOLD,
                    severity=SignalSeverity.MEDIUM,
                    source="weather",
                    metric="temp_c",
                    value=temp_c,
                    baseline=baseline,
                    threshold=thresholds.get("low"),
                    delta=temp_c - baseline if baseline else None,
                    message=f"🥶 Düşük sıcaklık uyarısı: {temp_c}°C",
                ))
            
            # Extreme heat
            if temp_c >= thresholds.get("high", 999):
                signals.append(Signal(
                    id=self._generate_signal_id(),
                    type=SignalType.THRESHOLD,
                    severity=SignalSeverity.MEDIUM,
                    source="weather",
                    metric="temp_c",
                    value=temp_c,
                    baseline=baseline,
                    threshold=thresholds.get("high"),
                    delta=temp_c - baseline if baseline else None,
                    message=f"🥵 Yüksek sıcaklık uyarısı: {temp_c}°C",
                ))
        
        # Weather condition signals
        condition = (weather.get("condition") or "").lower()
        if condition in ("rain", "storm", "thunderstorm", "snow"):
            severity = SignalSeverity.HIGH if "storm" in condition else SignalSeverity.MEDIUM
            signals.append(Signal(
                id=self._generate_signal_id(),
                type=SignalType.ANOMALY,
                severity=severity,
                source="weather",
                metric="condition",
                value=0,
                baseline=None,
                threshold=None,
                delta=None,
                message=f"🌧️ Hava durumu uyarısı: {condition.title()}",
            ))
        
        return signals
    
    def _analyze_exchange(self, exchange: dict[str, Any]) -> list[Signal]:
        signals = []
        
        rates = exchange.get("rates") or {}
        
        for currency, rate in rates.items():
            if not isinstance(rate, (int, float)):
                continue
            
            key = f"exchange.{currency.lower()}"
            baseline = self._get_baseline(key)
            last_value = self._last_values.get(key)
            self._record_value(key, rate)
            
            # Check for significant change
            if last_value and last_value > 0:
                change_pct = abs((rate - last_value) / last_value) * 100
                
                spike_threshold = self.thresholds.get(key, {}).get("spike_pct", 3.0)
                
                if change_pct >= spike_threshold:
                    direction = "yükseldi" if rate > last_value else "düştü"
                    signals.append(Signal(
                        id=self._generate_signal_id(),
                        type=SignalType.SPIKE if rate > last_value else SignalType.DROP,
                        severity=SignalSeverity.HIGH if change_pct >= 5 else SignalSeverity.MEDIUM,
                        source="exchange",
                        metric=currency,
                        value=rate,
                        baseline=baseline,
                        threshold=spike_threshold,
                        delta=rate - last_value,
                        message=f"💱 {currency} %{change_pct:.1f} {direction}: {rate:.4f}",
                    ))
        
        return signals
    
    def _analyze_calendar(self, calendar: dict[str, Any]) -> list[Signal]:
        signals = []
        
        events_today = calendar.get("events_today")
        if isinstance(events_today, (int, float)):
            key = "calendar.events_today"
            baseline = self._get_baseline(key)
            self._record_value(key, events_today)
            
            thresholds = self.thresholds.get(key, {})
            
            if events_today >= thresholds.get("overload", 999):
                signals.append(Signal(
                    id=self._generate_signal_id(),
                    type=SignalType.THRESHOLD,
                    severity=SignalSeverity.HIGH,
                    source="calendar",
                    metric="events_today",
                    value=events_today,
                    baseline=baseline,
                    threshold=thresholds.get("overload"),
                    delta=events_today - baseline if baseline else None,
                    message=f"📅 Takvim aşırı yoğun: {events_today} etkinlik",
                ))
            elif events_today >= thresholds.get("warn", 999):
                signals.append(Signal(
                    id=self._generate_signal_id(),
                    type=SignalType.THRESHOLD,
                    severity=SignalSeverity.MEDIUM,
                    source="calendar",
                    metric="events_today",
                    value=events_today,
                    baseline=baseline,
                    threshold=thresholds.get("warn"),
                    delta=events_today - baseline if baseline else None,
                    message=f"📆 Yoğun gün: {events_today} etkinlik planlandı",
                ))
        
        return signals
    
    def _analyze_news(self, news: list[dict[str, Any]]) -> list[Signal]:
        """
        Analyze news items for tech trends, security alerts, and AI developments.
        Uses keyword matching to classify news importance.
        """
        signals = []
        
        if not news or not isinstance(news, list):
            return signals
        
        # Keywords for classification
        security_keywords = [
            "vulnerability", "cve", "exploit", "breach", "hack", "security",
            "malware", "ransomware", "attack", "zero-day", "critical"
        ]
        ai_keywords = [
            "ai", "gpt", "llm", "machine learning", "neural", "openai",
            "anthropic", "google ai", "deepmind", "chatgpt", "claude",
            "artificial intelligence", "generative", "transformer"
        ]
        tech_keywords = [
            "react", "python", "rust", "go", "javascript", "typescript",
            "kubernetes", "docker", "aws", "azure", "github", "api",
            "startup", "funding", "ipo", "acquisition"
        ]
        
        has_security = False
        has_ai = False
        has_tech = False
        news_count = len(news)
        
        for item in news:
            title = (item.get("title") or "").lower()
            
            # Check for security news
            if any(kw in title for kw in security_keywords):
                has_security = True
            
            # Check for AI news
            if any(kw in title for kw in ai_keywords):
                has_ai = True
            
            # Check for general tech news
            if any(kw in title for kw in tech_keywords):
                has_tech = True
        
        # Emit signals based on detected content
        if news_count > 0:
            signals.append(Signal(
                id=self._generate_signal_id(),
                type=SignalType.STABLE,
                severity=SignalSeverity.LOW,
                source="news",
                metric="has_items",
                value=1 if news_count > 0 else 0,
                baseline=None,
                threshold=None,
                delta=None,
                message=f"📰 {news_count} haber makalesi mevcut",
            ))
        
        if has_security:
            signals.append(Signal(
                id=self._generate_signal_id(),
                type=SignalType.ANOMALY,
                severity=SignalSeverity.CRITICAL,
                source="news",
                metric="security_alert",
                value=1,
                baseline=None,
                threshold=None,
                delta=None,
                message="🔒 Güvenlik ile ilgili kritik haber algılandı!",
            ))
        
        if has_ai:
            signals.append(Signal(
                id=self._generate_signal_id(),
                type=SignalType.ANOMALY,
                severity=SignalSeverity.MEDIUM,
                source="news",
                metric="ai_related",
                value=1,
                baseline=None,
                threshold=None,
                delta=None,
                message="🤖 Yapay zeka ile ilgili önemli haber algılandı",
            ))
        
        if has_tech and not has_security and not has_ai:
            signals.append(Signal(
                id=self._generate_signal_id(),
                type=SignalType.STABLE,
                severity=SignalSeverity.LOW,
                source="news",
                metric="tech_update",
                value=1,
                baseline=None,
                threshold=None,
                delta=None,
                message="💻 Teknoloji haberleri güncel",
            ))
        
        return signals
    
    def get_status(self) -> dict[str, Any]:
        """Get engine status for monitoring."""
        return {
            "history_size": self.history_size,
            "tracked_metrics": len(self._history),
            "total_signals_emitted": self._signal_count,
            "metrics": list(self._history.keys()),
            "last_values": dict(self._last_values),
        }


# Singleton instance
_signal_engine: Optional[SignalEngine] = None


def get_signal_engine() -> SignalEngine:
    global _signal_engine
    if _signal_engine is None:
        _signal_engine = SignalEngine()
    return _signal_engine


def analyze_context(context: dict[str, Any]) -> list[Signal]:
    """Convenience function to analyze context."""
    return get_signal_engine().analyze_context(context)
