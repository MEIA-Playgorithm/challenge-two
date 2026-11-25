from domain.health import Health


class HealthService:
    def __init__(self, version: str) -> None:
        self._version = version

    def check(self) -> Health:
        return Health(status="ok", version=self._version)
