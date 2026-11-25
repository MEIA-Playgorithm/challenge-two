"""Entry point. Builds every object by hand and connects the layers.

Order: settings, then services, then routes. Repositories go between settings and services when they exist.
"""

import argparse
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes.health import build_health_router
from core.settings import Settings, load_settings
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


app = create_app(load_settings())


def run() -> None:
    parser = argparse.ArgumentParser(description="Run the backend with uvicorn.")
    parser.add_argument(
        "--dev", action="store_true", default=False, help="Development mode: restart the server when code changes."
    )
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind.")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind.")
    args = parser.parse_args()

    src_dir = str(Path(__file__).resolve().parent)
    if args.dev:
        uvicorn.run("main:app", host=args.host, port=args.port, reload=True, reload_dirs=[src_dir], app_dir=src_dir)
    else:
        uvicorn.run("main:app", host=args.host, port=args.port, reload=False, app_dir=src_dir)


if __name__ == "__main__":
    run()
