from __future__ import annotations

import time
from typing import Any, Dict, List, Optional

import feedparser


def fetch_news_rss(feed_url: str, limit: int = 5) -> Dict[str, Any]:
    """
    1-source news ingestion via RSS (no API key).
    Returns a normalized dict to embed under /api/v1/context as "news".
    """
    started = time.time()
    parsed = feedparser.parse(feed_url, request_headers={"User-Agent": "jarvis-mission-control/0.1"})
    items: List[Dict[str, Any]] = []

    for e in (parsed.entries or [])[: max(0, limit)]:
        items.append(
            {
                "title": getattr(e, "title", "")[:300],
                "link": getattr(e, "link", ""),
                "published": getattr(e, "published", None),
            }
        )

    return {
        "source": "rss",
        "feed_url": feed_url,
        "items": items,
        "raw": {
            "bozo": getattr(parsed, "bozo", None),
            "elapsed_ms": int((time.time() - started) * 1000),
        },
    }
