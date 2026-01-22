import os
import httpx
from typing import Dict


# WMO Weather interpretation codes to our condition schema
# https://open-meteo.com/en/docs
WEATHERCODE_TO_CONDITION = {
    0: "clear",      # Clear sky
    1: "clear",      # Mainly clear
    2: "cloudy",     # Partly cloudy
    3: "cloudy",     # Overcast
    45: "cloudy",    # Foggy
    48: "cloudy",    # Depositing rime fog
    51: "rain",      # Light drizzle
    53: "rain",      # Moderate drizzle
    55: "rain",      # Dense drizzle
    61: "rain",      # Slight rain
    63: "rain",      # Moderate rain
    65: "rain",      # Heavy rain
    71: "snow",      # Slight snow
    73: "snow",      # Moderate snow
    75: "snow",      # Heavy snow
    77: "snow",      # Snow grains
    80: "rain",      # Slight rain showers
    81: "rain",      # Moderate rain showers
    82: "rain",      # Violent rain showers
    85: "snow",      # Slight snow showers
    86: "snow",      # Heavy snow showers
    95: "rain",      # Thunderstorm
    96: "rain",      # Thunderstorm with slight hail
    99: "rain",      # Thunderstorm with heavy hail
}


async def fetch_weather() -> Dict[str, any]:
    """
    Fetch current weather from Open-Meteo and return normalized WeatherContext.

    Reads from environment:
    - WEATHER_LAT: latitude (required)
    - WEATHER_LON: longitude (required)
    - WEATHER_TZ: timezone (default: Europe/Istanbul)

    Returns:
        {"temp": <float>, "condition": <string>}

    Raises:
        Exception: On HTTP error, missing env vars, or parse error.
    """
    lat = os.getenv("WEATHER_LAT")
    lon = os.getenv("WEATHER_LON")
    tz = os.getenv("WEATHER_TZ", "Europe/Istanbul")

    if not lat or not lon:
        raise Exception("Missing required env vars: WEATHER_LAT, WEATHER_LON")

    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current_weather": True,
        "timezone": tz,
    }

    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(url, params=params)

        if resp.status_code != 200:
            raise Exception(
                f"Open-Meteo returned {resp.status_code}: {resp.text}"
            )

        try:
            data = resp.json()
            current = data.get("current_weather")

            if not current:
                raise Exception("No 'current_weather' in Open-Meteo response")

            temp = current.get("temperature") if current.get("temperature") is not None else current.get("temp")

            weathercode = current.get("weathercode") or current.get("weather_code")


            if temp is None or weathercode is None:
                raise Exception(
                    "Missing 'temperature' or 'weather_code' in current_weather"
                )

            condition = WEATHERCODE_TO_CONDITION.get(weathercode, "unknown")

            return {"temp": temp, "condition": condition}

        except ValueError as e:
            raise Exception(f"Failed to parse Open-Meteo response: {e}")
