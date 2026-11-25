import pytest

from core.settings import load_settings


def test_load_settings_defaults_host_and_port(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("APP_HOST", raising=False)
    monkeypatch.delenv("APP_PORT", raising=False)

    settings = load_settings()

    assert settings.host == "127.0.0.1"
    assert settings.port == 8000
