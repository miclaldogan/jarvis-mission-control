import logging
import httpx
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

# Hacker News search API (Algolia) - no API key required
HN_SEARCH_URL = "https://hn.algolia.com/api/v1/search"
HN_SEARCH_BY_DATE_URL = "https://hn.algolia.com/api/v1/search_by_date"


async def fetch_news(limit: int = 5, *, mode: str = "front_page") -> List[Dict[str, str]]:
    """
    Fetch news items from a single external source and map to normalized schema.

    Normalized output:
      [{"title": "<str>", "url": "<str>"}]

    Behavior:
    - On error, raise Exception (caller will handle partial failure)
    """
    hits_per_page = max(1, min(int(limit), 20))

    if mode == "latest":
        # More dynamic feed: newest stories (changes frequently)
        url = HN_SEARCH_BY_DATE_URL
        params = {
            "tags": "story",
            "hitsPerPage": hits_per_page,
        }
    else:
        # Stable feed: front page
        url = HN_SEARCH_URL
        params = {
            "tags": "front_page",
            "hitsPerPage": hits_per_page,
        }

    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(url, params=params)

    if resp.status_code != 200:
        raise Exception(f"HN API returned {resp.status_code}: {resp.text}")

    data: Dict[str, Any] = resp.json()
    hits = data.get("hits", [])
    if not isinstance(hits, list):
        raise Exception("HN API response missing 'hits' list")

    items: List[Dict[str, str]] = []

    for h in hits:
        # title can be in different fields depending on record
        title = (h.get("title") or h.get("story_title") or "").strip()

        # Prefer the external URL; fallback to HN item URL if missing
        url = (h.get("url") or "").strip()
        if not url:
            object_id = h.get("objectID")
            if object_id:
                url = f"https://news.ycombinator.com/item?id={object_id}"

        # Skip empty rows
        if not title or not url:
            continue

        items.append({"title": title, "url": url})

    return items
