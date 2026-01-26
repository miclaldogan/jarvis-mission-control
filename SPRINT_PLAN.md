# 🎯 JARVIS Mission Control - 3 Kişilik Sprint Planı

## 📊 Genel Bakış

**Toplam Issue:** 17 (2 Epic + 15 Implementation)
**Ekip:** İclal (Backend), Merve (Synthetic/Cache), Burcu (Frontend)
**Sprint Süresi:** 3 sprint (toplam ~3-4 hafta)

---

## 🔥 Kritik Başarı Kriterleri (Hoca Etkilenmesi İçin)

### 1. Görev Yaşam Döngüsü + Detay Sayfası ✅
- **Problem:** "Details'a basınca göremiyorum" = demo kıran bug
- **Çözüm:** Task'lar ID ile okunabilir (#99, #107)

### 2. Explainability (Neden bu görev?) ✅
- **Problem:** Skor bileşenleri görünmüyor
- **Çözüm:** UI'da "deadline 0.42, context 0.31" breakdown (#100, #107)

### 3. Scenario Simulator (WOW efekti) ✅
- **Problem:** Statik görev listesi sıkıcı
- **Çözüm:** Toggle'lar → görevler değişiyor (#98, #108)

---

## 📌 EPIC'LER (Büyük Resim)

### EPIC-A: Mission Lifecycle & Control Plane (#97)
**Hedef:** "To-do app" → "Kontrol edilebilir sistem"

**Özellikler:**
- Mission Run kavramı (her generate = bir run_id)
- Task state transitions (planned → in_progress → done)
- Audit log (neden değişti?)

**Demo Etkisi:** "Gün içinde context değişince yeni run oluşuyor"

### EPIC-B: Scenario Simulator (#98)
**Hedef:** Sunumun yıldızı

**Özellikler:**
- Toggle'lar: Weather, GitHub, Calendar, News
- Diff View: Hangi görev eklendi/kalktı
- Before/After karşılaştırma

**Demo Etkisi:** "Toggle'a basınca görevler değişiyor (gözünün önünde)"

---

## 👥 ROL DAĞILIMI

### �� İCLAL (Backend Core - EN ZOR GÖREVLER)

#### Difficulty: 🔥🔥🔥🔥🔥 (Very Hard)
- #99: Task Detail Endpoint & History API
- #100: Prioritization Explainability (algoritma tasarımı)
- #102: Mission Run Lifecycle & State Management
- #103: Audit Log System

#### Difficulty: 🔥🔥🔥 (Hard)
- #101: Multi-Source Context Ingestion (API integration)

**Toplam:** 5 task (hepsi P0/P1)

---

### ⚙️ MERVE (Synthetic + Cache + Reports)

#### Difficulty: 🔥�� (Medium)
- #105: Heavy Report Endpoints
- #106: Cache Evidence System (UI badges)

#### Difficulty: 🔥 (Easy)
- #104: Synthetic Task Generation Enhancement

**Toplam:** 3 task (P1/P2)

---

### 🎨 BURCU (Frontend - Ürün Hissi)

#### Difficulty: 🔥��🔥 (Hard)
- #108: Simulation Lab UI (diff view)
- #109: Mission Run History UI (timeline)

#### Difficulty: 🔥🔥 (Medium)
- #107: Task Detail Modal with Score Breakdown
- #110: Today Missions Dashboard with Filters

**Toplam:** 4 task (P0/P1)

---

## 🚀 SPRINT PLANI

### Sprint 1 - Demo Kıran Şeyleri Düzelt (1 hafta)
**Hedef:** Basic demo flow çalışsın

✅ Must Have:
- #99: Task detail endpoint (İclal)
- #100: Score breakdown API (İclal)
- #107: Task detail modal UI (Burcu)
- #110: Dashboard with filters (Burcu)
- #111: Fix demo-breaking bugs (Tüm ekip)

**Kabul Kriteri:** Dashboard → Click task → See breakdown → Complete → No crash

---

### Sprint 2 - WOW Features (1-1.5 hafta)
**Hedef:** Simulation + Run history

✅ Must Have:
- #102: Mission run lifecycle (İclal)
- #108: Simulation Lab UI (Burcu + İclal API)
- #109: Run history UI (Burcu)
- #105: Heavy report endpoints (Merve)
- #106: Cache evidence badges (Merve + Burcu)

**Kabul Kriteri:** Toggle rain → tasks change → Compare runs → Cache HIT/MISS visible

---

### Sprint 3 - Şov + Sağlamlık (1 hafta)
**Hedef:** Production-ready + Sunum hazırlığı

✅ Must Have:
- #101: Multi-source ingestion (İclal)
- #103: Audit log (İclal)
- #104: Realistic synthetic tasks (Merve)
- #112: Observability (İclal)
- #113: Demo script + docs (Tüm ekip)

**Kabul Kriteri:** Graceful degradation + Metrics + 90-second demo script

---

## 🎬 90 SANİYELİK DEMO AKIŞI

```
[0:00-0:15] Context Panel
            → Weather/GitHub/News canlı görünsün

[0:15-0:30] Generate Missions
            → Run #15 oluşsun (12 task)

[0:30-0:45] Task Detail
            → Score breakdown: deadline(0.42) + context(0.31)...

[0:45-1:00] Simulation Lab
            → Toggle rain → outdoor tasks kaybolsun
            → Toggle 20 issues → dev tasks yükselsin

[1:00-1:15] Cache Evidence
            → First call MISS 2000ms
            → Second call HIT 10ms (200x faster!)

[1:15-1:30] Run History
            → Run #15 vs Run #13 diff
            → "Context değişti, görevler adapte oldu"
```

**Sonuç:** "Bu basit to-do değil, ajan orkestrasyonu!"

---

## 📈 BAŞARI METRİKLERİ

### Teknik Metrikler:
- ✅ 3+ external source (Weather + GitHub + News)
- ✅ Cache hit rate >80%
- ✅ Task detail fetch <100ms
- ✅ Simulation diff <2s

### Demo Metrikleri:
- ✅ Hoca "vay be" dedi mi?
- ✅ "Bu sadece to-do" eleştirisi bitti mi?
- ✅ 90 saniye boyunca crash olmadı mı?

---

## 🔗 GitHub Issues

**Epic'ler:**
- #97: EPIC-A (Lifecycle)
- #98: EPIC-B (Simulator)

**İclal (Backend):**
- #99, #100, #101, #102, #103

**Merve (Synthetic/Cache):**
- #104, #105, #106

**Burcu (Frontend):**
- #107, #108, #109, #110

**Sprint Tasks:**
- #111, #112, #113

---

## 🎯 NET DELİVERABLE (Her Kişi)

### İclal:
→ "Task neden bu öncelikte?" sorusuna matematiksel cevap
→ Mission run history (context snapshot ile)

### Merve:
→ Cache kanıtı: MISS vs HIT (rozetlerle görünür)
→ 1M synthetic task generation

### Burcu:
→ Simulation Lab (toggle → diff view)
→ Professional dashboard UX

---

**🚀 Hedef:** "3 kişi bu kadar mı?" eleştirisini bitirmek!

---

## 🎯 YENİ EKLENEN GÖREVLER (WOW Paketi Tamamlama)

### WOW-1: Mission Run + Compare ✅
**Backend:** #102 (İclal) - Mission Run Lifecycle
**Frontend:** #109 (Burcu) - Run History UI + Compare
**Enhancement:** #115 (Burcu) - Run Badge & Dashboard Header

### WOW-2: Task Explainability ✅
**Backend:** #99 (İclal) - Task Detail API + #100 (İclal) - Score Breakdown
**Frontend:** #107 (Burcu) - Task Detail Modal with Breakdown
**Audit:** #103 (İclal) - Audit Log System

### WOW-3: Scenario Simulator ✅
**Backend:** #116 (İclal) - Scenario Simulation API
**Frontend:** #108 (Burcu) - Simulation Lab UI
**EPIC:** #98 - EPIC-B (Scenario Simulator)

### System Harmonics (Hoca Etkileyen) ✅
**Backend:** #118 (İclal) - Context Freshness & Anomaly Detection
**Frontend:** #114 (Burcu) - Context Health UI Component
**Base:** #101 (İclal) - Multi-Source Context Ingestion

### Cache Proof (Kriter-3 Kanıtı) ✅
**Backend:** #117 (Merve) - Make MISS Visibly Slow (1-3s)
**Backend:** #105 (Merve) - Heavy Report Endpoints
**Frontend:** #106 (Merve) - Cache Evidence Badges

---

## 📊 GÜNCEL İSTATİSTİKLER

**Toplam Issue:** 22 (2 EPIC + 20 Implementation)

**İclal (Backend Lead):** 7 task
- 5 original (core backend)
- 2 new (scenario API + context health)
- **En zor:** #100 (Explainability), #102 (Run Lifecycle)

**Merve (Cache/Synthetic):** 4 task
- 3 original (synthetic + reports + UI)
- 1 new (cache optimization)
- **Kritik:** #117 (MISS slow), #105 (Heavy reports)

**Burcu (Frontend UX):** 6 task
- 4 original (detail modal + simulation + run history + dashboard)
- 2 new (run badge + context health UI)
- **WOW:** #108 (Simulation UI), #114 (System Harmonics)

**Sprint Tasks (Tüm Ekip):** 3 task
- #111 (Sprint 1 - Demo blockers)
- #112 (Sprint 3 - Observability)
- #113 (Sprint 3 - Demo script)

---

## 🎬 75 SANİYELİK DEMO AKIŞI (Güncellenmiş)

```
[0:00-0:10] Global Context Page
            → System Harmonics dolu (#114)
            → 4 kaynak online, freshness göstergeleri
            → Anomaly: "GitHub issues spike: 15 → 23"

[0:10-0:20] Dashboard Header
            → RUN #15 badge (#115)
            → Context: 3m ago (fresh)
            → "GENERATE RUN" butonuna bas

[0:20-0:30] Task List
            → 12 görev geldi (#110)
            → Her kartda: priority bar + reason chips
            → Task'a tıkla → Details açıldı (#107)

[0:30-0:40] Task Details Panel
            → Score breakdown (#100): deadline(0.42) + context(0.31)...
            → Audit timeline (#103): "Run#14'te eklendi"
            → Reason chips: "rain", "github_issues_high"

[0:40-0:50] Simulation Lab
            → Toggle: sunny → rainy (#116, #108)
            → "Apply scenario" → Run #16 oluştu
            → Diff view: 3 görev gitti, 5 görev eklendi

[0:50-1:00] Cache Proof
            → Heavy report (#117)
            → First call: MISS 2100ms (#106 badge)
            → Second call: HIT 25ms
            → 80x speedup visible!

[1:00-1:15] Run History
            → Run timeline (#109)
            → Compare Run #16 vs #15
            → Context farkı + görev farkı açık
```

**Hoca Reaction:** "Bu basit to-do değil, kontrol edilebilir sistem + simulation lab!"

---

## ✅ TAMAMLANMA CHECKPOINT'LERİ

### Sprint 1 Sonu:
- [ ] Task details açılıyor ve score breakdown görünüyor
- [ ] Dashboard run badge + context age gösteriyor
- [ ] Cache MISS/HIT farkı bariz (2s vs 20ms)

### Sprint 2 Sonu:
- [ ] Simulation toggle'ları çalışıyor
- [ ] Diff view görevleri karşılaştırıyor
- [ ] Run history + compare feature çalışıyor
- [ ] System Harmonics dolu ve canlı

### Sprint 3 Sonu:
- [ ] 75 saniyelik demo script hazır
- [ ] Observability (logs, metrics, health check)
- [ ] Production deployment (Docker + SSL)

---

**🔗 GitHub:** https://github.com/miclaldogan/jarvis-mission-control/issues
**🚀 Son Güncelleme:** 5 yeni issue eklendi (WOW paketi tamamlandı)
