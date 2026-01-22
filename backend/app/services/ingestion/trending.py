from __future__ import annotations

import time
from typing import Any, Dict, List

import httpx

TMDB_TRENDING_URL = "https://api.themoviedb.org/3/trending/all/day"
DEFAULT_TIMEOUT_SECONDS = 5


async def fetch_trending(
    *,
    api_key: str,
    limit: int = 5,
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
) -> Dict[str, Any]:
    """
    Fetch trending items from TMDB.
    Contract:
    - NEVER raises (returns ok=False on failure)
    - Returns at least: ok: bool, elapsed_ms: int
    - Normalized items: [{title, url}]
    """
    start = time.perf_counter()
    try:
        timeout = httpx.Timeout(timeout_seconds)
        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.get(
                TMDB_TRENDING_URL,
                params={"api_key": api_key},
            )
            resp.raise_for_status()
            payload = resp.json()

        results = payload.get("results", [])[: max(0, limit)]
        items: List[Dict[str, str]] = []
        for r in results:
            title = r.get("title") or r.get("name") or r.get("original_title") or r.get("original_name") or "Unknown"
            media_type = r.get("media_type") or "all"
            tmdb_id = r.get("id")
            url = f"https://www.themoviedb.org/{media_type}/{tmdb_id}" if tmdb_id else "https://www.themoviedb.org/"
            items.append({"title": title, "url": url})

        elapsed_ms = int((time.perf_counter() - start) * 1000)
        return {"ok": True, "items": items, "elapsed_ms": elapsed_ms}
    except Exception as e:
        elapsed_ms = int((time.perf_counter() - start) * 1000)
        return {"ok": False, "error": str(e), "items": [], "elapsed_ms": elapsed_ms}
