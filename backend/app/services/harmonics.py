"""System Harmonics Service - Health, Risk & Energy Indices.

Provides 3 key indices for the "wow" demo:
1. Stability Index - Source health + cache health (0-100)
2. Risk Index - Weather/calendar/anomaly weighted (0-100)
3. Energy Fit Index - Task energy vs time of day (0-100)

Also tracks anomaly flags and freshness data.
"""

from __future__ import annotations

import time
from datetime import datetime, timezone, timedelta
from typing import Any, Optional
from collections import deque


# In-memory stores for historical tracking
_context_history: deque = deque(maxlen=10)  # Last 10 context snapshots for anomaly detection
_harmonics_cache: dict[str, Any] = {}
_last_computed: Optional[float] = None


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _parse_iso(iso_str: str) -> datetime:
    """Parse ISO timestamp string to datetime."""
    if iso_str.endswith("Z"):
        iso_str = iso_str[:-1] + "+00:00"
    return datetime.fromisoformat(iso_str)


def _age_seconds(iso_str: str) -> float:
    """Calculate age in seconds from ISO timestamp."""
    try:
        dt = _parse_iso(iso_str)
        now = datetime.now(timezone.utc)
        return (now - dt).total_seconds()
    except:
        return 9999.0


def compute_source_health(context: dict[str, Any], ttl_seconds: int = 120) -> dict[str, Any]:
    """Compute health status for each data source.
    
    Returns per-source:
    - status: OK / DEGRADED / DOWN
    - last_updated: ISO timestamp
    - age_seconds: How old the data is
    - ttl_remaining: Seconds until data is considered stale
    - freshness_level: green/yellow/red
    """
    sources = ["weather", "github", "news", "exchange", "trending", "traffic", "calendar"]
    freshness = context.get("freshness", {})
    sources_ok = context.get("sources_ok", [])
    sources_failed = [s["source"] for s in context.get("sources_failed", [])]
    sources_skipped = [s["source"] for s in context.get("sources_skipped", [])]
    
    health_data = {}
    
    for source in sources:
        update_key = f"{source}_updated_at"
        last_updated = freshness.get(update_key)
        
        if source in sources_ok and last_updated:
            age = _age_seconds(last_updated)
            ttl_remaining = max(0, ttl_seconds - age)
            
            # Freshness levels: green (0-60s), yellow (60-180s), red (180s+)
            if age < 60:
                freshness_level = "green"
                status = "OK"
            elif age < 180:
                freshness_level = "yellow"
                status = "DEGRADED"
            else:
                freshness_level = "red"
                status = "DEGRADED"
            
            health_data[source] = {
                "status": status,
                "last_updated": last_updated,
                "age_seconds": round(age, 1),
                "ttl_remaining": round(ttl_remaining, 1),
                "freshness_level": freshness_level,
            }
        elif source in sources_failed:
            health_data[source] = {
                "status": "DOWN",
                "last_updated": None,
                "age_seconds": None,
                "ttl_remaining": 0,
                "freshness_level": "red",
                "error": next((s["error"] for s in context.get("sources_failed", []) if s["source"] == source), "Unknown"),
            }
        elif source in sources_skipped:
            health_data[source] = {
                "status": "SKIPPED",
                "last_updated": None,
                "age_seconds": None,
                "ttl_remaining": None,
                "freshness_level": "gray",
                "reason": next((s["reason"] for s in context.get("sources_skipped", []) if s["source"] == source), "Not configured"),
            }
        else:
            # Calendar is special - synthetic
            if source == "calendar":
                health_data[source] = {
                    "status": "OK",
                    "last_updated": context.get("observed_at"),
                    "age_seconds": 0,
                    "ttl_remaining": ttl_seconds,
                    "freshness_level": "green",
                }
            else:
                health_data[source] = {
                    "status": "UNKNOWN",
                    "last_updated": None,
                    "age_seconds": None,
                    "ttl_remaining": None,
                    "freshness_level": "gray",
                }
    
    return health_data


def detect_anomalies(context: dict[str, Any]) -> list[dict[str, Any]]:
    """Detect anomalies by comparing current context to historical averages.
    
    Anomaly types:
    - github_spike: Issue count > 150% of avg
    - weather_risk: Rain/storm + low temp
    - calendar_overload: > 5 events today
    - news_topic_hit: AI regulation or major tech news
    """
    global _context_history
    
    anomalies = []
    
    # Add current to history
    _context_history.append({
        "timestamp": context.get("observed_at"),
        "github_issues": context.get("github", {}).get("open_issues", 0) if context.get("github") else 0,
        "weather_condition": context.get("weather", {}).get("condition", "unknown") if context.get("weather") else "unknown",
        "weather_temp": context.get("weather", {}).get("temp_c", 20) if context.get("weather") else 20,
        "calendar_events": context.get("calendar", {}).get("events_today", 0) if context.get("calendar") else 0,
        "news_titles": [n.get("title", "") for n in context.get("news", [])] if context.get("news") else [],
    })
    
    current = _context_history[-1]
    
    # GitHub Issue Spike Detection
    if len(_context_history) >= 3:
        avg_issues = sum(h["github_issues"] for h in list(_context_history)[:-1]) / (len(_context_history) - 1)
        current_issues = current["github_issues"]
        if avg_issues > 0 and current_issues > avg_issues * 1.5:
            anomalies.append({
                "type": "github_spike",
                "severity": "warning",
                "message": f"GitHub issues spiked to {current_issues} (avg: {avg_issues:.0f})",
                "delta_percent": round((current_issues - avg_issues) / avg_issues * 100),
                "icon": "🔥",
            })
    
    # Weather Risk Detection
    weather_condition = current["weather_condition"].lower() if current["weather_condition"] else ""
    weather_temp = current["weather_temp"]
    risky_conditions = ["rain", "storm", "snow", "thunderstorm", "drizzle", "fog"]
    
    if any(cond in weather_condition for cond in risky_conditions):
        severity = "critical" if "storm" in weather_condition or "thunder" in weather_condition else "warning"
        anomalies.append({
            "type": "weather_risk",
            "severity": severity,
            "message": f"Weather alert: {weather_condition.title()} at {weather_temp}°C",
            "condition": weather_condition,
            "temp_c": weather_temp,
            "icon": "🌧️" if "rain" in weather_condition else "⛈️",
        })
    
    if weather_temp is not None and weather_temp < 5:
        anomalies.append({
            "type": "weather_risk",
            "severity": "info",
            "message": f"Cold weather: {weather_temp}°C - dress warmly",
            "temp_c": weather_temp,
            "icon": "🥶",
        })
    
    # Calendar Overload Detection
    events = current["calendar_events"]
    if events > 5:
        anomalies.append({
            "type": "calendar_overload",
            "severity": "warning",
            "message": f"Busy day: {events} calendar events",
            "event_count": events,
            "icon": "📅",
        })
    elif events > 3:
        anomalies.append({
            "type": "calendar_busy",
            "severity": "info",
            "message": f"Moderate schedule: {events} events today",
            "event_count": events,
            "icon": "📆",
        })
    
    # News Topic Hit Detection
    hot_topics = ["ai regulation", "openai", "artificial intelligence", "gpt", "llm", "tech layoff", "cybersecurity"]
    news_titles = " ".join(current["news_titles"]).lower()
    
    for topic in hot_topics:
        if topic in news_titles:
            anomalies.append({
                "type": "news_topic_hit",
                "severity": "info",
                "message": f"Hot topic detected: '{topic.title()}'",
                "topic": topic,
                "icon": "📰",
            })
            break  # Only report first match
    
    return anomalies


def compute_stability_index(source_health: dict[str, Any], cache_stats: dict[str, Any]) -> dict[str, Any]:
    """Compute Stability Index (0-100).
    
    Formula:
    - Source health weight: 70%
    - Cache health weight: 30%
    """
    # Source health score
    sources_up = sum(1 for s in source_health.values() if s.get("status") == "OK")
    sources_degraded = sum(1 for s in source_health.values() if s.get("status") == "DEGRADED")
    sources_down = sum(1 for s in source_health.values() if s.get("status") == "DOWN")
    total_active = sources_up + sources_degraded + sources_down
    
    if total_active > 0:
        source_score = ((sources_up * 100) + (sources_degraded * 50) + (sources_down * 0)) / total_active
    else:
        source_score = 0
    
    # Cache health score
    cache_hit_rate = cache_stats.get("hit_rate", 0)
    cache_score = cache_hit_rate  # Already 0-100
    
    # Weighted combination
    stability = (source_score * 0.7) + (cache_score * 0.3)
    
    return {
        "value": round(stability, 1),
        "source_score": round(source_score, 1),
        "cache_score": round(cache_score, 1),
        "sources_up": sources_up,
        "sources_degraded": sources_degraded,
        "sources_down": sources_down,
        "interpretation": "excellent" if stability >= 80 else "good" if stability >= 60 else "fair" if stability >= 40 else "poor",
    }


def compute_risk_index(context: dict[str, Any], anomalies: list[dict[str, Any]]) -> dict[str, Any]:
    """Compute Risk Index (0-100).
    
    Higher = more risk. Based on:
    - Weather conditions (30%)
    - Calendar load (20%)
    - Anomaly severity (30%)
    - GitHub pressure (20%)
    """
    risk = 0
    breakdown = {}
    
    # Weather risk (0-30)
    weather = context.get("weather") or {}
    condition = (weather.get("condition") or "").lower()
    temp = weather.get("temp_c", 20)
    
    weather_risk = 0
    if any(c in condition for c in ["storm", "thunder"]):
        weather_risk = 30
    elif any(c in condition for c in ["rain", "snow"]):
        weather_risk = 20
    elif any(c in condition for c in ["fog", "drizzle"]):
        weather_risk = 10
    
    if temp is not None and temp < 0:
        weather_risk = min(30, weather_risk + 10)
    
    breakdown["weather"] = weather_risk
    risk += weather_risk
    
    # Calendar risk (0-20)
    events = (context.get("calendar") or {}).get("events_today", 0)
    calendar_risk = min(20, events * 3)  # 3 points per event, max 20
    breakdown["calendar"] = calendar_risk
    risk += calendar_risk
    
    # Anomaly risk (0-30)
    critical_anomalies = sum(1 for a in anomalies if a.get("severity") == "critical")
    warning_anomalies = sum(1 for a in anomalies if a.get("severity") == "warning")
    anomaly_risk = min(30, critical_anomalies * 15 + warning_anomalies * 7)
    breakdown["anomalies"] = anomaly_risk
    risk += anomaly_risk
    
    # GitHub pressure (0-20)
    github = context.get("github") or {}
    issues = github.get("open_issues", 0)
    prs = github.get("open_prs", 0)
    github_risk = min(20, (issues // 5) + (prs * 2))
    breakdown["github"] = github_risk
    risk += github_risk
    
    return {
        "value": min(100, round(risk, 1)),
        "breakdown": breakdown,
        "interpretation": "critical" if risk >= 70 else "high" if risk >= 50 else "moderate" if risk >= 30 else "low",
    }


def compute_energy_fit_index(context: dict[str, Any], current_hour: int = None) -> dict[str, Any]:
    """Compute Energy Fit Index (0-100).
    
    How well does the current context match optimal productivity?
    Based on:
    - Time of day alignment (40%)
    - Weather comfort (30%)
    - Calendar space (30%)
    """
    if current_hour is None:
        current_hour = datetime.now(timezone.utc).hour
    
    fit = 0
    breakdown = {}
    
    # Time of day fit (0-40)
    # Peak productivity: 9-11, 14-16
    if 9 <= current_hour <= 11 or 14 <= current_hour <= 16:
        time_fit = 40
    elif 8 <= current_hour <= 18:
        time_fit = 25
    elif 6 <= current_hour <= 22:
        time_fit = 15
    else:
        time_fit = 5
    
    breakdown["time_of_day"] = time_fit
    fit += time_fit
    
    # Weather comfort (0-30)
    weather = context.get("weather") or {}
    condition = (weather.get("condition") or "").lower()
    temp = weather.get("temp_c", 20)
    
    if any(c in condition for c in ["clear", "sunny", "partly"]):
        weather_fit = 30
    elif any(c in condition for c in ["cloudy", "overcast"]):
        weather_fit = 25
    elif any(c in condition for c in ["drizzle", "fog"]):
        weather_fit = 15
    else:
        weather_fit = 10
    
    # Adjust for temperature
    if temp is not None:
        if 18 <= temp <= 25:
            weather_fit = min(30, weather_fit + 5)
        elif temp < 5 or temp > 35:
            weather_fit = max(0, weather_fit - 10)
    
    breakdown["weather_comfort"] = weather_fit
    fit += weather_fit
    
    # Calendar space (0-30) - fewer events = more energy fit
    events = (context.get("calendar") or {}).get("events_today", 0)
    if events <= 2:
        calendar_fit = 30
    elif events <= 4:
        calendar_fit = 20
    elif events <= 6:
        calendar_fit = 10
    else:
        calendar_fit = 5
    
    breakdown["calendar_space"] = calendar_fit
    fit += calendar_fit
    
    return {
        "value": round(fit, 1),
        "breakdown": breakdown,
        "current_hour": current_hour,
        "interpretation": "optimal" if fit >= 80 else "good" if fit >= 60 else "moderate" if fit >= 40 else "low",
    }


async def compute_harmonics(context: dict[str, Any], cache_stats: dict[str, Any] = None) -> dict[str, Any]:
    """Compute full System Harmonics snapshot.
    
    Returns:
    - source_health: Per-source health data
    - anomalies: Detected anomaly flags
    - indices: stability, risk, energy_fit
    - computed_at: Timestamp
    """
    global _harmonics_cache, _last_computed
    
    # Default cache stats if not provided
    if cache_stats is None:
        cache_stats = {"hit_rate": 50, "total_hits": 0, "total_misses": 0}
    
    source_health = compute_source_health(context)
    anomalies = detect_anomalies(context)
    stability = compute_stability_index(source_health, cache_stats)
    risk = compute_risk_index(context, anomalies)
    energy_fit = compute_energy_fit_index(context)
    
    harmonics = {
        "computed_at": _now_iso(),
        "context_id": context.get("context_id"),
        "source_health": source_health,
        "anomalies": anomalies,
        "anomaly_count": len(anomalies),
        "indices": {
            "stability": stability,
            "risk": risk,
            "energy_fit": energy_fit,
        },
        "summary": {
            "overall_health": "healthy" if stability["value"] >= 70 and risk["value"] < 40 else "warning" if risk["value"] < 60 else "critical",
            "sources_active": stability["sources_up"],
            "sources_degraded": stability["sources_degraded"],
            "sources_down": stability["sources_down"],
        },
    }
    
    _harmonics_cache = harmonics
    _last_computed = time.time()
    
    return harmonics


def get_cached_harmonics() -> dict[str, Any] | None:
    """Get cached harmonics if available and fresh (< 30s old)."""
    global _harmonics_cache, _last_computed
    
    if _last_computed is None:
        return None
    
    age = time.time() - _last_computed
    if age > 30:
        return None
    
    return _harmonics_cache
