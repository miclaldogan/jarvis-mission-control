from __future__ import annotations

from typing import Optional
from pydantic_settings import BaseSettings


<<<<<<< HEAD
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

=======
@dataclass(frozen=True)
class Settings:
    app_version: str
    redis_url: str
    cache_ttl_seconds: int
    synthetic_ratelimit_per_min: int
    synthetic_ratelimit_window_seconds: int
    cors_allowed_origins: tuple[str, ...]
    cors_allow_credentials: bool


def _parse_bool(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _parse_csv(value: str) -> tuple[str, ...]:
    items = [item.strip() for item in value.split(",")]
    return tuple([item for item in items if item])


def get_settings() -> Settings:
    return Settings(
        app_version=os.getenv("APP_VERSION", "0.1.0"),
        redis_url=os.getenv("REDIS_URL", "redis://redis:6379/0"),
        cache_ttl_seconds=int(os.getenv("CACHE_TTL_SECONDS", "120")),
        synthetic_ratelimit_per_min=int(os.getenv("SYNTHETIC_RATELIMIT_PER_MIN", "30")),
        synthetic_ratelimit_window_seconds=int(os.getenv("SYNTHETIC_RATELIMIT_WINDOW_SECONDS", "60")),
        cors_allowed_origins=_parse_csv(
            os.getenv("CORS_ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000")
        ),
        cors_allow_credentials=_parse_bool(os.getenv("CORS_ALLOW_CREDENTIALS", "false")),
    )
>>>>>>> origin/dev
