# Database Schema Documentation

> **Status**: ✅ Implemented in `backend/app/db/`

## Overview

Jarvis Mission Control uses SQLite for persistent storage with the following tables:
- `missions` - Task/mission records with full CRUD support
- `context_snapshots` - Historical context data from all sources
- `user_preferences` - User settings and preferences

---

## missions

Stores all mission/task records with scoring and evidence data.

| Column | Type | Default | Description |
|--------|------|---------|-------------|
| `id` | TEXT | PK | Unique mission ID (e.g., `msn_abc123`) |
| `title` | TEXT | NOT NULL | Mission title/description |
| `priority` | TEXT | 'P3' | Priority level: P1, P2, P3, P4 |
| `status` | TEXT | 'open' | Status: open, in_progress, done, snoozed, cancelled |
| `tags` | TEXT | '[]' | JSON array of tags |
| `why` | TEXT | '' | Explanation of why this mission exists |
| `due_at` | TEXT | NULL | ISO 8601 deadline timestamp |
| `completed_at` | TEXT | NULL | ISO 8601 completion timestamp |
| `created_at` | TEXT | NOT NULL | ISO 8601 creation timestamp |
| `updated_at` | TEXT | NOT NULL | ISO 8601 last update timestamp |
| `evidence` | TEXT | '{}' | JSON object with sources and confidence |
| `actions` | TEXT | '[]' | JSON array of action items |
| `priority_score` | REAL | 0.0 | Calculated priority score |
| `score_breakdown` | TEXT | '{}' | JSON object with score components |
| `reasons` | TEXT | '[]' | JSON array of scoring reasons |

### Indexes
- `idx_missions_status` - Fast status filtering
- `idx_missions_priority` - Priority-based queries
- `idx_missions_due_at` - Deadline queries
- `idx_missions_created_at` - Chronological queries

---

## context_snapshots

Historical context data from all ingestion sources.

| Column | Type | Default | Description |
|--------|------|---------|-------------|
| `id` | TEXT | PK | Unique snapshot ID (e.g., `ctx_abc123`) |
| `run_id` | TEXT | NOT NULL | Ingestion run ID (e.g., `run_20260125_abc123`) |
| `source` | TEXT | NOT NULL | Source name: weather, github, news, calendar, etc. |
| `data` | TEXT | '{}' | JSON object with source-specific data |
| `ingested_at` | TEXT | NOT NULL | ISO 8601 ingestion timestamp |
| `ttl_seconds` | INTEGER | 120 | Time-to-live in seconds |
| `is_synthetic` | INTEGER | 0 | 1 if synthetic/test data, 0 otherwise |

### Indexes
- `idx_context_run_id` - Group snapshots by run
- `idx_context_source` - Filter by source
- `idx_context_ingested_at` - Time-based queries

---

## user_preferences

User settings and preferences.

| Column | Type | Default | Description |
|--------|------|---------|-------------|
| `id` | TEXT | PK | User ID (default: 'default') |
| `energy_level` | TEXT | 'medium' | Energy level: low, medium, high |
| `focus_tags` | TEXT | '[]' | JSON array of prioritized tags |
| `blocked_tags` | TEXT | '[]' | JSON array of deprioritized tags |
| `work_hours_start` | INTEGER | 9 | Work start hour (24h format) |
| `work_hours_end` | INTEGER | 18 | Work end hour (24h format) |
| `timezone` | TEXT | 'UTC' | User timezone |
| `notification_enabled` | INTEGER | 1 | Enable notifications |
| `theme` | TEXT | 'dark' | UI theme: dark, light |
| `created_at` | TEXT | NOT NULL | ISO 8601 creation timestamp |
| `updated_at` | TEXT | NOT NULL | ISO 8601 last update timestamp |

---

## SQL DDL Reference

```sql
-- Missions table
CREATE TABLE IF NOT EXISTS missions (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    priority TEXT DEFAULT 'P3',
    status TEXT DEFAULT 'open',
    tags TEXT DEFAULT '[]',
    why TEXT DEFAULT '',
    due_at TEXT,
    completed_at TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    evidence TEXT DEFAULT '{}',
    actions TEXT DEFAULT '[]',
    priority_score REAL DEFAULT 0.0,
    score_breakdown TEXT DEFAULT '{}',
    reasons TEXT DEFAULT '[]'
);

-- Context snapshots table
CREATE TABLE IF NOT EXISTS context_snapshots (
    id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL,
    source TEXT NOT NULL,
    data TEXT DEFAULT '{}',
    ingested_at TEXT NOT NULL,
    ttl_seconds INTEGER DEFAULT 120,
    is_synthetic INTEGER DEFAULT 0
);

-- User preferences table
CREATE TABLE IF NOT EXISTS user_preferences (
    id TEXT PRIMARY KEY DEFAULT 'default',
    energy_level TEXT DEFAULT 'medium',
    focus_tags TEXT DEFAULT '[]',
    blocked_tags TEXT DEFAULT '[]',
    work_hours_start INTEGER DEFAULT 9,
    work_hours_end INTEGER DEFAULT 18,
    timezone TEXT DEFAULT 'UTC',
    notification_enabled INTEGER DEFAULT 1,
    theme TEXT DEFAULT 'dark',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_missions_status ON missions(status);
CREATE INDEX IF NOT EXISTS idx_missions_priority ON missions(priority);
CREATE INDEX IF NOT EXISTS idx_missions_due_at ON missions(due_at);
CREATE INDEX IF NOT EXISTS idx_missions_created_at ON missions(created_at);
CREATE INDEX IF NOT EXISTS idx_context_run_id ON context_snapshots(run_id);
CREATE INDEX IF NOT EXISTS idx_context_source ON context_snapshots(source);
CREATE INDEX IF NOT EXISTS idx_context_ingested_at ON context_snapshots(ingested_at);
```

---

## Usage Examples

### Python Repository Pattern

```python
from app.db import MissionRepository, ContextRepository

# Create mission
mission = Mission(title="Review PR #123", priority="P2")
MissionRepository.create(mission)

# Get today's missions
today_missions = MissionRepository.get_today()

# Complete a mission
MissionRepository.complete("msn_abc123")

# Get completion stats
stats = MissionRepository.get_completion_stats()
# {"total": 50, "done": 35, "completion_rate": 70.0}
```

### REST API

```bash
# Ingest custom context
curl -X POST /api/v1/context/ingest \
  -H "Content-Type: application/json" \
  -d '{"source": "calendar", "data": {"events": [...]}}'

# Get today's missions
curl /api/v1/missions/today

# Complete a mission
curl -X POST /api/v1/missions/complete/msn_abc123

# Get history with stats
curl "/api/v1/missions/history?status=done&limit=100"
```

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_PATH` | `/tmp/jarvis_mission_control.db` | SQLite database file path |
| `USE_MEMORY_DB` | `false` | Use in-memory database (for testing) |
