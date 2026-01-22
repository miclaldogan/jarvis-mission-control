from __future__ import annotations

import time
from typing import Any, Dict

import httpx

FRANKFURTER_URL = "https://api.frankfurter.app/latest"
DEFAULT_TIMEOUT_SECONDS = 5


async def fetch_exchange_rates(
    base: str = "EUR",
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
) -> Dict[str, Any]:
    """
    Fetch exchange rates from Frankfurter (ECB-based). No API key required.

    Contract:
    - NEVER raises (returns ok=False on failure)
    - Returns at least: ok: bool, elapsed_ms: int
    """
    start = time.perf_counter()

    try:
        timeout = httpx.Timeout(timeout_seconds)
        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.get(FRANKFURTER_URL, params={"base": base})
            resp.raise_for_status()
            data = resp.json()

        elapsed_ms = int((time.perf_counter() - start) * 1000)
        return {
            "ok": True,
            "base": data.get("base", base),
            "rates": data.get("rates", {}),
            "observed_at": data.get("date"),  # "YYYY-MM-DD"
            "elapsed_ms": elapsed_ms,
        }
    except Exception as e:
        elapsed_ms = int((time.perf_counter() - start) * 1000)
        return {"ok": False, "error": str(e), "elapsed_ms": elapsed_ms}
