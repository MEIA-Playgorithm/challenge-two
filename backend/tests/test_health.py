from fastapi.testclient import TestClient

from core.settings import Settings
from main import create_app
from services.health_service import HealthService


def make_settings() -> Settings:
    return Settings(app_name="Playgorithm", version="test", cors_origins=[])


def test_health_service_reports_ok() -> None:
    health = HealthService(version="test").check()

    assert health.status == "ok"
    assert health.version == "test"


def test_health_route_returns_status_and_version() -> None:
    client = TestClient(create_app(make_settings()))

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "version": "test"}
