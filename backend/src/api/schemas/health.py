from pydantic import BaseModel

from domain.health import Health


class HealthResponse(BaseModel):
    status: str
    version: str


def to_health_response(health: Health) -> HealthResponse:
    return HealthResponse(status=health.status, version=health.version)
