"""Application settings, read once from environment variables."""

import os
from dataclasses import dataclass

DEFAULT_CORS_ORIGINS = "http://localhost:4173,http://localhost:5173"


@dataclass(frozen=True)
class Settings:
    app_name: str
    version: str
    cors_origins: list[str]
    host: str
    port: int


def load_settings() -> Settings:
    origins = os.environ.get("CORS_ORIGINS", DEFAULT_CORS_ORIGINS)
    return Settings(
        app_name=os.environ.get("APP_NAME", "Playgorithm"),
        version=os.environ.get("APP_VERSION", "0.1.0"),
        cors_origins=[origin.strip() for origin in origins.split(",") if origin.strip()],
        host=os.environ.get("APP_HOST", "127.0.0.1"),
        port=int(os.environ.get("APP_PORT", "8000")),
    )
