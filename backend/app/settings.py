from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    app_version: str
    redis_url: str
    cache_ttl_seconds: int


def get_settings() -> Settings:
    return Settings(
        app_version=os.getenv("APP_VERSION", "0.1.0"),
        redis_url=os.getenv("REDIS_URL", "redis://redis:6379/0"),
        cache_ttl_seconds=int(os.getenv("CACHE_TTL_SECONDS", "120")),
    )
