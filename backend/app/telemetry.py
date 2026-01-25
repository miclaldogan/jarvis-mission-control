"""API Telemetry - Real request tracking for Network Traffic panel.

Tracks:
- Requests per second (RPS)
- Latency distribution (p50, p95, p99)
- Error rate
- Top endpoints by traffic
- Rolling window (60 seconds)
"""

from __future__ import annotations

import time
import statistics
from collections import deque, defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional
from threading import Lock


@dataclass
class RequestRecord:
    """Single request record."""
    timestamp: float  # Unix timestamp
    endpoint: str
    method: str
    status_code: int
    latency_ms: float
    request_size: int  # bytes (approximate)
    response_size: int  # bytes (approximate)


class TelemetryStore:
    """Thread-safe telemetry storage with rolling window."""
    
    def __init__(self, window_seconds: int = 60, max_records: int = 10000):
        self.window_seconds = window_seconds
        self.max_records = max_records
        self._records: deque[RequestRecord] = deque(maxlen=max_records)
        self._lock = Lock()
        
        # Counters for quick aggregation
        self._total_requests = 0
        self._total_errors = 0
        self._endpoint_counts: dict[str, int] = defaultdict(int)
    
    def record(self, 
               endpoint: str, 
               method: str, 
               status_code: int, 
               latency_ms: float,
               request_size: int = 0,
               response_size: int = 0):
        """Record a request."""
        with self._lock:
            record = RequestRecord(
                timestamp=time.time(),
                endpoint=endpoint,
                method=method,
                status_code=status_code,
                latency_ms=latency_ms,
                request_size=request_size,
                response_size=response_size,
            )
            self._records.append(record)
            self._total_requests += 1
            self._endpoint_counts[f"{method} {endpoint}"] += 1
            
            if status_code >= 400:
                self._total_errors += 1
    
    def _get_window_records(self) -> list[RequestRecord]:
        """Get records within the rolling window."""
        cutoff = time.time() - self.window_seconds
        with self._lock:
            return [r for r in self._records if r.timestamp >= cutoff]
    
    def get_summary(self) -> dict[str, Any]:
        """Get telemetry summary for the rolling window."""
        records = self._get_window_records()
        
        if not records:
            return {
                "window_seconds": self.window_seconds,
                "total_requests": 0,
                "rps": 0.0,
                "error_rate": 0.0,
                "latency": {
                    "p50": 0.0,
                    "p95": 0.0,
                    "p99": 0.0,
                    "avg": 0.0,
                    "min": 0.0,
                    "max": 0.0,
                },
                "status_codes": {},
                "top_endpoints": [],
                "bytes_in": 0,
                "bytes_out": 0,
                "computed_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            }
        
        # Calculate time span
        time_span = max(records[-1].timestamp - records[0].timestamp, 1)
        if time_span < self.window_seconds:
            time_span = min(time.time() - records[0].timestamp, self.window_seconds)
        
        # RPS
        rps = len(records) / max(time_span, 1)
        
        # Error rate
        errors = sum(1 for r in records if r.status_code >= 400)
        error_rate = (errors / len(records)) * 100 if records else 0
        
        # Latency percentiles
        latencies = sorted([r.latency_ms for r in records])
        
        def percentile(data: list[float], p: float) -> float:
            if not data:
                return 0.0
            k = (len(data) - 1) * p / 100
            f = int(k)
            c = f + 1 if f < len(data) - 1 else f
            return data[f] + (k - f) * (data[c] - data[f])
        
        # Status code distribution
        status_codes: dict[str, int] = defaultdict(int)
        for r in records:
            bucket = f"{r.status_code // 100}xx"
            status_codes[bucket] += 1
        
        # Top endpoints
        endpoint_counts: dict[str, int] = defaultdict(int)
        endpoint_latencies: dict[str, list[float]] = defaultdict(list)
        for r in records:
            key = f"{r.method} {r.endpoint}"
            endpoint_counts[key] += 1
            endpoint_latencies[key].append(r.latency_ms)
        
        top_endpoints = sorted(
            [
                {
                    "endpoint": k,
                    "count": v,
                    "avg_latency_ms": round(statistics.mean(endpoint_latencies[k]), 2),
                }
                for k, v in endpoint_counts.items()
            ],
            key=lambda x: x["count"],
            reverse=True,
        )[:10]
        
        # Bytes
        bytes_in = sum(r.request_size for r in records)
        bytes_out = sum(r.response_size for r in records)
        
        return {
            "window_seconds": self.window_seconds,
            "total_requests": len(records),
            "rps": round(rps, 2),
            "error_rate": round(error_rate, 2),
            "latency": {
                "p50": round(percentile(latencies, 50), 2),
                "p95": round(percentile(latencies, 95), 2),
                "p99": round(percentile(latencies, 99), 2),
                "avg": round(statistics.mean(latencies) if latencies else 0, 2),
                "min": round(min(latencies) if latencies else 0, 2),
                "max": round(max(latencies) if latencies else 0, 2),
            },
            "status_codes": dict(status_codes),
            "top_endpoints": top_endpoints,
            "bytes_in": bytes_in,
            "bytes_out": bytes_out,
            "computed_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        }
    
    def get_time_series(self, bucket_seconds: int = 5) -> list[dict[str, Any]]:
        """Get time series data for charting (buckets of N seconds)."""
        records = self._get_window_records()
        
        if not records:
            return []
        
        # Group by time bucket
        buckets: dict[int, list[RequestRecord]] = defaultdict(list)
        now = time.time()
        
        for r in records:
            bucket_idx = int((now - r.timestamp) // bucket_seconds)
            buckets[bucket_idx].append(r)
        
        # Generate time series
        series = []
        for i in range(self.window_seconds // bucket_seconds):
            bucket_records = buckets.get(i, [])
            bucket_time = now - (i * bucket_seconds)
            
            if bucket_records:
                latencies = [r.latency_ms for r in bucket_records]
                errors = sum(1 for r in bucket_records if r.status_code >= 400)
                series.append({
                    "time": datetime.fromtimestamp(bucket_time, tz=timezone.utc).isoformat().replace("+00:00", "Z"),
                    "seconds_ago": i * bucket_seconds,
                    "requests": len(bucket_records),
                    "rps": len(bucket_records) / bucket_seconds,
                    "avg_latency_ms": round(statistics.mean(latencies), 2),
                    "p95_latency_ms": round(sorted(latencies)[int(len(latencies) * 0.95)] if len(latencies) > 1 else latencies[0], 2),
                    "errors": errors,
                    "error_rate": round((errors / len(bucket_records)) * 100, 2),
                })
            else:
                series.append({
                    "time": datetime.fromtimestamp(bucket_time, tz=timezone.utc).isoformat().replace("+00:00", "Z"),
                    "seconds_ago": i * bucket_seconds,
                    "requests": 0,
                    "rps": 0,
                    "avg_latency_ms": 0,
                    "p95_latency_ms": 0,
                    "errors": 0,
                    "error_rate": 0,
                })
        
        return list(reversed(series))  # Oldest first
    
    def get_lifetime_stats(self) -> dict[str, Any]:
        """Get all-time statistics."""
        with self._lock:
            return {
                "total_requests": self._total_requests,
                "total_errors": self._total_errors,
                "error_rate": round((self._total_errors / self._total_requests) * 100, 2) if self._total_requests > 0 else 0,
                "top_endpoints_alltime": sorted(
                    [{"endpoint": k, "count": v} for k, v in self._endpoint_counts.items()],
                    key=lambda x: x["count"],
                    reverse=True,
                )[:10],
            }


# Global telemetry store
_telemetry_store: Optional[TelemetryStore] = None


def get_telemetry_store() -> TelemetryStore:
    """Get or create the global telemetry store."""
    global _telemetry_store
    if _telemetry_store is None:
        _telemetry_store = TelemetryStore(window_seconds=60, max_records=10000)
    return _telemetry_store


def record_request(
    endpoint: str,
    method: str,
    status_code: int,
    latency_ms: float,
    request_size: int = 0,
    response_size: int = 0,
):
    """Convenience function to record a request."""
    get_telemetry_store().record(
        endpoint=endpoint,
        method=method,
        status_code=status_code,
        latency_ms=latency_ms,
        request_size=request_size,
        response_size=response_size,
    )
