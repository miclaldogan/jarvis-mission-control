# JARVIS Mission Control - Architecture Overview

## 🎯 System Purpose
**Adaptive Task Orchestration System** that generates, prioritizes, and adjusts missions based on real-time context with transparent AI decision-making.

---

## 🏗️ High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        JARVIS Mission Control                       │
│                     (Explainable AI Task System)                    │
└─────────────────────────────────────────────────────────────────────┘

                              ▼
        ┌──────────────────────────────────────────────┐
        │          User Interaction Layer              │
        │  (React SPA - Port 5173 - Vite Dev Server)  │
        └──────────────────────────────────────────────┘
                              │
            ┌─────────────────┼─────────────────┐
            │                 │                 │
    ┌───────▼────────┐ ┌─────▼──────┐ ┌───────▼────────┐
    │   Dashboard    │ │ Simulation │ │  Run History   │
    │   • Context    │ │    Lab     │ │  • Timeline    │
    │   • Missions   │ │ • Scenarios│ │  • Comparison  │
    │   • Details    │ │ • Diff View│ │  • Evolution   │
    └────────────────┘ └────────────┘ └────────────────┘
                              │
                              │ HTTP/JSON API
                              ▼
        ┌──────────────────────────────────────────────┐
        │            API Gateway Layer                 │
        │   (FastAPI - Port 8000 - Request Router)    │
        │  • Request ID tracking                       │
        │  • Structured logging                        │
        │  • CORS handling                             │
        │  • Health checks                             │
        └──────────────────────────────────────────────┘
                              │
            ┌─────────────────┼─────────────────┐
            │                 │                 │
    ┌───────▼────────┐ ┌─────▼──────┐ ┌───────▼────────┐
    │  Mission API   │ │ Reports API│ │  System API    │
    │  /missions     │ │ /reports   │ │  /health       │
    │  /synthetic    │ │ /simulation│ │  /metrics      │
    └────────────────┘ └────────────┘ └────────────────┘
                              │
                              ▼
        ┌──────────────────────────────────────────────┐
        │           Business Logic Layer               │
        │      (Services - Core Intelligence)          │
        └──────────────────────────────────────────────┘
                              │
            ┌─────────────────┼─────────────────┐
            │                 │                 │
    ┌───────▼────────┐ ┌─────▼──────┐ ┌───────▼────────┐
    │ Context Service│ │   Scoring  │ │ Mission Service│
    │ • Weather API  │ │   Engine   │ │ • Generation   │
    │ • GitHub API   │ │ • Deadline │ │ • Filtering    │
    │ • Calendar API │ │ • Context  │ │ • Ranking      │
    │ • News Feed    │ │ • Energy   │ │ • Runs         │
    └────────────────┘ └────────────┘ └────────────────┘
                              │
                              ▼
        ┌──────────────────────────────────────────────┐
        │            Caching & Storage Layer           │
        │        (Redis - Port 6379 - In-Memory)       │
        │  • Synthetic task cache                      │
        │  • Mission load report cache                 │
        │  • Context snapshot cache                    │
        │  • Cache key versioning (v1)                 │
        └──────────────────────────────────────────────┘
                              │
                              ▼
        ┌──────────────────────────────────────────────┐
        │          Observability & Monitoring          │
        │  • Prometheus metrics (/metrics)             │
        │  • Structured JSON logs                      │
        │  • Request ID propagation                    │
        │  • Health checks with dependencies           │
        └──────────────────────────────────────────────┘
```

---

## 📊 Data Flow: Mission Generation

```
User Action                 Context Gathering           Scoring              Response
    │                            │                        │                     │
    │  1. Click "Generate"       │                        │                     │
    ├──────────────────────────► │                        │                     │
    │                            │                        │                     │
    │                            │  2. Fetch Context      │                     │
    │                            ├─────────────┐          │                     │
    │                            │             │          │                     │
    │                            │  ┌──────────▼────────┐ │                     │
    │                            │  │ External APIs     │ │                     │
    │                            │  │ • Weather: 22°C   │ │                     │
    │                            │  │ • GitHub: 5 issues│ │                     │
    │                            │  │ • Calendar: 3 evt │ │                     │
    │                            │  │ • News: 2 updates │ │                     │
    │                            │  └───────────────────┘ │                     │
    │                            │◄─────────────┘          │                     │
    │                            │                         │                     │
    │                            │  3. Pass Context        │                     │
    │                            ├────────────────────────►│                     │
    │                            │                         │                     │
    │                            │                         │  4. Generate Tasks  │
    │                            │                         ├──────────┐          │
    │                            │                         │          │          │
    │                            │                         │  ┌───────▼────────┐ │
    │                            │                         │  │ Task Pool      │ │
    │                            │                         │  │ • 50+ templates│ │
    │                            │                         │  │ • Filter by    │ │
    │                            │                         │  │   context      │ │
    │                            │                         │  └────────────────┘ │
    │                            │                         │◄─────────┘          │
    │                            │                         │                     │
    │                            │                         │  5. Score Each Task │
    │                            │                         ├──────────┐          │
    │                            │                         │          │          │
    │                            │                         │  ┌───────▼────────┐ │
    │                            │                         │  │ Score = f(     │ │
    │                            │                         │  │  deadline,     │ │
    │                            │                         │  │  context,      │ │
    │                            │                         │  │  energy,       │ │
    │                            │                         │  │  preference    │ │
    │                            │                         │  │ )              │ │
    │                            │                         │  └────────────────┘ │
    │                            │                         │◄─────────┘          │
    │                            │                         │                     │
    │                            │  6. Return Ranked Missions                   │
    │◄─────────────────────────────────────────────────────────────────────────┤
    │                            │                         │                     │
    │  7. Display UI             │                         │                     │
    │  • Mission list            │                         │                     │
    │  • Score badges            │                         │                     │
    │  • Context panel           │                         │                     │
    └────────────────────────────┘                         │                     │
```

---

## 🎯 Key Components

### 1. Frontend (React SPA)
**Location:** `client/src/`
**Port:** 5173 (Vite dev server)

```typescript
// Page Components
Dashboard.tsx         → Mission list + context panel
SimulationLab.tsx     → Scenario testing + diff view
MissionRunHistory.tsx → Timeline + comparison view
Reports.tsx           → Cache performance + metrics

// UI Components
TaskDetailDialog.tsx  → Score breakdown modal
CacheBadge.tsx        → HIT/MISS indicators
CyberCard.tsx         → Gradient cyber-themed cards
```

**Tech:** React 18, TypeScript, Vite, Wouter, shadcn/ui, Tailwind CSS

---

### 2. Backend API (FastAPI)
**Location:** `backend/app/`
**Port:** 8000

```python
# API Endpoints
/api/v1/missions         → Generate missions, get details
/api/v1/synthetic/tasks  → Synthetic task generation
/api/v1/reports/*        → Mission load, aggregations
/api/v1/simulation/*     → Scenario testing
/api/v1/health           → Health checks
/metrics                 → Prometheus metrics

# Middleware
request_id_middleware()  → Track requests across stack
structured_logging()     → JSON log formatting
```

**Tech:** FastAPI, Pydantic, asyncio, Redis

---

### 3. Business Logic Services
**Location:** `backend/app/services/`

```python
context.py     → Fetch weather, GitHub, calendar, news
missions.py    → Generate + filter + rank missions
scoring.py     → Calculate priority scores with reasoning
storage.py     → Mission run persistence (future: DB)
```

**Scoring Algorithm:**
```
score = w1 * deadline_factor(task, context)
      + w2 * context_relevance(task, context)
      + w3 * energy_match(task, context)
      + w4 * user_preference(task, history)

where: w1=0.4, w2=0.3, w3=0.2, w4=0.1 (tunable)
```

---

### 4. Caching Layer (Redis)
**Location:** Docker container
**Port:** 6379

```
Cache Keys:
cache:v1:synthetic_tasks:n={n}:seed={seed}:sample={size}
cache:v1:mission_load:window={window}:bucket={bucket}:seed={seed}

TTL: 300s (5 minutes) for demo purposes
Eviction: LRU (Least Recently Used)
```

**Performance:**
- Cold cache (MISS): 2000-3000ms
- Warm cache (HIT): 10-20ms
- Speedup: 200x+

---

### 5. Observability Stack
**Location:** `backend/app/logging_config.py`, `backend/app/main.py`

```python
# Structured Logging
{
  "timestamp": "2025-01-24T22:03:32.679389+00:00",
  "level": "INFO",
  "logger": "jarvis",
  "message": "Request completed",
  "request_id": "req_abc123",
  "endpoint": "/api/v1/missions",
  "method": "GET",
  "status_code": 200,
  "duration_ms": 847
}

# Health Checks
GET /api/v1/health
→ { "status": "healthy", "dependencies": {
    "redis": "ok",
    "weather_api": "ok",
    "github_api": "degraded"
  }}

# Prometheus Metrics
cache_hits_total{endpoint="/missions"}
cache_misses_total{endpoint="/missions"}
http_requests_total{method="GET",path="/missions",status="200"}
http_request_duration_seconds{...}
```

---

## 🔄 Request Lifecycle

### Example: Generate Missions

```
1. User clicks "Generate Missions"
   └─► Frontend: POST /api/v1/missions

2. API Gateway (middleware)
   ├─► Generate request_id: req_abc123
   ├─► Log: "Request started"
   └─► Route to handler

3. Mission API Handler
   └─► Call MissionService.generate()

4. Mission Service
   ├─► Fetch context (ContextService)
   │   ├─► Weather API: GET /current?city=Istanbul
   │   ├─► GitHub API: GET /repos/:owner/:repo/issues
   │   ├─► Calendar API: GET /events?date=today
   │   └─► News API: GET /headlines
   │
   ├─► Generate task candidates
   │   └─► Filter 50+ templates by context
   │
   ├─► Score each task (ScoringService)
   │   ├─► deadline_factor() → +0.42
   │   ├─► context_relevance() → +0.31
   │   ├─► energy_match() → +0.18
   │   └─► user_preference() → +0.09
   │
   └─► Return top 12 ranked missions

5. API Gateway (response)
   ├─► Add X-Request-Id header
   ├─► Add X-Cache: MISS header
   ├─► Log: "Request completed (847ms)"
   └─► Return JSON response

6. Frontend renders missions
   ├─► Display mission cards
   ├─► Show context panel
   └─► Enable task detail modal
```

---

## 🎨 UI/UX Design Principles

### Visual Theme: **Cyber Mission Control**
- Dark background with neon accents
- Gradient cards (purple → pink → orange)
- Monospace fonts for data
- Badge-style status indicators

### Interaction Patterns
1. **Dashboard** - At-a-glance mission overview
2. **Modal Dialogs** - Deep dive into task details
3. **Diff Views** - Visual comparison of states
4. **Real-Time Feedback** - Cache badges, loading states

### Accessibility
- Color-blind safe palette
- Keyboard navigation support
- ARIA labels on interactive elements
- High contrast text

---

## 📈 Performance Characteristics

### Latency Targets
| Endpoint | Cold (MISS) | Warm (HIT) | Target |
|----------|-------------|------------|--------|
| `/missions` | 500-800ms | N/A | <1s |
| `/synthetic` | 2000-3000ms | 10-20ms | <100ms (cached) |
| `/reports/mission-load` | 1500-2000ms | 10-15ms | <100ms (cached) |
| `/health` | 50-100ms | N/A | <200ms |

### Caching Strategy
- **Cache heavy computations** (synthetic tasks, aggregations)
- **Don't cache dynamic data** (current missions, user state)
- **Versioned keys** (cache:v1:...) for safe schema changes
- **TTL = 300s** (5 minutes for demo, tune for production)

### Scalability Considerations
- **Horizontal scaling**: Stateless API servers
- **Vertical scaling**: Redis memory for cache
- **API rate limiting**: 100 req/min per user (future)
- **Async operations**: Concurrent health checks, context fetching

---

## 🔒 Security & Reliability

### Security Headers
```
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
Referrer-Policy: no-referrer
Permissions-Policy: geolocation=(), microphone=(), camera=()
```

### CORS Configuration
```python
allow_origins: ["http://localhost:5173"]  # Frontend dev server
allow_credentials: True
allow_methods: ["GET", "POST", "PUT", "DELETE"]
allow_headers: ["*"]
expose_headers: ["X-Request-Id", "X-Cache", "X-Compute-Time-ms"]
```

### Error Handling
```python
# Standard envelope format
{
  "envelope_version": "2024-12",
  "request_id": "req_abc123",
  "status": "error",
  "data": null,
  "error": {
    "code": "INVALID_PARAMS",
    "message": "Missing required field: seed"
  }
}
```

### Graceful Degradation
- Weather API down → Use cached/default weather
- GitHub API down → Use stale issue count
- Redis down → Skip caching, compute fresh
- System continues with degraded status

---

## 🧪 Testing Strategy

### Unit Tests
```python
# backend/tests/
test_scoring.py           → Score calculation logic
test_context_cache.py     → Redis caching behavior
test_mission_creation.py  → Task generation
test_health.py            → Health check endpoints
```

### Integration Tests
```python
test_exchange_ingestion.py  → Full API workflows
test_synthetic_cache.py     → Cache HIT/MISS cycles
test_trending_ingestion.py  → Context fetching
```

### Demo Validation
```bash
./infra/scripts/demo.sh
# Validates:
# - Health endpoint
# - Cache MISS → HIT cycle
# - Metrics endpoint
# - Compute time improvements
```

---

## 📚 Key Documentation

| Document | Purpose |
|----------|---------|
| [presentation_demo.md](presentation_demo.md) | 90-second demo script |
| [api_contract.md](api_contract.md) | REST API specification |
| [mission_rules.md](mission_rules.md) | Scoring algorithm details |
| [context_schema.md](context_schema.md) | External data integration |
| [db_schema.md](db_schema.md) | Future database design |

---

## 🚀 Deployment Architecture (Future)

```
┌─────────────────────────────────────────────────────┐
│                   Load Balancer                     │
│                 (Nginx / ALB)                       │
└─────────────────────────────────────────────────────┘
                      │
          ┌───────────┴───────────┐
          │                       │
    ┌─────▼─────┐           ┌────▼──────┐
    │ Frontend  │           │ Frontend  │
    │ Container │           │ Container │
    │ (Nginx)   │           │ (Nginx)   │
    └───────────┘           └───────────┘
          │                       │
          └───────────┬───────────┘
                      │
                      │ API Requests
                      │
          ┌───────────▼───────────┐
          │    API Gateway        │
          │   (FastAPI Cluster)   │
          └───────────┬───────────┘
                      │
          ┌───────────┴───────────┐
          │                       │
    ┌─────▼─────┐           ┌────▼──────┐
    │ Backend   │           │ Backend   │
    │ Instance  │           │ Instance  │
    └─────┬─────┘           └────┬──────┘
          │                      │
          └──────────┬───────────┘
                     │
          ┌──────────▼──────────┐
          │   Redis Cluster     │
          │ (ElastiCache / AWS) │
          └─────────────────────┘
```

---

## 📊 Metrics Dashboard (Grafana - Future)

**Key Metrics to Monitor:**
1. Request rate (req/s)
2. Response time (p50, p95, p99)
3. Cache hit ratio (%)
4. Error rate (%)
5. Dependency health (Redis, APIs)

**Alerts:**
- Response time p95 > 2s
- Cache hit ratio < 80%
- Error rate > 5%
- Redis connection failures

---

## 🎓 Learning Outcomes

This architecture demonstrates:

1. **Microservices Patterns**
   - Service separation (context, missions, scoring)
   - API gateway pattern
   - Caching layer

2. **Production Best Practices**
   - Structured logging
   - Health checks
   - Graceful degradation
   - Request tracing

3. **Modern Web Stack**
   - Async Python (FastAPI)
   - React hooks & TypeScript
   - Redis caching
   - Prometheus monitoring

4. **Explainable AI**
   - Transparent scoring
   - Evidence-based reasoning
   - User-facing explanations

---

**Last Updated:** January 2025
**Version:** 1.0
**Status:** Production-Ready Demo System
