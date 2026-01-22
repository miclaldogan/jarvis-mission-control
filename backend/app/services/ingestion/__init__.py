"""
Ingestion adapters for external context sources.

Each adapter must:
- NOT raise exceptions
- Return a dict with at least:
    - ok: bool
    - elapsed_ms: int
- Be non-blocking for /api/v1/context
"""

from .weather import fetch_weather
from .news import fetch_news
from .github import fetch_github
from .exchange import fetch_exchange_rates
from .trending import fetch_trending

__all__ = [
    "fetch_trending",
    "fetch_weather",
    "fetch_news",
    "fetch_github",
    "fetch_exchange_rates",
]
