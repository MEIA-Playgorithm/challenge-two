from fastapi import APIRouter

from api.schemas.health import HealthResponse, to_health_response
from services.health_service import HealthService


def build_health_router(service: HealthService) -> APIRouter:
    router = APIRouter(tags=["health"])

    def get_health() -> HealthResponse:
        return to_health_response(service.check())

    router.add_api_route("/health", get_health, methods=["GET"], response_model=HealthResponse)
    return router
