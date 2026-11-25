"""Build the FastAPI app."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes.health import build_health_router
from core.settings import Settings
from services.health_service import HealthService


def create_app(settings: Settings) -> FastAPI:
    health_service = HealthService(version=settings.version)

    app = FastAPI(title=settings.app_name, version=settings.version)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(build_health_router(health_service))
    return app
