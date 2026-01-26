# JARVIS Mission Control - 90-Second Demo Script

## 🎯 Demo Goal
Show that JARVIS is **not just a to-do list** - it's an **adaptive task orchestration system** that generates, prioritizes, and adjusts missions based on real-time context.

## 🕐 Timeline (90 seconds)

### [0:00-0:15] System Overview & Live Context
**Script:**
> "This is JARVIS Mission Control - an adaptive task orchestration system that generates missions based on real-time context."

**Actions:**
1. Open Dashboard at `http://localhost:5173`
2. Point to Context Panel showing:
   - 🌤️ Weather: Clear skies, 22°C
   - 📊 GitHub: 5 open issues
   - 📅 Calendar: Team standup in 30 minutes
   - 📰 News: Tech conference announced

**Key Point:** "The system is constantly aware of what's happening around you."

---

### [0:15-0:30] Mission Generation
**Script:**
> "Watch how JARVIS generates missions dynamically based on current conditions."

**Actions:**
1. Click **"Generate Missions"** button
2. Show loading state
3. Highlight result: **"Run #15 created with 12 missions"**
4. Point to generated tasks:
   - "Morning jog in the park" (weather-aware)
   - "Review PR #127" (GitHub-aware)
   - "Prepare standup notes" (calendar-aware)

**Key Point:** "Tasks aren't static - they're generated for THIS moment."

---

### [0:30-0:45] Explainable Scoring
**Script:**
> "Every mission has an explainable priority score."

**Actions:**
1. Click on high-priority task: **"Review PR #127"**
2. Show **Task Detail Modal** with score breakdown:
   ```
   Deadline Factor:    +0.42  ━━━━━━━━━━━━━━━━━━━━ 84%
   Context Relevance:  +0.31  ━━━━━━━━━━━━━━ 62%
   Energy Match:       +0.18  ━━━━━━━━ 36%
   User Preference:    +0.09  ━━━━ 18%
   ──────────────────────────────────────────
   Total Score:         1.00  100/100
   ```
3. Show evidence:
   - "Deadline in 2 hours" → +0.42
   - "GitHub issue activity detected" → +0.31
   - "High energy time of day" → +0.18

**Key Point:** "Transparent AI - you know WHY this task matters now."

---

### [0:45-1:00] Context Adaptation (Simulation Lab)
**Script:**
> "The system adapts in real-time to context changes."

**Actions:**
1. Navigate to **Simulation Lab** page
2. Show **Before** state: 12 missions including outdoor tasks
3. Toggle scenario controls:
   - ☔ Enable "Heavy Rain"
   - 🐛 Set "20 GitHub Issues"
4. Click **"Generate Missions"**
5. Show **After** state:
   - ❌ "Morning jog" removed (weather conflict)
   - ✅ "Fix bug #134" added (GitHub spike)
   - ✅ "Review 3 PRs" promoted (dev urgency)
6. Highlight **Diff View**:
   - 🔴 Removed: 2 outdoor tasks
   - 🟢 Added: 4 dev tasks
   - ⚪ Kept: 6 indoor tasks

**Key Point:** "Missions evolve automatically as your world changes."

---

### [1:00-1:15] Production Performance (Cache)
**Script:**
> "This is production-ready, not just a prototype."

**Actions:**
1. Navigate to **Reports** page
2. Trigger mission load report (first call)
3. Show cache headers:
   ```
   X-Cache: MISS
   X-Compute-Time-ms: 2847ms
   ```
4. Trigger same report again (second call)
5. Show cache speedup:
   ```
   X-Cache: HIT
   X-Compute-Time-ms: 12ms
   ```
6. Point to badge: **"237x faster"**

**Key Point:** "Smart caching makes complex computations instant."

---

### [1:15-1:30] Mission Evolution (Run History)
**Script:**
> "Track how missions evolved throughout the day."

**Actions:**
1. Navigate to **Mission Run History** page
2. Show timeline of runs:
   - Run #13: 08:00 AM (morning context)
   - Run #14: 12:00 PM (midday context)
   - Run #15: 04:00 PM (afternoon context)
3. Click **Run #13** and **Run #15** for comparison
4. Show **Diff View**:
   ```
   🟢 Added in Run #15:
   - Review PR #127 (GitHub activity spike)
   - Prepare presentation (calendar reminder)
   
   🔴 Removed from Run #13:
   - Morning jog (time passed)
   - Review email (already completed)
   
   ⚪ Kept in both:
   - Team standup (still scheduled)
   - Deploy backend (still pending)
   ```

**Key Point:** "This is a controllable, explainable system - not a black box."

---

## 🎭 Demo Variations

### Quick Demo (60 seconds)
Skip Simulation Lab and Run History. Focus on:
1. Context awareness (15s)
2. Mission generation (15s)
3. Score breakdown (20s)
4. Cache performance (10s)

### Technical Deep-Dive (3 minutes)
Add:
- Show Prometheus metrics at `/metrics`
- Demonstrate structured logging (JSON format)
- Show health endpoint with dependency checks
- Display Redis cache keys with `redis-cli KEYS cache:*`

---

## 🎨 Visual Highlights

### Dashboard
- ✨ Cyber-themed gradient cards
- 📊 Real-time context badges
- 🎯 Priority color coding (red → yellow → green)

### Task Detail Modal
- 📈 Score breakdown with progress bars
- 🔍 Evidence list with confidence percentages
- 🎮 Status transition buttons (Start → Complete → Fail)

### Simulation Lab
- 🎛️ Scenario controls with toggles
- 🔄 Before/After comparison view
- 🎨 Color-coded diff (green/red/gray)

### Reports Page
- ⚡ Cache badges (MISS/HIT with speedup)
- 📊 Mission load charts
- 📈 Compute time comparison

---

## 🚀 Setup Checklist

Before demo:
- [ ] Run `docker-compose up -d` (backend + Redis)
- [ ] Start frontend with `npm run dev` in `client/`
- [ ] Verify health: `curl http://localhost:8000/api/v1/health`
- [ ] Clear browser cache for clean demo
- [ ] Preload one mission run to show Run #1

---

## 💡 Key Messages

### Why This Isn't Just a To-Do App

1. **Context-Aware Generation**
   - To-do apps: Static lists you create manually
   - JARVIS: Dynamic missions generated from real-world context

2. **Explainable AI**
   - To-do apps: You decide priority
   - JARVIS: AI calculates priority with transparent reasoning

3. **Adaptive System**
   - To-do apps: Manual updates when things change
   - JARVIS: Automatic adaptation to context shifts

4. **Production-Ready**
   - To-do apps: Simple CRUD operations
   - JARVIS: Caching, observability, graceful degradation

5. **Temporal Intelligence**
   - To-do apps: Snapshot of your list
   - JARVIS: Historical view of how missions evolved

---

## 🎯 Closing Statement

> "JARVIS Mission Control demonstrates that modern AI systems can be both **intelligent** and **transparent**. It doesn't just tell you what to do - it explains why, adapts to your world, and lets you see how decisions evolved over time. This is the future of human-AI collaboration."

---

## 📝 Q&A Preparation

**Q: How does it compare to existing task managers?**
A: Traditional apps are static lists. JARVIS is a dynamic orchestration system that generates tasks contextually.

**Q: What if the AI is wrong?**
A: Every score is explainable. You can see exactly why a task was prioritized and override it.

**Q: How does it scale?**
A: Redis caching provides 200x+ speedup. Structured logging and health checks ensure production readiness.

**Q: What's the tech stack?**
A: FastAPI backend, React frontend, Redis cache, Prometheus metrics, structured JSON logging.

**Q: Can it integrate with real APIs?**
A: Yes - we already integrate Weather API, GitHub API, and calendar data. It's designed to be extensible.
