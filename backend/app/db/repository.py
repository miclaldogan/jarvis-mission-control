"""Repository pattern for database operations.

Provides high-level CRUD operations for all entities.
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, List, Optional

from app.db.connection import get_db_context, execute_query, execute_write
from app.db.models import Mission, ContextSnapshot, UserPreference


def _generate_id(prefix: str = "") -> str:
    """Generate unique ID with optional prefix."""
    short_uuid = uuid.uuid4().hex[:12]
    return f"{prefix}{short_uuid}" if prefix else short_uuid


def _utc_now_iso() -> str:
    """Get current UTC timestamp in ISO format."""
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _today_start_iso() -> str:
    """Get start of today in ISO format."""
    now = datetime.now(timezone.utc)
    start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    return start.isoformat().replace("+00:00", "Z")


def _today_end_iso() -> str:
    """Get end of today in ISO format."""
    now = datetime.now(timezone.utc)
    end = now.replace(hour=23, minute=59, second=59, microsecond=999999)
    return end.isoformat().replace("+00:00", "Z")


class MissionRepository:
    """Repository for Mission CRUD operations."""
    
    @staticmethod
    def create(mission: Mission, db_path: Optional[str] = None) -> Mission:
        """Create a new mission."""
        if not mission.id:
            mission.id = _generate_id("msn_")
        
        with get_db_context(db_path) as conn:
            conn.execute(
                """
                INSERT INTO missions (
                    id, title, priority, status, tags, why, due_at,
                    completed_at, created_at, updated_at, evidence,
                    actions, priority_score, score_breakdown, reasons
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    mission.id,
                    mission.title,
                    mission.priority,
                    mission.status,
                    json.dumps(mission.tags),
                    mission.why,
                    mission.due_at,
                    mission.completed_at,
                    mission.created_at,
                    mission.updated_at,
                    json.dumps(mission.evidence),
                    json.dumps(mission.actions),
                    mission.priority_score,
                    json.dumps(mission.score_breakdown),
                    json.dumps(mission.reasons),
                ),
            )
            conn.commit()
        
        return mission
    
    @staticmethod
    def get_by_id(mission_id: str, db_path: Optional[str] = None) -> Optional[Mission]:
        """Get mission by ID."""
        rows = execute_query(
            "SELECT * FROM missions WHERE id = ?",
            (mission_id,),
            db_path,
        )
        if not rows:
            return None
        return MissionRepository._row_to_mission(rows[0])
    
    @staticmethod
    def get_all(
        status: Optional[str] = None,
        priority: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
        db_path: Optional[str] = None,
    ) -> List[Mission]:
        """Get all missions with optional filters."""
        query = "SELECT * FROM missions WHERE 1=1"
        params: list = []
        
        if status:
            query += " AND status = ?"
            params.append(status)
        if priority:
            query += " AND priority = ?"
            params.append(priority)
        
        query += " ORDER BY priority_score DESC, created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        rows = execute_query(query, tuple(params), db_path)
        return [MissionRepository._row_to_mission(row) for row in rows]
    
    @staticmethod
    def get_today(db_path: Optional[str] = None) -> List[Mission]:
        """Get missions for today (created or due today)."""
        today_start = _today_start_iso()
        today_end = _today_end_iso()
        
        rows = execute_query(
            """
            SELECT * FROM missions 
            WHERE (created_at >= ? AND created_at <= ?)
               OR (due_at >= ? AND due_at <= ?)
               OR (status = 'open' AND (due_at IS NULL OR due_at >= ?))
            ORDER BY priority_score DESC, due_at ASC
            """,
            (today_start, today_end, today_start, today_end, today_start),
            db_path,
        )
        return [MissionRepository._row_to_mission(row) for row in rows]
    
    @staticmethod
    def update(mission: Mission, db_path: Optional[str] = None) -> Mission:
        """Update an existing mission."""
        mission.updated_at = _utc_now_iso()
        
        execute_write(
            """
            UPDATE missions SET
                title = ?, priority = ?, status = ?, tags = ?, why = ?,
                due_at = ?, completed_at = ?, updated_at = ?, evidence = ?,
                actions = ?, priority_score = ?, score_breakdown = ?, reasons = ?
            WHERE id = ?
            """,
            (
                mission.title,
                mission.priority,
                mission.status,
                json.dumps(mission.tags),
                mission.why,
                mission.due_at,
                mission.completed_at,
                mission.updated_at,
                json.dumps(mission.evidence),
                json.dumps(mission.actions),
                mission.priority_score,
                json.dumps(mission.score_breakdown),
                json.dumps(mission.reasons),
                mission.id,
            ),
            db_path,
        )
        return mission
    
    @staticmethod
    def complete(mission_id: str, db_path: Optional[str] = None) -> Optional[Mission]:
        """Mark mission as completed."""
        mission = MissionRepository.get_by_id(mission_id, db_path)
        if not mission:
            return None
        
        mission.mark_complete()
        return MissionRepository.update(mission, db_path)
    
    @staticmethod
    def delete(mission_id: str, db_path: Optional[str] = None) -> bool:
        """Delete a mission."""
        affected = execute_write(
            "DELETE FROM missions WHERE id = ?",
            (mission_id,),
            db_path,
        )
        return affected > 0
    
    @staticmethod
    def get_history(
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        status: str = "done",
        limit: int = 100,
        db_path: Optional[str] = None,
    ) -> List[Mission]:
        """Get historical missions (completed by default)."""
        query = "SELECT * FROM missions WHERE status = ?"
        params: list = [status]
        
        if start_date:
            query += " AND completed_at >= ?"
            params.append(start_date)
        if end_date:
            query += " AND completed_at <= ?"
            params.append(end_date)
        
        query += " ORDER BY completed_at DESC LIMIT ?"
        params.append(limit)
        
        rows = execute_query(query, tuple(params), db_path)
        return [MissionRepository._row_to_mission(row) for row in rows]
    
    @staticmethod
    def get_completion_stats(
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        db_path: Optional[str] = None,
    ) -> dict:
        """Get mission completion statistics."""
        base_query = "SELECT COUNT(*) as count, status FROM missions"
        params: list = []
        
        if start_date or end_date:
            base_query += " WHERE 1=1"
            if start_date:
                base_query += " AND created_at >= ?"
                params.append(start_date)
            if end_date:
                base_query += " AND created_at <= ?"
                params.append(end_date)
        
        base_query += " GROUP BY status"
        
        rows = execute_query(base_query, tuple(params), db_path)
        
        stats = {
            "total": 0,
            "open": 0,
            "in_progress": 0,
            "done": 0,
            "snoozed": 0,
            "cancelled": 0,
            "completion_rate": 0.0,
        }
        
        for row in rows:
            status = row["status"]
            count = row["count"]
            stats[status] = count
            stats["total"] += count
        
        if stats["total"] > 0:
            stats["completion_rate"] = round(
                (stats["done"] / stats["total"]) * 100, 2
            )
        
        return stats
    
    @staticmethod
    def _row_to_mission(row: dict) -> Mission:
        """Convert database row to Mission object."""
        return Mission(
            id=row["id"],
            title=row["title"],
            priority=row["priority"],
            status=row["status"],
            tags=json.loads(row["tags"]) if row["tags"] else [],
            why=row["why"] or "",
            due_at=row["due_at"],
            completed_at=row["completed_at"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            evidence=json.loads(row["evidence"]) if row["evidence"] else {},
            actions=json.loads(row["actions"]) if row["actions"] else [],
            priority_score=row["priority_score"] or 0.0,
            score_breakdown=json.loads(row["score_breakdown"]) if row["score_breakdown"] else {},
            reasons=json.loads(row["reasons"]) if row["reasons"] else [],
        )


class ContextRepository:
    """Repository for ContextSnapshot operations."""
    
    @staticmethod
    def create(snapshot: ContextSnapshot, db_path: Optional[str] = None) -> ContextSnapshot:
        """Create a new context snapshot."""
        if not snapshot.id:
            snapshot.id = _generate_id("ctx_")
        
        with get_db_context(db_path) as conn:
            conn.execute(
                """
                INSERT INTO context_snapshots (
                    id, run_id, source, data, ingested_at, ttl_seconds, is_synthetic
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    snapshot.id,
                    snapshot.run_id,
                    snapshot.source,
                    json.dumps(snapshot.data),
                    snapshot.ingested_at,
                    snapshot.ttl_seconds,
                    1 if snapshot.is_synthetic else 0,
                ),
            )
            conn.commit()
        
        return snapshot
    
    @staticmethod
    def get_by_run_id(run_id: str, db_path: Optional[str] = None) -> List[ContextSnapshot]:
        """Get all snapshots for a run."""
        rows = execute_query(
            "SELECT * FROM context_snapshots WHERE run_id = ? ORDER BY ingested_at DESC",
            (run_id,),
            db_path,
        )
        return [ContextRepository._row_to_snapshot(row) for row in rows]
    
    @staticmethod
    def get_latest_by_source(source: str, db_path: Optional[str] = None) -> Optional[ContextSnapshot]:
        """Get latest snapshot for a source."""
        rows = execute_query(
            "SELECT * FROM context_snapshots WHERE source = ? ORDER BY ingested_at DESC LIMIT 1",
            (source,),
            db_path,
        )
        if not rows:
            return None
        return ContextRepository._row_to_snapshot(rows[0])
    
    @staticmethod
    def get_history(
        source: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: int = 100,
        db_path: Optional[str] = None,
    ) -> List[ContextSnapshot]:
        """Get context history with optional filters."""
        query = "SELECT * FROM context_snapshots WHERE 1=1"
        params: list = []
        
        if source:
            query += " AND source = ?"
            params.append(source)
        if start_date:
            query += " AND ingested_at >= ?"
            params.append(start_date)
        if end_date:
            query += " AND ingested_at <= ?"
            params.append(end_date)
        
        query += " ORDER BY ingested_at DESC LIMIT ?"
        params.append(limit)
        
        rows = execute_query(query, tuple(params), db_path)
        return [ContextRepository._row_to_snapshot(row) for row in rows]
    
    @staticmethod
    def delete_expired(db_path: Optional[str] = None) -> int:
        """Delete expired snapshots based on TTL."""
        # Calculate cutoff for each TTL value
        return execute_write(
            """
            DELETE FROM context_snapshots 
            WHERE datetime(ingested_at) < datetime('now', '-' || ttl_seconds || ' seconds')
            """,
            (),
            db_path,
        )
    
    @staticmethod
    def _row_to_snapshot(row: dict) -> ContextSnapshot:
        """Convert database row to ContextSnapshot object."""
        return ContextSnapshot(
            id=row["id"],
            run_id=row["run_id"],
            source=row["source"],
            data=json.loads(row["data"]) if row["data"] else {},
            ingested_at=row["ingested_at"],
            ttl_seconds=row["ttl_seconds"],
            is_synthetic=bool(row["is_synthetic"]),
        )


class PreferenceRepository:
    """Repository for UserPreference operations."""
    
    @staticmethod
    def get(user_id: str = "default", db_path: Optional[str] = None) -> UserPreference:
        """Get user preferences, create default if not exists."""
        rows = execute_query(
            "SELECT * FROM user_preferences WHERE id = ?",
            (user_id,),
            db_path,
        )
        
        if rows:
            return PreferenceRepository._row_to_preference(rows[0])
        
        # Create default preferences
        pref = UserPreference(id=user_id)
        return PreferenceRepository.save(pref, db_path)
    
    @staticmethod
    def save(pref: UserPreference, db_path: Optional[str] = None) -> UserPreference:
        """Save or update user preferences."""
        pref.updated_at = _utc_now_iso()
        
        with get_db_context(db_path) as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO user_preferences (
                    id, energy_level, focus_tags, blocked_tags,
                    work_hours_start, work_hours_end, timezone,
                    notification_enabled, theme, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    pref.id,
                    pref.energy_level,
                    json.dumps(pref.focus_tags),
                    json.dumps(pref.blocked_tags),
                    pref.work_hours_start,
                    pref.work_hours_end,
                    pref.timezone,
                    1 if pref.notification_enabled else 0,
                    pref.theme,
                    pref.created_at,
                    pref.updated_at,
                ),
            )
            conn.commit()
        
        return pref
    
    @staticmethod
    def _row_to_preference(row: dict) -> UserPreference:
        """Convert database row to UserPreference object."""
        return UserPreference(
            id=row["id"],
            energy_level=row["energy_level"],
            focus_tags=json.loads(row["focus_tags"]) if row["focus_tags"] else [],
            blocked_tags=json.loads(row["blocked_tags"]) if row["blocked_tags"] else [],
            work_hours_start=row["work_hours_start"],
            work_hours_end=row["work_hours_end"],
            timezone=row["timezone"],
            notification_enabled=bool(row["notification_enabled"]),
            theme=row["theme"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )
