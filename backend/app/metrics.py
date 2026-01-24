from __future__ import annotations

from prometheus_client import Counter, Histogram

http_requests_total = Counter(
    "http_requests_total",
    "Total number of HTTP requests.",
    ["method", "path", "status"],
)

http_request_duration_seconds = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds.",
    ["method", "path"],
)

cache_hits_total = Counter(
    "cache_hits_total",
    "Total cache hits.",
)

cache_misses_total = Counter(
    "cache_misses_total",
    "Total cache misses.",
)

synthetic_tasks_generated_total = Counter(
    "synthetic_tasks_generated_total",
    "Total synthetic tasks requested/generated (by n parameter).",
)

# Track compute times for averaging
_compute_times: list[float] = []
_max_compute_times = 1000  # Rolling window


def observe_request(*, method: str, path: str, status: int, duration_seconds: float) -> None:
    http_requests_total.labels(method=method, path=path, status=str(status)).inc()
    http_request_duration_seconds.labels(method=method, path=path).observe(duration_seconds)


def inc_cache_hit() -> None:
    cache_hits_total.inc()


def inc_cache_miss() -> None:
    cache_misses_total.inc()


def inc_synthetic_generated(n: int) -> None:
    if n > 0:
        synthetic_tasks_generated_total.inc(n)


def record_compute_time(ms: float) -> None:
    """Record compute time for averaging."""
    global _compute_times
    _compute_times.append(ms)
    if len(_compute_times) > _max_compute_times:
        _compute_times = _compute_times[-_max_compute_times:]


def get_cache_stats() -> dict:
    """Get cache statistics for API endpoint."""
    hits = cache_hits_total._value.get()
    misses = cache_misses_total._value.get()
    total = hits + misses
    hit_rate = (hits / total * 100) if total > 0 else 0.0
    avg_compute = sum(_compute_times) / len(_compute_times) if _compute_times else 0.0
    
    return {
        "hits": int(hits),
        "misses": int(misses),
        "total_requests": int(total),
        "hit_rate_percent": round(hit_rate, 2),
        "avg_compute_time_ms": round(avg_compute, 2),
        "recent_compute_times": len(_compute_times),
    }
