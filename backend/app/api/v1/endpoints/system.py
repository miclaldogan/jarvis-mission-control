from __future__ import annotations

import importlib

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from app.http_envelope import err, ok

router = APIRouter()


@router.get("/system/vitals")
async def system_vitals(request: Request):
    """
    Return real system metrics (CPU, memory, network, disk).
    If psutil is not installed, return 503 with standard error envelope.
    """
    try:
        psutil = importlib.import_module("psutil")
    except ModuleNotFoundError:
        body, status = err(
            request,
            code="psutil_missing",
            message="psutil is required for system vitals. Install backend requirements.",
            status_code=503,
        )
        return JSONResponse(content=body, status_code=status)

    cpu_percent = float(psutil.cpu_percent(interval=0.1))
    cpu_cores = int(psutil.cpu_count() or 0)

    mem = psutil.virtual_memory()
    mem_percent = float(mem.percent)
    mem_used_gb = round(mem.used / 1e9, 2)
    mem_total_gb = round(mem.total / 1e9, 2)

    net = psutil.net_io_counters()
    bytes_sent = int(net.bytes_sent)
    bytes_recv = int(net.bytes_recv)

    disk = psutil.disk_usage("/")
    disk_percent = float(disk.percent)
    disk_used_gb = round(disk.used / 1e9, 2)
    disk_total_gb = round(disk.total / 1e9, 2)

    data = {
        "cpu": {"percent": cpu_percent, "cores": cpu_cores},
        "memory": {"percent": mem_percent, "used_gb": mem_used_gb, "total_gb": mem_total_gb},
        "network": {"bytes_sent": bytes_sent, "bytes_recv": bytes_recv},
        "disk": {"percent": disk_percent, "used_gb": disk_used_gb, "total_gb": disk_total_gb},
    }
    return ok(request, data)
