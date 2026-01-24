from __future__ import annotations

import random
from datetime import datetime, timedelta, timezone
from typing import Any, Literal, Optional

from app.services.scoring import calculate_mission_score


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


def generate_missions(
    *,
    context: dict[str, Any],
    preferences: Optional[dict[str, Any]] = None,
    limit: int = 15,
    seed: Optional[int] = None,
) -> list[dict[str, Any]]:
    """Generate a demo-friendly mission list from context.

    The goal is explainability and determinism (when seed is provided), not ML.
    """

    rng = random.Random(seed)
    preferences = preferences or {}

    weather = context.get("weather") or {}
    github = context.get("github") or {}
    news = context.get("news") or []

    energy_level = preferences.get("energy_level")

    missions: list[dict[str, Any]] = []

    def add(
        *,
        title: str,
        priority: Priority,
        tags: list[str],
        why: str,
        sources: list[str],
        due_at: Optional[str] = None,
        confidence: float = 0.7,
        actions: Optional[list[dict[str, str]]] = None,
    ) -> None:
        idx = len(missions) + 1
        
        # Calculate dynamic score
        score = calculate_mission_score(
            due_at=due_at,
            tags=tags,
            context=context,
            preferences=preferences,
        )
        score_dict = score.to_dict()
        
        missions.append(
            {
                "id": f"msn_{idx:03d}",
                "title": title,
                "priority": score_dict["priority"],  # Use calculated priority
                "priority_score": score_dict["total"],
                "score_breakdown": score_dict["breakdown"],
                "reasons": score_dict["reasons"],
                "status": "open",
                "due_at": due_at,
                "tags": tags,
                "why": why,
                "actions": actions
                or [
                    {"label": "Context detayına git", "type": "link", "target": "/context"}
                ],
                "evidence": {
                    "sources": sources,
                    "confidence": max(0.0, min(1.0, float(confidence))),
                },
            }
        )

    # Rule 1: Weather-driven planning
    condition = (weather.get("condition") or "").lower()
    temp_c = weather.get("temp_c")
    if condition in ("rain", "snow"):
        add(
            title="Dış planları güncelle (hava kötü)",
            priority="P2",
            tags=["weather", "planning"],
            why=f"Hava durumu '{condition}' görünüyor; dış aktiviteleri ertele veya iç mekana al.",
            sources=["weather"],
            due_at=_iso_in_hours(4),
            confidence=0.78 + _energy_bonus(energy_level),
        )
    elif condition:
        add(
            title="Gün planını hava durumuna göre ayarla",
            priority="P3",
            tags=["weather", "planning"],
            why=f"Hava durumu '{condition}'. Küçük plan optimizasyonu önerildi.",
            sources=["weather"],
            due_at=_iso_in_hours(8),
            confidence=0.62 + _energy_bonus(energy_level),
        )

    if isinstance(temp_c, (int, float)) and temp_c <= 2:
        add(
            title="Soğuk hava: dışarı çıkışları azalt",
            priority="P3",
            tags=["weather", "health"],
            why=f"Sıcaklık {temp_c}°C; kısa/az dış aktivite daha güvenli.",
            sources=["weather"],
            due_at=_iso_in_hours(6),
            confidence=0.66,
        )

    # Rule 2: GitHub workload pressure
    open_prs = github.get("open_prs")
    open_issues = github.get("open_issues")

    if isinstance(open_prs, int) and open_prs >= 5:
        add(
            title="PR kuyruğunu temizle (review/merge)",
            priority="P1",
            tags=["github", "delivery"],
            why=f"Açık PR sayısı {open_prs}; review gecikmesi risk oluşturuyor.",
            sources=["github"],
            due_at=_iso_in_hours(3),
            confidence=0.82,
            actions=[
                {"label": "PR listesine git", "type": "link", "target": "https://github.com"}
            ],
        )
    elif isinstance(open_prs, int) and open_prs > 0:
        add(
            title="Açık PR'leri sırala ve önceliklendir",
            priority="P2",
            tags=["github", "planning"],
            why=f"{open_prs} açık PR var; en kritik olanları seç.",
            sources=["github"],
            due_at=_iso_in_hours(6),
            confidence=0.74,
        )

    if isinstance(open_issues, int) and open_issues >= 10:
        add(
            title="Issue triage yap (etiketle/assign et)",
            priority="P2",
            tags=["github", "maintenance"],
            why=f"Açık issue sayısı {open_issues}; backlog büyüyor.",
            sources=["github"],
            due_at=_iso_in_hours(12),
            confidence=0.72,
        )

    # Rule 3: News-driven awareness
    if isinstance(news, list) and len(news) > 0:
        top = news[0]
        top_title = top.get("title") if isinstance(top, dict) else None
        add(
            title="Gündemi tarayıp 5dk özet çıkar",
            priority="P4",
            tags=["news", "awareness"],
            why=f"Öne çıkan başlık: {top_title}" if top_title else "Gündem verisi mevcut.",
            sources=["news"],
            due_at=_iso_in_hours(24),
            confidence=0.55,
        )

    # Fillers: deterministic small tasks to reach limit
    filler_titles = [
        "Bugünün 3 hedefini yaz",
        "Inbox temizliği (10dk)",
        "Plan: 1 saat deep work blokla",
        "Kısa mola + su iç",
        "Yarın için 1 risk notu",
    ]

    while len(missions) < limit:
        title = rng.choice(filler_titles)
        pr: Priority = rng.choice(["P2", "P3", "P4"])
        add(
            title=title,
            priority=pr,
            tags=["routine"],
            why="Deterministik demo görevi (seed ile sabit).",
            sources=["synthetic"],
            due_at=None,
            confidence=0.40,
            actions=[{"label": "Lab'a git", "type": "link", "target": "/lab"}],
        )

    # Add generated-at for easier UI display
    for m in missions:
        m.setdefault("generated_at", _now_iso())

    return missions[:limit]
