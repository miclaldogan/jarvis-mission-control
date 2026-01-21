from __future__ import annotations

from fastapi import APIRouter, Request

from app.http_envelope import ok

router = APIRouter()


@router.get("/context")
async def get_context(request: Request):
    # Placeholder aggregated context. Ingestion will replace this later.
    return ok(
        request,
        {
            "context_id": "ctx_placeholder",
            "observed_at": "2026-01-21T09:00:00Z",
            "weather": {"city": "Istanbul", "temp_c": 7, "condition": "rain"},
            "news": [{"title": "Example headline", "url": "https://example.com"}],
            "github": {"open_issues": 12, "open_prs": 4},
            "calendar": {"events_today": 3},
        },
    )
