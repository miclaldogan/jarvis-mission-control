"""
Simulation API for testing context-driven task generation.

Allows creating fake context scenarios to test how the system responds
to different conditions without affecting real data sources.
"""
from __future__ import annotations

import time
import uuid
from datetime import datetime, timezone
from typing import Any, Literal, Optional

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from app.http_envelope import ok
from app.services.missions import generate_missions
from app.services import storage

router = APIRouter()


class ScenarioConfig(BaseModel):
    """Configuration for a simulation scenario."""
    weather: Literal["sunny", "rainy", "cloudy", "snowy"] = "sunny"
    github_issues: Literal[2, 5, 10, 20, 50] = 5
    calendar_events: Literal[0, 2, 5] = 0
    news_topic: Literal["ai", "tech", "finance", "none"] = "none"
    energy_level: Optional[Literal["low", "medium", "high"]] = "medium"


class SimulationGenerateRequest(BaseModel):
    """Request to generate missions from simulation context."""
    scenario: ScenarioConfig
    limit: int = Field(15, ge=1, le=30)
    seed: Optional[int] = None


def generate_fake_weather(condition: str) -> dict[str, Any]:
    """Generate fake weather data based on condition."""
    temp_map = {
        "sunny": 25,
        "cloudy": 18,
        "rainy": 15,
        "snowy": -2,
    }
    
    return {
        "city": "Istanbul (Simulated)",
        "lat": "41.0082",
        "lon": "28.9784",
        "tz": "Europe/Istanbul",
        "temp_c": temp_map.get(condition, 20),
        "condition": condition,
    }


def generate_fake_github(issue_count: int) -> dict[str, Any]:
    """Generate fake GitHub data."""
    return {
        "owner": "simulation-user",
        "repo": "test-repo",
        "open_issues": issue_count,
        "open_prs": max(1, issue_count // 5),
    }


def generate_fake_news(topic: str, limit: int = 5) -> list[dict[str, Any]]:
    """Generate fake news based on topic."""
    if topic == "none":
        return []
    
    news_templates = {
        "ai": [
            {"title": "New AI Model Breaks Records", "url": "https://example.com/ai1"},
            {"title": "Machine Learning Advances", "url": "https://example.com/ai2"},
            {"title": "AI Ethics Debate Continues", "url": "https://example.com/ai3"},
        ],
        "tech": [
            {"title": "Tech Giant Releases New Product", "url": "https://example.com/tech1"},
            {"title": "Startup Funding Hits Record", "url": "https://example.com/tech2"},
            {"title": "Cybersecurity Alert Issued", "url": "https://example.com/tech3"},
        ],
        "finance": [
            {"title": "Markets React to Economic Data", "url": "https://example.com/fin1"},
            {"title": "Cryptocurrency Volatility", "url": "https://example.com/fin2"},
            {"title": "Interest Rates Unchanged", "url": "https://example.com/fin3"},
        ],
    }
    
    return news_templates.get(topic, [])[:limit]


def generate_fake_calendar(event_count: int) -> dict[str, Any]:
    """Generate fake calendar data."""
    return {
        "events_today": event_count,
    }


@router.post("/simulation/context")
async def create_simulation_context(request: Request, scenario: ScenarioConfig):
    """
    Create a fake context from simulation scenario.
    
    Returns a context snapshot that can be used with mission generation.
    """
    start = time.perf_counter()
    
    sim_id = f"sim_{uuid.uuid4().hex[:8]}"
    observed_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    
    # Build fake context
    fake_context = {
        "context_id": f"ctx_{sim_id}",
        "observed_at": observed_at,
        "fetched_at": observed_at,
        "is_simulation": True,
        "simulation_id": sim_id,
        "weather": generate_fake_weather(scenario.weather),
        "github": generate_fake_github(scenario.github_issues),
        "news": generate_fake_news(scenario.news_topic),
        "calendar": generate_fake_calendar(scenario.calendar_events),
        "exchange": None,  # Not simulated yet
        "traffic": None,
        "trending": [],
        "sources_ok": ["weather", "github", "news", "calendar"],
        "sources_failed": [],
        "sources_skipped": ["exchange", "traffic", "trending"],
        "freshness": {
            "weather_updated_at": observed_at,
            "github_updated_at": observed_at,
            "news_updated_at": observed_at,
        },
    }
    
    data = {
        "simulation_id": sim_id,
        "scenario": scenario.model_dump(),
        "context": fake_context,
    }
    
    response = JSONResponse(ok(request, data), status_code=200)
    compute_ms = int((time.perf_counter() - start) * 1000)
    response.headers["X-Compute-Time-ms"] = str(compute_ms)
    response.headers["X-Simulation"] = "true"
    return response


@router.post("/simulation/generate")
async def generate_simulation_missions(request: Request, body: SimulationGenerateRequest):
    """
    Generate missions from simulation scenario.
    
    Creates tasks based on fake context without affecting real data.
    """
    start = time.perf_counter()
    
    sim_id = f"sim_{uuid.uuid4().hex[:8]}"
    observed_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    
    # Build fake context
    fake_context = {
        "context_id": f"ctx_{sim_id}",
        "observed_at": observed_at,
        "fetched_at": observed_at,
        "is_simulation": True,
        "simulation_id": sim_id,
        "weather": generate_fake_weather(body.scenario.weather),
        "github": generate_fake_github(body.scenario.github_issues),
        "news": generate_fake_news(body.scenario.news_topic),
        "calendar": generate_fake_calendar(body.scenario.calendar_events),
        "exchange": None,
        "traffic": None,
        "trending": [],
        "sources_ok": ["weather", "github", "news", "calendar"],
        "sources_failed": [],
        "sources_skipped": ["exchange", "traffic", "trending"],
    }
    
    # Generate missions with fake context
    preferences = None
    if body.scenario.energy_level:
        preferences = {"energy_level": body.scenario.energy_level}
    
    missions = generate_missions(
        context=fake_context,
        preferences=preferences,
        limit=body.limit,
        seed=body.seed,
    )
    
    # Mark missions as simulation (don't store in regular storage)
    for mission in missions:
        mission["is_simulation"] = True
        mission["simulation_id"] = sim_id
    
    data = {
        "simulation_id": sim_id,
        "scenario": body.scenario.model_dump(),
        "context": {
            "context_id": fake_context.get("context_id"),
            "observed_at": fake_context.get("observed_at"),
            "is_simulation": True,
        },
        "missions": missions,
    }
    
    response = JSONResponse(ok(request, data), status_code=200)
    compute_ms = int((time.perf_counter() - start) * 1000)
    response.headers["X-Compute-Time-ms"] = str(compute_ms)
    response.headers["X-Simulation"] = "true"
    return response
