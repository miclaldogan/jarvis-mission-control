from __future__ import annotations

import random
import uuid
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
    exclude_keys: Optional[set[str]] = None,
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

    def mission_key(*, title: str, priority: str, category: str) -> str:
        return f"{(title or '').strip().lower()}|{(priority or '').strip().lower()}|{(category or '').strip().lower()}"

    # Keys to avoid generating (e.g., existing DB missions)
    seen_keys: set[str] = set(exclude_keys or set())
    
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
        candidate_key = mission_key(title=gm.title, priority=gm.priority, category=gm.category)
        if candidate_key in seen_keys:
            continue

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
            "id": f"msn_{uuid.uuid4().hex[:12]}",
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
        seen_keys.add(candidate_key)

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
        {
            "title": "Kritik bağımlılık güncellemelerini kontrol et",
            "priority": "P2",
            "category": "work",
            "energy_cost": "medium",
            "duration_minutes": 20,
            "tags": ["maintenance", "deps"],
            "why": "Küçük güncellemeler, büyük hataları önler.",
            "pack": "maintenance",
            "rule": "deps_review",
        },
        {
            "title": "Kısa kod inceleme: son PR'ları tara",
            "priority": "P2",
            "category": "work",
            "energy_cost": "medium",
            "duration_minutes": 15,
            "tags": ["code-review", "quality"],
            "why": "Erken inceleme, riskleri azaltır.",
            "pack": "quality",
            "rule": "quick_review",
        },
        {
            "title": "Testleri çalıştır ve kırıkları not et",
            "priority": "P2",
            "category": "work",
            "energy_cost": "low",
            "duration_minutes": 10,
            "tags": ["tests", "quality"],
            "why": "Günlük test koşumu regressions yakalar.",
            "pack": "quality",
            "rule": "daily_tests",
        },
        {
            "title": "Dokümantasyonda 1 iyileştirme yap",
            "priority": "P3",
            "category": "admin",
            "energy_cost": "low",
            "duration_minutes": 15,
            "tags": ["docs", "maintenance"],
            "why": "Demo/kurulum dokümanı ekip hızını artırır.",
            "pack": "maintenance",
            "rule": "docs_update",
        },
        {
            "title": "Log'larda hata/uyarı var mı kontrol et",
            "priority": "P3",
            "category": "system",
            "energy_cost": "low",
            "duration_minutes": 10,
            "tags": ["ops", "monitoring"],
            "why": "Küçük uyarılar büyümeden yakalanır.",
            "pack": "ops",
            "rule": "log_review",
        },
        {
            "title": "Cache demo için aynı seed ile tekrar dene",
            "priority": "P3",
            "category": "study",
            "energy_cost": "low",
            "duration_minutes": 5,
            "tags": ["cache", "redis", "demo"],
            "why": "HIT/MISS davranışını gözlemlemek için stabil seed kullan.",
            "pack": "demo",
            "rule": "cache_proof",
        },
        {
            "title": "Kısa mola: 10 derin nefes",
            "priority": "P4",
            "category": "health",
            "energy_cost": "low",
            "duration_minutes": 2,
            "tags": ["health", "focus"],
            "why": "Kısa nefes egzersizi odak resetler.",
            "pack": "routine",
            "rule": "breathing",
        },
        {
            "title": "5dk yürüyüş (odak reset)",
            "priority": "P4",
            "category": "health",
            "energy_cost": "low",
            "duration_minutes": 5,
            "tags": ["health", "break"],
            "why": "Kısa hareket kan dolaşımını artırır ve odak tazeler.",
            "pack": "routine",
            "rule": "walk_break",
        },
        {
            "title": "Günün 1 önceliğini netleştir",
            "priority": "P3",
            "category": "admin",
            "energy_cost": "low",
            "duration_minutes": 5,
            "tags": ["planning", "focus"],
            "why": "Tek bir odak noktası seçmek dağılmayı azaltır.",
            "pack": "routine",
            "rule": "single_priority",
        },
        {
            "title": "Bugün için 1 küçük teslim edilebilir çıktıyı seç",
            "priority": "P3",
            "category": "work",
            "energy_cost": "low",
            "duration_minutes": 10,
            "tags": ["planning", "delivery"],
            "why": "Küçük ama tamamlanabilir hedefler momentum sağlar.",
            "pack": "delivery",
            "rule": "small_win",
        },
        {
            "title": "PR/branch listesini gözden geçir",
            "priority": "P3",
            "category": "work",
            "energy_cost": "low",
            "duration_minutes": 10,
            "tags": ["git", "hygiene"],
            "why": "Dallanma/PR hijyeni merge risklerini azaltır.",
            "pack": "quality",
            "rule": "branch_hygiene",
        },
        {
            "title": "1 test ekle veya flaky testi işaretle",
            "priority": "P2",
            "category": "work",
            "energy_cost": "medium",
            "duration_minutes": 20,
            "tags": ["tests", "quality"],
            "why": "Küçük test iyileştirmeleri regresyonları erken yakalar.",
            "pack": "quality",
            "rule": "add_or_tag_test",
        },
        {
            "title": "Log seviyelerini kontrol et (INFO/WARN/ERROR)",
            "priority": "P3",
            "category": "system",
            "energy_cost": "low",
            "duration_minutes": 10,
            "tags": ["ops", "logging"],
            "why": "Gereksiz gürültü gerçek hataları gizlemesin.",
            "pack": "ops",
            "rule": "log_levels",
        },
        {
            "title": "Docker compose ile hızlı health-check turu",
            "priority": "P2",
            "category": "system",
            "energy_cost": "low",
            "duration_minutes": 10,
            "tags": ["docker", "ops"],
            "why": "Servisler ayakta mı? Demo öncesi hızlı doğrulama.",
            "pack": "ops",
            "rule": "compose_health",
        },
        {
            "title": "API sözleşmesini (docs) 1 kez gözden geçir",
            "priority": "P3",
            "category": "study",
            "energy_cost": "low",
            "duration_minutes": 15,
            "tags": ["docs", "api"],
            "why": "Sözleşme tutarlılığı demo akışını rahatlatır.",
            "pack": "maintenance",
            "rule": "api_contract_review",
        },
        {
            "title": "Context snapshot alanlarını hızlı kontrol et",
            "priority": "P3",
            "category": "study",
            "energy_cost": "low",
            "duration_minutes": 10,
            "tags": ["context", "schema"],
            "why": "Context şeması stabil kalırsa skorlar ve UI daha güvenilir olur.",
            "pack": "maintenance",
            "rule": "context_schema_check",
        },
        {
            "title": "Redis cache anahtar formatını örnekle doğrula",
            "priority": "P2",
            "category": "system",
            "energy_cost": "medium",
            "duration_minutes": 15,
            "tags": ["redis", "cache"],
            "why": "Tutarlı key formatı hit-rate’i artırır.",
            "pack": "demo",
            "rule": "redis_key_check",
        },
        {
            "title": "Frontend prod build al (vite) ve hata var mı bak",
            "priority": "P2",
            "category": "work",
            "energy_cost": "medium",
            "duration_minutes": 15,
            "tags": ["frontend", "build"],
            "why": "Demo öncesi build kırığı sürpriz olmasın.",
            "pack": "ops",
            "rule": "frontend_build",
        },
        {
            "title": "Backend testlerini hızlı koş (pytest -q)",
            "priority": "P2",
            "category": "work",
            "energy_cost": "medium",
            "duration_minutes": 15,
            "tags": ["backend", "tests"],
            "why": "Kritik endpoint’ler sağlamsa demo daha rahat.",
            "pack": "quality",
            "rule": "backend_pytest_quick",
        },
        {
            "title": "Rate limit davranışını 1 örnek istekle doğrula",
            "priority": "P3",
            "category": "system",
            "energy_cost": "low",
            "duration_minutes": 10,
            "tags": ["rate-limit", "api"],
            "why": "Limitler beklenmedik 429 üretmesin.",
            "pack": "ops",
            "rule": "rate_limit_check",
        },
        {
            "title": "Open missions listesini gözden geçir, 1 tanesini kapat",
            "priority": "P3",
            "category": "admin",
            "energy_cost": "low",
            "duration_minutes": 10,
            "tags": ["workflow", "cleanup"],
            "why": "Küçük kapanışlar ilerleme hissini artırır.",
            "pack": "routine",
            "rule": "close_one",
        },
        {
            "title": "Demo akışını 3 maddeyle not al",
            "priority": "P2",
            "category": "admin",
            "energy_cost": "low",
            "duration_minutes": 10,
            "tags": ["demo", "planning"],
            "why": "Kısa demo script’i stres azaltır.",
            "pack": "demo",
            "rule": "demo_notes",
        },
        {
            "title": "UI'da 1 küçük metin/etiket tutarlılığını düzelt",
            "priority": "P3",
            "category": "work",
            "energy_cost": "low",
            "duration_minutes": 15,
            "tags": ["ui", "polish"],
            "why": "Tutarlı metinler kullanıcı güvenini artırır.",
            "pack": "quality",
            "rule": "ui_copy_fix",
        },
        {
            "title": "Bir endpoint için örnek curl komutu ekle",
            "priority": "P3",
            "category": "admin",
            "energy_cost": "low",
            "duration_minutes": 10,
            "tags": ["docs", "api"],
            "why": "Kullanım örnekleri onboarding'i hızlandırır.",
            "pack": "maintenance",
            "rule": "add_curl_example",
        },
        {
            "title": "Bir hata senaryosu için kullanıcı mesajını doğrula",
            "priority": "P3",
            "category": "work",
            "energy_cost": "low",
            "duration_minutes": 10,
            "tags": ["ux", "errors"],
            "why": "Net hata mesajı debug süresini kısaltır.",
            "pack": "quality",
            "rule": "error_message_check",
        },
        {
            "title": "Missions generate limitini 1 kez 30 ile dene",
            "priority": "P3",
            "category": "study",
            "energy_cost": "low",
            "duration_minutes": 5,
            "tags": ["missions", "demo"],
            "why": "Limit davranışı demo sırasında sürpriz olmasın.",
            "pack": "demo",
            "rule": "generate_max_limit",
        },
        {
            "title": "Context sayfasında source sayısını kontrol et",
            "priority": "P3",
            "category": "study",
            "energy_cost": "low",
            "duration_minutes": 10,
            "tags": ["context", "ui"],
            "why": "Kaynak sayıları beklenen aralıkta mı kontrol et.",
            "pack": "demo",
            "rule": "context_sources_check",
        },
        {
            "title": "System vitals metriklerini hızlı gözden geçir",
            "priority": "P3",
            "category": "system",
            "energy_cost": "low",
            "duration_minutes": 10,
            "tags": ["metrics", "ops"],
            "why": "CPU/RAM/latency trendleri erken uyarı sağlar.",
            "pack": "ops",
            "rule": "vitals_review",
        },
        {
            "title": "Nginx/Proxy konfigini 1 kez kontrol et",
            "priority": "P3",
            "category": "system",
            "energy_cost": "low",
            "duration_minutes": 10,
            "tags": ["nginx", "ops"],
            "why": "Proxy ayarları doğruysa prod deneyimi stabil olur.",
            "pack": "ops",
            "rule": "nginx_check",
        },
        {
            "title": "README'de kurulum adımlarını 1 kez takip et",
            "priority": "P3",
            "category": "admin",
            "energy_cost": "low",
            "duration_minutes": 15,
            "tags": ["docs", "onboarding"],
            "why": "Doküman, gerçek kullanımda çalışıyor mu doğrula.",
            "pack": "maintenance",
            "rule": "readme_walkthrough",
        },
        {
            "title": "1 küçük refactor: isimlendirme/tutarlılık",
            "priority": "P3",
            "category": "work",
            "energy_cost": "medium",
            "duration_minutes": 20,
            "tags": ["refactor", "quality"],
            "why": "Küçük refactor’lar uzun vadeli bakım maliyetini düşürür.",
            "pack": "quality",
            "rule": "small_refactor",
        },
        {
            "title": "Güncel bağımlılık lisanslarını hızlı tarama",
            "priority": "P3",
            "category": "work",
            "energy_cost": "low",
            "duration_minutes": 15,
            "tags": ["license", "compliance"],
            "why": "Lisans sürprizleri ileride sorun çıkarabilir.",
            "pack": "maintenance",
            "rule": "license_scan",
        },
        {
            "title": "Sentry/telemetry ayarlarını kontrol et (varsa)",
            "priority": "P4",
            "category": "system",
            "energy_cost": "low",
            "duration_minutes": 10,
            "tags": ["telemetry", "ops"],
            "why": "Gözlemlenebilirlik demo sırasında debug'u kolaylaştırır.",
            "pack": "ops",
            "rule": "telemetry_check",
        },
        {
            "title": "Günün sonunda 2 satır öğrenim notu çıkar",
            "priority": "P4",
            "category": "study",
            "energy_cost": "low",
            "duration_minutes": 5,
            "tags": ["learning", "routine"],
            "why": "Kısa öğrenim notları kalıcılığı artırır.",
            "pack": "routine",
            "rule": "learning_note",
        },
    ]

    used_fillers: set[str] = set()
    
    while len(missions) < limit:
        remaining = []
        for f in filler_tasks:
            key = mission_key(title=f["title"], priority=f["priority"], category=f["category"])
            if f["title"] in used_fillers:
                continue
            if key in seen_keys:
                continue
            remaining.append((f, key))

        if not remaining:
            break

        filler, filler_key = rng.choice(remaining)
        used_fillers.add(filler["title"])

        score = calculate_mission_score(
            due_at=None,
            tags=filler.get("tags", []),
            context=context,
            preferences=preferences,
        )
        score_dict = score.to_dict()
        
        idx = len(missions) + 1
        missions.append({
            "id": f"msn_{uuid.uuid4().hex[:12]}",
            "title": filler["title"],
            "priority": filler["priority"],
            "priority_score": score_dict["total"],
            "score_breakdown": score_dict["breakdown"],
            "reasons": [
                f"[{filler['pack']}:{filler['rule']}] {filler['why']}",
                *score_dict["reasons"],
            ],
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
        seen_keys.add(filler_key)

    # ═══════════════════════════════════════════════════════════════════
    # PHASE 3: Sort by priority and return
    # ═══════════════════════════════════════════════════════════════════
    missions.sort(key=lambda m: (_priority_to_num(m["priority"]), -m.get("priority_score", 0)))

    return missions[:limit]
