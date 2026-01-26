#!/usr/bin/env python
"""
Quick verification script to test the context ingestion without running the full server.
Run from backend/ directory: python ../verify_ingestion.py
"""
import os
import asyncio
import sys

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

from app.services.ingestion.weather import fetch_weather
from app.services.ingestion.github import fetch_github


async def verify():
    """Test weather and GitHub ingestion."""
    print("🔍 Verifying ingestion services...\n")

    # Check environment variables
    print("📋 Environment variables:")
    env_vars = {
        "WEATHER_LAT": os.getenv("WEATHER_LAT"),
        "WEATHER_LON": os.getenv("WEATHER_LON"),
        "WEATHER_CITY": os.getenv("WEATHER_CITY", "Unknown"),
        "WEATHER_TZ": os.getenv("WEATHER_TZ", "Europe/Istanbul"),
        "GITHUB_OWNER": os.getenv("GITHUB_OWNER"),
        "GITHUB_REPO": os.getenv("GITHUB_REPO"),
        "GITHUB_TOKEN": "***" if os.getenv("GITHUB_TOKEN") else "(not set)",
    }
    for key, value in env_vars.items():
        status = "✅" if value or key in ("WEATHER_CITY", "WEATHER_TZ", "GITHUB_TOKEN") else "❌"
        print(f"  {status} {key}: {value}")

    # Test weather
    print("\n🌤️  Testing weather ingestion...")
    try:
        weather = await fetch_weather()
        print(f"  ✅ Success: temp_c={weather['temp']}, condition={weather['condition']}")
    except Exception as e:
        print(f"  ❌ Failed: {e}")

    # Test GitHub
    print("\n🐙 Testing GitHub ingestion...")
    try:
        github = await fetch_github()
        print(f"  ✅ Success: open_issues={github['open_issues']}, open_prs={github['open_prs']}")
    except Exception as e:
        print(f"  ❌ Failed: {e}")

    print("\n✨ Verification complete!")


if __name__ == "__main__":
    asyncio.run(verify())
