import os
from __future__ import annotations

from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # App
    app_version: str = "0.1.0"
    redis_url: str = "redis://redis:6379/0"
    cache_ttl_seconds: int = 120
    
    # Weather
    weather_lat: str
    weather_lon: str
    weather_city: str = "Unknown"
    weather_tz: str = "Europe/Istanbul"
    
    # GitHub
    github_owner: str
    github_repo: str
    github_token: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = False


def get_settings() -> Settings:
    """Load and validate settings from environment."""
    try:
        return Settings()
    except Exception as e:
        # Provide clear error message listing missing required variables
        error_msg = str(e)
        if "validation error" in error_msg.lower():
            print("\n❌ Missing required environment variables:")
            print("   - WEATHER_LAT")
            print("   - WEATHER_LON")
            print("   - GITHUB_OWNER")
            print("   - GITHUB_REPO")
            print("\nOptional:")
            print("   - GITHUB_TOKEN (for higher GitHub API rate limits)")
            print("   - WEATHER_CITY (default: Unknown)")
            print("   - WEATHER_TZ (default: Europe/Istanbul)")
        raise

# --- NEWS SETTINGS (AUTO) ---
NEWS_RSS_FEED_URL = os.getenv("NEWS_RSS_FEED_URL", "https://feeds.bbci.co.uk/news/world/rss.xml")
NEWS_LIMIT = int(os.getenv("NEWS_LIMIT", "5"))

