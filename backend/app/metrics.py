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
