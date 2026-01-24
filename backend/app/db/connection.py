"""SQLite database connection management.

Provides async-compatible connection handling for SQLite persistence.
Uses aiosqlite for async operations in FastAPI context.
"""

from __future__ import annotations

import os
import sqlite3
import json
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Generator, Optional

from app.db.models import SQL_SCHEMA


# Default database path
DEFAULT_DB_PATH = os.getenv("DATABASE_PATH", "/tmp/jarvis_mission_control.db")

# In-memory option for testing
USE_MEMORY_DB = os.getenv("USE_MEMORY_DB", "false").lower() in ("true", "1", "yes")

# Global connection for in-memory mode
_memory_connection: Optional[sqlite3.Connection] = None


def _get_db_path() -> str:
    """Get database file path."""
    if USE_MEMORY_DB:
        return ":memory:"
    return DEFAULT_DB_PATH


def _json_serializer(obj: Any) -> str:
    """Serialize Python objects to JSON for SQLite storage."""
    return json.dumps(obj, default=str)


def _json_deserializer(data: str) -> Any:
    """Deserialize JSON string from SQLite storage."""
    try:
        return json.loads(data)
    except (json.JSONDecodeError, TypeError):
        return data


def init_db(db_path: Optional[str] = None) -> sqlite3.Connection:
    """Initialize database with schema.
    
    Args:
        db_path: Optional custom database path
        
    Returns:
        Database connection
    """
    global _memory_connection
    
    path = db_path or _get_db_path()
    
    if path == ":memory:" and _memory_connection is not None:
        return _memory_connection
    
    # Ensure directory exists for file-based DB
    if path != ":memory:":
        Path(path).parent.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    
    # Enable foreign keys and WAL mode for better concurrency
    conn.execute("PRAGMA foreign_keys = ON")
    if path != ":memory:":
        conn.execute("PRAGMA journal_mode = WAL")
    
    # Create tables
    conn.executescript(SQL_SCHEMA)
    conn.commit()
    
    if path == ":memory:":
        _memory_connection = conn
    
    return conn


def get_db(db_path: Optional[str] = None) -> sqlite3.Connection:
    """Get database connection.
    
    Creates connection if needed, reuses for in-memory mode.
    
    Args:
        db_path: Optional custom database path
        
    Returns:
        Database connection
    """
    global _memory_connection
    
    path = db_path or _get_db_path()
    
    if path == ":memory:":
        if _memory_connection is None:
            _memory_connection = init_db(path)
        return _memory_connection
    
    # For file-based DB, create new connection (thread-safe)
    conn = sqlite3.connect(path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


@contextmanager
def get_db_context(db_path: Optional[str] = None) -> Generator[sqlite3.Connection, None, None]:
    """Context manager for database connection.
    
    Args:
        db_path: Optional custom database path
        
    Yields:
        Database connection
    """
    conn = get_db(db_path)
    try:
        yield conn
    finally:
        if _get_db_path() != ":memory:":
            conn.close()


def close_db() -> None:
    """Close database connection(s)."""
    global _memory_connection
    
    if _memory_connection is not None:
        _memory_connection.close()
        _memory_connection = None


def reset_db(db_path: Optional[str] = None) -> sqlite3.Connection:
    """Reset database (drop all tables and recreate).
    
    Useful for testing.
    
    Args:
        db_path: Optional custom database path
        
    Returns:
        Fresh database connection
    """
    close_db()
    
    path = db_path or _get_db_path()
    
    # Delete file if exists
    if path != ":memory:" and Path(path).exists():
        Path(path).unlink()
    
    return init_db(path)


def execute_query(
    query: str,
    params: tuple = (),
    db_path: Optional[str] = None,
) -> list[dict[str, Any]]:
    """Execute a SELECT query and return results as list of dicts.
    
    Args:
        query: SQL query string
        params: Query parameters
        db_path: Optional custom database path
        
    Returns:
        List of row dictionaries
    """
    with get_db_context(db_path) as conn:
        cursor = conn.execute(query, params)
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        return [dict(zip(columns, row)) for row in rows]


def execute_write(
    query: str,
    params: tuple = (),
    db_path: Optional[str] = None,
) -> int:
    """Execute an INSERT/UPDATE/DELETE query.
    
    Args:
        query: SQL query string
        params: Query parameters
        db_path: Optional custom database path
        
    Returns:
        Number of affected rows
    """
    with get_db_context(db_path) as conn:
        cursor = conn.execute(query, params)
        conn.commit()
        return cursor.rowcount
