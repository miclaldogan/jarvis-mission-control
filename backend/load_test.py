#!/usr/bin/env python3
"""
Jarvis Mission Control - Load Test Script
==========================================

Usage:
    python load_test.py                    # Default: 100 concurrent, 30s
    python load_test.py --users 1000       # 1000 concurrent users
    python load_test.py --duration 60      # 60 seconds test
    python load_test.py --target http://localhost:8000

Requirements:
    pip install aiohttp asyncio

Endpoints tested:
    - GET  /api/v1/health
    - GET  /api/v1/context
    - GET  /api/v1/system/vitals
    - GET  /api/v1/system/harmonics
    - GET  /api/v1/metrics/traffic
    - POST /api/v1/missions/generate
"""

import argparse
import asyncio
import random
import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Optional

try:
    import aiohttp
except ImportError:
    print("Installing aiohttp...")
    import subprocess
    subprocess.check_call(["pip", "install", "aiohttp"])
    import aiohttp


@dataclass
class RequestResult:
    endpoint: str
    method: str
    status: int
    latency_ms: float
    success: bool
    error: Optional[str] = None


@dataclass
class LoadTestStats:
    total_requests: int = 0
    success_count: int = 0
    error_count: int = 0
    latencies: list = field(default_factory=list)
    status_codes: dict = field(default_factory=lambda: defaultdict(int))
    errors: list = field(default_factory=list)
    endpoint_stats: dict = field(default_factory=lambda: defaultdict(list))
    start_time: float = 0
    end_time: float = 0
    
    def record(self, result: RequestResult):
        self.total_requests += 1
        self.status_codes[result.status] += 1
        self.latencies.append(result.latency_ms)
        self.endpoint_stats[result.endpoint].append(result.latency_ms)
        
        if result.success:
            self.success_count += 1
        else:
            self.error_count += 1
            if result.error:
                self.errors.append(result.error)
    
    def percentile(self, p: float) -> float:
        if not self.latencies:
            return 0
        sorted_lat = sorted(self.latencies)
        idx = int(len(sorted_lat) * p / 100)
        return sorted_lat[min(idx, len(sorted_lat) - 1)]
    
    def summary(self) -> dict:
        duration = max(self.end_time - self.start_time, 0.001)
        return {
            "duration_seconds": round(duration, 2),
            "total_requests": self.total_requests,
            "success_count": self.success_count,
            "error_count": self.error_count,
            "error_rate_percent": round(self.error_count / max(self.total_requests, 1) * 100, 2),
            "rps": round(self.total_requests / duration, 2),
            "latency": {
                "avg_ms": round(sum(self.latencies) / max(len(self.latencies), 1), 2),
                "min_ms": round(min(self.latencies) if self.latencies else 0, 2),
                "max_ms": round(max(self.latencies) if self.latencies else 0, 2),
                "p50_ms": round(self.percentile(50), 2),
                "p95_ms": round(self.percentile(95), 2),
                "p99_ms": round(self.percentile(99), 2),
            },
            "status_codes": dict(self.status_codes),
            "endpoint_rps": {
                ep: round(len(lats) / duration, 2) 
                for ep, lats in self.endpoint_stats.items()
            },
        }


# Test scenarios with weights
SCENARIOS = [
    # endpoint, method, weight, body
    ("/api/v1/health", "GET", 10, None),
    ("/api/v1/context", "GET", 20, None),
    ("/api/v1/system/vitals", "GET", 25, None),
    ("/api/v1/system/harmonics", "GET", 15, None),
    ("/api/v1/metrics/traffic", "GET", 10, None),
    ("/api/v1/missions/generate", "POST", 20, {"limit": 10}),
]


def weighted_choice():
    """Pick a scenario based on weights."""
    total = sum(s[2] for s in SCENARIOS)
    r = random.random() * total
    cumulative = 0
    for scenario in SCENARIOS:
        cumulative += scenario[2]
        if r <= cumulative:
            return scenario
    return SCENARIOS[-1]


async def make_request(
    session: aiohttp.ClientSession,
    base_url: str,
    stats: LoadTestStats,
) -> RequestResult:
    """Make a single request."""
    endpoint, method, _, body = weighted_choice()
    url = f"{base_url.rstrip('/')}{endpoint}"
    
    start = time.perf_counter()
    try:
        if method == "GET":
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as resp:
                await resp.read()
                status = resp.status
        else:
            async with session.post(
                url, 
                json=body,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as resp:
                await resp.read()
                status = resp.status
        
        latency_ms = (time.perf_counter() - start) * 1000
        success = 200 <= status < 400
        
        result = RequestResult(
            endpoint=f"{method} {endpoint}",
            method=method,
            status=status,
            latency_ms=latency_ms,
            success=success,
        )
    except Exception as e:
        latency_ms = (time.perf_counter() - start) * 1000
        result = RequestResult(
            endpoint=f"{method} {endpoint}",
            method=method,
            status=0,
            latency_ms=latency_ms,
            success=False,
            error=str(e)[:100],
        )
    
    stats.record(result)
    return result


async def user_session(
    session: aiohttp.ClientSession,
    base_url: str,
    stats: LoadTestStats,
    duration: float,
    user_id: int,
):
    """Simulate a single user making requests."""
    end_time = time.time() + duration
    
    while time.time() < end_time:
        await make_request(session, base_url, stats)
        # Small random delay between requests (50-200ms)
        await asyncio.sleep(random.uniform(0.05, 0.2))


async def run_load_test(
    base_url: str,
    concurrent_users: int,
    duration_seconds: float,
) -> LoadTestStats:
    """Run the load test."""
    stats = LoadTestStats()
    stats.start_time = time.time()
    
    print(f"\n{'='*60}")
    print(f"🚀 JARVIS MISSION CONTROL - LOAD TEST")
    print(f"{'='*60}")
    print(f"  Target:      {base_url}")
    print(f"  Users:       {concurrent_users}")
    print(f"  Duration:    {duration_seconds}s")
    print(f"{'='*60}\n")
    
    # Connection pool settings
    connector = aiohttp.TCPConnector(
        limit=concurrent_users,
        limit_per_host=concurrent_users,
    )
    
    async with aiohttp.ClientSession(connector=connector) as session:
        # Create all user tasks
        tasks = [
            user_session(session, base_url, stats, duration_seconds, i)
            for i in range(concurrent_users)
        ]
        
        # Progress indicator
        async def progress():
            start = time.time()
            while True:
                elapsed = time.time() - start
                if elapsed >= duration_seconds:
                    break
                pct = int(elapsed / duration_seconds * 100)
                reqs = stats.total_requests
                err = stats.error_count
                print(f"\r  Progress: [{pct:3d}%] | Requests: {reqs:6d} | Errors: {err:4d}", end="", flush=True)
                await asyncio.sleep(0.5)
            print()
        
        # Run all tasks concurrently
        await asyncio.gather(progress(), *tasks)
    
    stats.end_time = time.time()
    return stats


def print_results(stats: LoadTestStats, target_error_rate: float = 1.0):
    """Print test results."""
    summary = stats.summary()
    
    error_rate = summary["error_rate_percent"]
    passed = error_rate <= target_error_rate
    
    print(f"\n{'='*60}")
    print(f"📊 TEST RESULTS")
    print(f"{'='*60}")
    
    print(f"\n  Duration:        {summary['duration_seconds']:.1f}s")
    print(f"  Total Requests:  {summary['total_requests']:,}")
    print(f"  Successful:      {summary['success_count']:,}")
    print(f"  Failed:          {summary['error_count']:,}")
    
    print(f"\n  {'─'*40}")
    print(f"  Throughput:      {summary['rps']:.1f} req/s")
    
    print(f"\n  {'─'*40}")
    print(f"  Latency:")
    lat = summary["latency"]
    print(f"    Avg:           {lat['avg_ms']:.1f} ms")
    print(f"    Min:           {lat['min_ms']:.1f} ms")
    print(f"    Max:           {lat['max_ms']:.1f} ms")
    print(f"    P50:           {lat['p50_ms']:.1f} ms")
    print(f"    P95:           {lat['p95_ms']:.1f} ms")
    print(f"    P99:           {lat['p99_ms']:.1f} ms")
    
    print(f"\n  {'─'*40}")
    print(f"  Status Codes:")
    for code, count in sorted(summary["status_codes"].items()):
        print(f"    {code}: {count:,}")
    
    print(f"\n  {'─'*40}")
    print(f"  Endpoint RPS:")
    for ep, rps in sorted(summary["endpoint_rps"].items(), key=lambda x: -x[1]):
        print(f"    {ep}: {rps:.1f}/s")
    
    print(f"\n{'='*60}")
    if passed:
        print(f"  ✅ PASSED: Error rate {error_rate:.2f}% ≤ {target_error_rate}%")
    else:
        print(f"  ❌ FAILED: Error rate {error_rate:.2f}% > {target_error_rate}%")
    print(f"{'='*60}\n")
    
    if stats.errors:
        print(f"\n  Sample Errors ({min(5, len(stats.errors))} of {len(stats.errors)}):")
        for err in stats.errors[:5]:
            print(f"    - {err}")
    
    return passed


def main():
    parser = argparse.ArgumentParser(description="Jarvis Mission Control Load Test")
    parser.add_argument(
        "--target", "-t",
        default="http://localhost:8000",
        help="Target URL (default: http://localhost:8000)"
    )
    parser.add_argument(
        "--users", "-u",
        type=int,
        default=100,
        help="Concurrent users (default: 100)"
    )
    parser.add_argument(
        "--duration", "-d",
        type=int,
        default=30,
        help="Test duration in seconds (default: 30)"
    )
    parser.add_argument(
        "--error-rate", "-e",
        type=float,
        default=1.0,
        help="Max acceptable error rate %% (default: 1.0)"
    )
    
    args = parser.parse_args()
    
    stats = asyncio.run(run_load_test(
        base_url=args.target,
        concurrent_users=args.users,
        duration_seconds=args.duration,
    ))
    
    passed = print_results(stats, args.error_rate)
    exit(0 if passed else 1)


if __name__ == "__main__":
    main()
