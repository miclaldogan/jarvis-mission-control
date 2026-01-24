# 🤖 JARVIS Mission Control

**An adaptive task orchestration system that generates, prioritizes, and adjusts missions based on real-time context.**

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18.3+-blue.svg)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.6+-blue.svg)](https://www.typescriptlang.org/)
[![Redis](https://img.shields.io/badge/Redis-Cache-red.svg)](https://redis.io/)

---

## 🎯 Why This Isn't Just a To-Do App

### 1. **Context-Aware Mission Generation**
**To-Do Apps:** Static lists you create manually
**JARVIS:** Dynamic missions generated from real-world context

```python
# JARVIS analyzes your environment in real-time
context = {
    "weather": "Clear skies, 22°C",           # ☀️ Perfect for outdoor tasks
    "github": "5 open issues, 2 urgent",      # 🐛 Dev work needed
    "calendar": "Team standup in 30 minutes", # 📅 Meeting prep required
    "news": "Tech conference announced"       # 📰 Opportunity detected
}

# Generates missions that make sense RIGHT NOW
missions = generate_missions(context)
# → "Morning jog in the park"        (weather-aware)
# → "Review PR #127"                 (GitHub-aware)
# → "Prepare standup notes"          (calendar-aware)
```

### 2. **Explainable AI Scoring**
**To-Do Apps:** You manually decide priority
**JARVIS:** AI calculates priority with transparent reasoning

Every mission has a **visual score breakdown**:
```
Deadline Factor:    +0.42  ━━━━━━━━━━━━━━━━━━━━ 84%  "Due in 2 hours"
Context Relevance:  +0.31  ━━━━━━━━━━━━━━ 62%      "GitHub activity spike"
Energy Match:       +0.18  ━━━━━━━━ 36%            "High energy time of day"
User Preference:    +0.09  ━━━━ 18%                "Recent focus area"
────────────────────────────────────────────────
Total Score:         1.00  100/100
```

You always know **WHY** a task is prioritized.

### 3. **Real-Time Adaptation**
**To-Do Apps:** Manual updates when things change
**JARVIS:** Automatic adaptation to context shifts

```diff
Before: Clear Weather ☀️              After: Heavy Rain ☔
+ Morning jog in the park          - Morning jog in the park
+ Outdoor team lunch              - Outdoor team lunch
  Review PR #127                    Review PR #127
  Team standup prep                 Team standup prep
                                  + Work from home setup
                                  + Indoor coding focus time
```

Use the **Simulation Lab** to test how missions change with different contexts.

### 4. **Production-Ready Performance**
**To-Do Apps:** Simple CRUD operations
**JARVIS:** Caching, observability, graceful degradation

```
First Call:  X-Cache: MISS  |  2847ms  |  Full computation
Second Call: X-Cache: HIT   |  12ms    |  ⚡ 237x faster
```

- **Redis caching** for expensive computations
- **Structured JSON logging** for observability
- **Health checks** with dependency monitoring
- **Prometheus metrics** for production monitoring
- **Request ID tracking** across the stack

### 5. **Temporal Intelligence**
**To-Do Apps:** Snapshot of your current list
**JARVIS:** Historical view of mission evolution

Compare mission runs throughout the day:
```
Run #13 (08:00 AM)     →     Run #15 (04:00 PM)
Morning context              Afternoon context

🔴 Removed:                  🟢 Added:
- Morning jog (time passed)  + Review PR #127 (new activity)
- Review email (completed)   + Prepare presentation (reminder)

⚪ Kept in both:
- Team standup (still scheduled)
- Deploy backend (still pending)
```

See how your missions evolved as context changed.

---

## 🚀 Features

### Core System
- 🎯 **Dynamic Mission Generation** - Context-aware task orchestration
- 📊 **Explainable Scoring** - Transparent AI decision-making
- 🌐 **Real-Time Context** - Weather, GitHub, Calendar, News integration
- ⚡ **Smart Caching** - Redis-powered performance (200x+ speedup)
- 🔍 **Observability** - Structured logging, health checks, metrics

### User Experience
- 📈 **Score Breakdown Modal** - Visual priority explanation
- 🧪 **Simulation Lab** - Test scenario impacts on missions
- 📅 **Run History** - Compare mission evolution over time
- 🎨 **Cyber UI** - Retro-futuristic mission control aesthetic
- 📊 **Cache Performance** - Real-time HIT/MISS visualization

### Production Readiness
- 🏥 **Health Endpoints** - Dependency monitoring (Redis, APIs)
- 📝 **Structured Logging** - JSON format for log aggregation
- 🆔 **Request Tracking** - Distributed tracing with Request IDs
- 📈 **Prometheus Metrics** - System performance monitoring
- 🔄 **Graceful Degradation** - Continues with partial failures

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    JARVIS Mission Control               │
└─────────────────────────────────────────────────────────┘

   Frontend (React)              Backend (FastAPI)
   ┌──────────────┐             ┌────────────────┐
   │  Dashboard   │────────────▶│  Mission API   │
   │  Simulation  │             │  Scoring Logic │
   │  Run History │             │  Context Svc   │
   │  Reports     │             │  Cache Layer   │
   └──────────────┘             └────────────────┘
                                      │     │
                    ┌─────────────────┘     └──────────────┐
                    │                                       │
              ┌─────▼─────┐                        ┌───────▼────┐
              │   Redis   │                        │ External   │
              │   Cache   │                        │    APIs    │
              └───────────┘                        └────────────┘
                                                   • Weather API
                                                   • GitHub API
                                                   • Calendar
                                                   • News Feed
```

See [docs/architecture.md](docs/architecture.md) for detailed design.

---

## 📦 Project Structure

```
jarvis-mission-control/
├── backend/              # FastAPI backend service
│   ├── app/
│   │   ├── api/         # API endpoints
│   │   ├── services/    # Business logic
│   │   ├── cache.py     # Redis caching
│   │   ├── logging_config.py  # Structured logging
│   │   └── main.py      # Application entry
│   └── tests/           # Backend tests
├── client/              # React frontend
│   ├── src/
│   │   ├── components/  # UI components
│   │   ├── pages/       # Page components
│   │   ├── hooks/       # Custom React hooks
│   │   └── lib/         # Utilities
│   └── public/          # Static assets
├── docs/                # Documentation
│   ├── architecture.md
│   ├── api_contract.md
│   ├── presentation_demo.md
│   └── ...
├── infra/               # Infrastructure
│   ├── nginx/           # Nginx config
│   └── scripts/         # Deployment scripts
└── docker-compose.yml   # Local development setup
```

---

## 🚀 Quick Start

### Prerequisites
- **Docker** and **Docker Compose** (for Redis)
- **Python 3.11+** (for backend)
- **Node.js 18+** (for frontend)

### 1. Start Backend + Redis
```bash
# Start services
docker-compose up -d

# Check health
curl http://localhost:8000/api/v1/health
```

### 2. Start Frontend
```bash
cd client
npm install
npm run dev

# Open browser at http://localhost:5173
```

### 3. Generate Your First Mission Run
1. Open Dashboard at `http://localhost:5173`
2. Click **"Generate Missions"**
3. See real-time context and generated tasks
4. Click any task to view score breakdown

---

## 🧪 Try It Out

### Simulation Lab
Test how context changes affect missions:
```
1. Go to Simulation Lab page
2. Toggle "Heavy Rain" ☔
3. Set "20 GitHub Issues" 🐛
4. Click "Generate Missions"
5. See diff view: outdoor tasks removed, dev tasks added
```

### Cache Performance
Observe Redis caching in action:
```
1. Go to Reports page
2. Load mission report (MISS: ~2000ms)
3. Reload same report (HIT: ~10ms)
4. See 200x+ speedup badge
```

### Mission Evolution
Compare runs throughout the day:
```
1. Go to Mission Run History
2. Select two different runs
3. See which tasks were added/removed/kept
4. Understand how context shaped priorities
```

---

## 🧪 Development

### Run Tests
```bash
# Backend tests
cd backend
pytest -v

# Frontend tests (if added)
cd client
npm test
```

### Demo Script
Run automated demo verification:
```bash
./infra/scripts/demo.sh
```

### View Metrics
```bash
# Prometheus metrics
curl http://localhost:8000/metrics

# Redis cache keys
docker exec -it jarvis-redis redis-cli KEYS "cache:*"
```

---

## 📚 Documentation

- [Architecture Design](docs/architecture.md) - System design and components
- [API Contract](docs/api_contract.md) - REST API specification
- [Presentation Demo](docs/presentation_demo.md) - 90-second demo script
- [Mission Rules](docs/mission_rules.md) - Scoring algorithm details
- [Context Schema](docs/context_schema.md) - External data integration

---

## 🛠️ Tech Stack

### Backend
- **FastAPI** - Modern async web framework
- **Redis** - High-performance caching layer
- **Prometheus** - Metrics and monitoring
- **Pydantic** - Data validation
- **asyncio** - Concurrent operations

### Frontend
- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Fast build tool
- **Wouter** - Lightweight routing
- **shadcn/ui** - Component library
- **Tailwind CSS** - Utility-first styling

### DevOps
- **Docker Compose** - Local development
- **Nginx** - Reverse proxy (production)
- **GitHub Actions** - CI/CD (future)

---

## 👥 Team

This project was built by a 4-person team as part of a university course:
- **Backend Development** - Context services, caching, scoring logic
- **Frontend Development** - React UI, simulation lab, run history
- **Integration & Testing** - API contracts, demo scripts, E2E tests
- **DevOps & Documentation** - Docker setup, monitoring, architecture docs

---

## 📝 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) for details.

---

## 🎓 Academic Context

**Course:** Advanced Software Engineering
**University:** [Your University Name]
**Semester:** Spring 2025
**Project Goal:** Build a production-ready AI system with explainability and observability

---

## 🙏 Acknowledgments

- FastAPI for the excellent async framework
- Redis for blazing-fast caching
- shadcn/ui for beautiful components
- The entire open-source community

---

<div align="center">

**Made with 🤖 by the JARVIS Team**

[Report Bug](https://github.com/miclaldogan/jarvis-mission-control/issues) · [Request Feature](https://github.com/miclaldogan/jarvis-mission-control/issues)

</div>
