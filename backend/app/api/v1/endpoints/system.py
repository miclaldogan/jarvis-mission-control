from __future__ import annotations

from datetime import datetime, timezone

import psutil
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from app.http_envelope import ok
from app.metrics import get_cache_stats


router = APIRouter()


def _clamp_0_100(x: float) -> float:
    if x < 0:
        return 0.0
    if x > 100:
        return 100.0
    return x


@router.get("/system/vitals")
async def system_vitals(request: Request):
    """
    Real-time system vitals (CPU/Mem/Disk + lightweight network proxy).

    Notes:
      - CPU/Mem/Disk are real percentages (0-100).
      - Network utilization percent is not well-defined without link capacity;
        we return a capped proxy (0-100) + raw MB counters for visibility.
    """
    try:
        cpu = float(psutil.cpu_percent(interval=0.1))
        mem = float(psutil.virtual_memory().percent)

        # Docker/Linux friendly
        disk_usage = psutil.disk_usage("/")
        disk = float(disk_usage.percent)

        net = psutil.net_io_counters()
        sent_mb = float(net.bytes_sent) / 1024.0 / 1024.0
        recv_mb = float(net.bytes_recv) / 1024.0 / 1024.0
        net_mb_total = sent_mb + recv_mb

        data = {
            "cpu": round(_clamp_0_100(cpu), 1),
            "memory": round(_clamp_0_100(mem), 1),
            "disk": round(_clamp_0_100(disk), 1),

            # proxy metric that always stays 0-100 for UI/simple comparisons
            "network": round(_clamp_0_100(net_mb_total), 1),

            # raw counters for future improvements
            "network_mb_sent": round(sent_mb, 1),
            "network_mb_recv": round(recv_mb, 1),

            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        return JSONResponse(ok(request, data), status_code=200)
    except Exception as e:
        # keep envelope shape even on failure (CI-friendly)
        data = {
            "cpu": 0.0,
            "memory": 0.0,
            "disk": 0.0,
            "network": 0.0,
            "network_mb_sent": 0.0,
            "network_mb_recv": 0.0,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "error": str(e),
        }
        return JSONResponse(ok(request, data), status_code=200)


@router.get("/metrics/cache")
async def cache_metrics(request: Request):
    """
    Get cache performance statistics.
    
    Returns:
        - hits: Total cache hits
        - misses: Total cache misses
        - total_requests: Total requests (hits + misses)
        - hit_rate_percent: Cache hit rate as percentage
        - avg_compute_time_ms: Average compute time in milliseconds
    """
    stats = get_cache_stats()
    return JSONResponse(ok(request, stats), status_code=200)
