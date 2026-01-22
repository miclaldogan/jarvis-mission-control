from __future__ import annotations

import os
import re

from fastapi.testclient import TestClient

from app.main import create_app


def _get_counter_value(metrics_text: str, name: str) -> float:
    # Matches lines like:
    # cache_hits_total 3
    pattern = re.compile(rf"^{re.escape(name)}\s+([0-9]+(?:\.[0-9]+)?)$", re.MULTILINE)
    match = pattern.search(metrics_text)
    if not match:
        raise AssertionError(f"Counter '{name}' not found in /metrics output")
    return float(match.group(1))


def test_metrics_endpoint_exposes_expected_metric_names():
    os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")
    app = create_app()

    with TestClient(app) as client:
        res = client.get("/metrics")
        assert res.status_code == 200
        assert res.headers["content-type"].startswith("text/plain")

        body = res.text
        assert "http_requests_total" in body
        assert "http_request_duration_seconds" in body
        assert "cache_hits_total" in body
        assert "cache_misses_total" in body
        assert "synthetic_tasks_generated_total" in body


def test_cache_hit_miss_counters_increase_with_synthetic_calls():
    os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")
    app = create_app()

    with TestClient(app) as client:
        before = client.get("/metrics").text
        hits_before = _get_counter_value(before, "cache_hits_total")
        misses_before = _get_counter_value(before, "cache_misses_total")

        # First call should MISS, second should HIT (seed enables caching)
        r1 = client.get("/api/v1/synthetic/tasks?n=100000&seed=42")
        assert r1.status_code == 200
        r2 = client.get("/api/v1/synthetic/tasks?n=100000&seed=42")
        assert r2.status_code == 200

        after = client.get("/metrics").text
        hits_after = _get_counter_value(after, "cache_hits_total")
        misses_after = _get_counter_value(after, "cache_misses_total")

        assert misses_after >= misses_before + 1
        assert hits_after >= hits_before + 1
