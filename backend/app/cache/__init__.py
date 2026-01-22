from __future__ import annotations

import json
import os
import time
from typing import Any, Optional, Dict, Tuple

# ----------------------------
# Simple cache interface
# - Works without Redis (in-memory fallback)
# - If Redis available, you can wire it later
# ----------------------------

_DEFAULT_TTL = int(os.getenv("CACHE_TTL_SECONDS", "120"))

# In-memory fallback cache: key -> (expires_at, value_str)
_MEM: Dict[str, Tuple[float, str]] = {}


def _now() -> float:
    return time.time()


def _get_ttl() -> int:
    try:
        return int(os.getenv("CACHE_TTL_SECONDS", str(_DEFAULT_TTL)))
    except Exception:
        return _DEFAULT_TTL


def cache_key_synthetic_tasks(n: int, seed: int) -> str:
    return f"synthetic:v1:n={n}:seed={seed}"


def cache_key_mission_load(size: int, seed: int) -> str:
    return f"mission_load:v1:size={size}:seed={seed}"


def get_json(key: str) -> Optional[Any]:
    item = _MEM.get(key)
    if not item:
        return None
    expires_at, raw = item
    if expires_at < _now():
        _MEM.pop(key, None)
        return None
    try:
        return json.loads(raw)
    except Exception:
        return None


def set_json(key: str, value: Any, ttl_seconds: Optional[int] = None) -> None:
    ttl = ttl_seconds if ttl_seconds is not None else _get_ttl()
    expires_at = _now() + ttl
    _MEM[key] = (expires_at, json.dumps(value, ensure_ascii=False))
