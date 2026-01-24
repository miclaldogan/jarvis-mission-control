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
