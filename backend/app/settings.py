from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    app_version: str
    redis_url: str
    cache_ttl_seconds: int
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
        cors_allowed_origins=_parse_csv(
            os.getenv("CORS_ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000")
        ),
        cors_allow_credentials=_parse_bool(os.getenv("CORS_ALLOW_CREDENTIALS", "false")),
    )
