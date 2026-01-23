# backend/app/services/ingestion/traffic.py
from __future__ import annotations

import math
import os
from typing import Any, Dict, Optional, Tuple

import httpx


ORS_URL = "https://api.openrouteservice.org/v2/directions/driving-car"


def _get_float_env(name: str) -> Optional[float]:
    v = os.getenv(name)
    if v is None or v.strip() == "":
        return None
    try:
        return float(v)
    except ValueError:
        return None


def load_traffic_config() -> Tuple[Optional[str], Optional[float], Optional[float], Optional[float], Optional[float]]:
    """
    Reads traffic config from env:
      TRAFFIC_API_KEY
      TRAFFIC_ORIGIN_LAT, TRAFFIC_ORIGIN_LON
      TRAFFIC_DEST_LAT,   TRAFFIC_DEST_LON
    """
    key = os.getenv("TRAFFIC_API_KEY")
    o_lat = _get_float_env("TRAFFIC_ORIGIN_LAT")
    o_lon = _get_float_env("TRAFFIC_ORIGIN_LON")
    d_lat = _get_float_env("TRAFFIC_DEST_LAT")
    d_lon = _get_float_env("TRAFFIC_DEST_LON")
    return key, o_lat, o_lon, d_lat, d_lon


async def fetch_traffic_eta_minutes(timeout_s: float = 10.0) -> Dict[str, Any]:
    """
    Returns either:
      {"ok": True, "data": {"origin": {...}, "destination": {...}, "eta_minutes": int}}
    or
      {"ok": False, "skip_reason": "missing_api_key" | "missing_origin_destination" | "timeout" | "http_error_401" | ...}
    """
    key, o_lat, o_lon, d_lat, d_lon = load_traffic_config()

    if not key:
        return {"ok": False, "skip_reason": "missing_api_key"}

    if o_lat is None or o_lon is None or d_lat is None or d_lon is None:
        return {"ok": False, "skip_reason": "missing_origin_destination"}

    headers = {"Authorization": key}
    params = {
        "start": f"{o_lon},{o_lat}",  # ORS expects lon,lat
        "end": f"{d_lon},{d_lat}",
    }

    try:
        async with httpx.AsyncClient(timeout=timeout_s) as client:
            r = await client.get(ORS_URL, headers=headers, params=params)
            if r.status_code >= 400:
                return {"ok": False, "skip_reason": f"http_error_{r.status_code}"}

            payload = r.json()
            # ORS directions response: features[0].properties.summary.duration (seconds)
            duration_s = (
                payload.get("features", [{}])[0]
                .get("properties", {})
                .get("summary", {})
                .get("duration", None)
            )
            if duration_s is None:
                return {"ok": False, "skip_reason": "invalid_response"}

            eta_minutes = int(math.ceil(float(duration_s) / 60.0))
            return {
                "ok": True,
                "data": {
                    "origin": {"lat": o_lat, "lon": o_lon},
                    "destination": {"lat": d_lat, "lon": d_lon},
                    "eta_minutes": eta_minutes,
                },
            }

    except httpx.TimeoutException:
        return {"ok": False, "skip_reason": "timeout"}
    except Exception:
        # keep it safe; don't crash the whole /context
        return {"ok": False, "skip_reason": "unexpected_error"}
