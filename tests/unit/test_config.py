"""Unit tests for src/config.py — Pydantic-settings Pattern C validation."""

import pytest
from pydantic import ValidationError

from src.config import APIConfig, OAuthConfig, Settings, TelemetryConfig


def test_settings_default_values():
    """Verify default values load correctly."""
    # dev_mode=true in config.toml allows empty api_key
    settings = Settings()
    assert settings.dev_mode is True
    assert str(settings.api.base_url) == "http://localhost:8001/"
    assert settings.api.timeout == 30
    assert settings.api.max_retries == 3
    assert settings.telemetry.enabled is True
    assert settings.telemetry.service_name == "pantry-mcp"


def test_settings_env_override(monkeypatch):
    """Verify ENV vars override config.toml (hierarchical priority)."""
    monkeypatch.setenv("PANTRY_API__BASE_URL", "https://api.production.com")
    monkeypatch.setenv("PANTRY_API__TIMEOUT", "60")
    monkeypatch.setenv("PANTRY_TELEMETRY__SAMPLING_RATIO", "0.1")

    settings = Settings()
    assert str(settings.api.base_url) == "https://api.production.com/"
    assert settings.api.timeout == 60
    assert settings.telemetry.sampling_ratio == 0.1


def test_api_key_required_when_dev_mode_false(monkeypatch):
    """api_key must be set when dev_mode=false."""
    monkeypatch.setenv("PANTRY_DEV_MODE", "false")
    # No PANTRY_API__API_KEY set

    with pytest.raises(ValidationError, match="api_key is required"):
        Settings()


def test_api_key_accepts_value(monkeypatch):
    """api_key can be set via ENV and SecretStr unwraps correctly."""
    monkeypatch.setenv("PANTRY_DEV_MODE", "false")
    monkeypatch.setenv("PANTRY_API__API_KEY", "secret123")

    settings = Settings()
    assert settings.api.api_key.get_secret_value() == "secret123"


def test_oauth_enabled_raises_v010_not_implemented():
    """oauth.enabled=true raises at boot (v0.1.0 ships API key only)."""
    with pytest.raises(
        ValidationError,
        match="v0.1.0 ships API key auth only",
    ):
        Settings(oauth=OAuthConfig(enabled=True, issuer="https://auth.example.com"))


def test_oauth_issuer_required_when_enabled():
    """oauth.issuer must be set when oauth.enabled=true."""
    with pytest.raises(ValidationError, match="oauth.issuer is required"):
        OAuthConfig(enabled=True)


def test_telemetry_config_defaults():
    """Verify TelemetryConfig default values."""
    config = TelemetryConfig()
    assert config.enabled is True
    assert config.otlp_endpoint == "http://localhost:4318/v1/traces"
    assert config.service_name == "pantry-mcp"
    assert config.sampling_ratio == 1.0


def test_api_config_secret_str_no_repr_leak():
    """SecretStr prevents api_key from appearing in repr/logs."""
    config = APIConfig(api_key="secret123")
    repr_str = repr(config)
    assert "secret123" not in repr_str
    assert "SecretStr" in repr_str
