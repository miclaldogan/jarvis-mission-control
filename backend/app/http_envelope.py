from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional

from fastapi import Request


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def ok(request: Request, data: Any, *, extra_meta: Optional[dict[str, Any]] = None) -> dict[str, Any]:
    meta: dict[str, Any] = {
        "request_id": getattr(request.state, "request_id", None),
        "ts": _now_iso(),
    }
    if extra_meta:
        meta.update(extra_meta)
    return {"ok": True, "data": data, "meta": meta}


def err(
    request: Request,
    *,
    code: str,
    message: str,
    status_code: int,
    details: Optional[dict[str, Any]] = None,
) -> tuple[dict[str, Any], int]:
    payload: dict[str, Any] = {
        "ok": False,
        "data": None,
        "meta": {
            "request_id": getattr(request.state, "request_id", None),
            "ts": _now_iso(),
        },
        "error": {"code": code, "message": message, "details": details or {}},
    }
    return payload, status_code
