from prometheus_client import Counter

CONTEXT_REQUESTS_TOTAL = Counter(
    "context_requests_total",
    "Total number of /api/v1/context requests",
)

CACHE_HIT_TOTAL = Counter(
    "cache_hit_total",
    "Total cache HIT count (context)",
)

CACHE_MISS_TOTAL = Counter(
    "cache_miss_total",
    "Total cache MISS count (context)",
)
