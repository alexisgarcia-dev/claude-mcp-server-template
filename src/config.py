"""Configuration management using Pydantic-settings Pattern C.

Hierarchical priority: ENV vars > .env file > config.toml > defaults

Example override at deployment:
    PANTRY_API__API_KEY=secret123 uv run server

Nested model overrides use double underscore:
    PANTRY_OAUTH__ISSUER=https://auth.example.com

See: docs/design-v0.1.0.md §2
"""

import logging
import sys

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, SecretStr, model_validator
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    TomlConfigSettingsSource,
)

logger = logging.getLogger(__name__)


class OAuthConfig(BaseModel):
    """OAuth client configuration (v0.2.0).

    v0.1.0 ships API key auth only. OAuth client_credentials stub raises at boot if enabled.
    """

    model_config = ConfigDict(extra="forbid")

    enabled: bool = False
    issuer: HttpUrl | None = None
    client_id: str | None = None
    client_secret: SecretStr | None = None

    @model_validator(mode="after")
    def oauth_issuer_required_when_enabled(self):
        if self.enabled and not self.issuer:
            raise ValueError(
                "oauth.issuer is required when oauth.enabled=true. "
                "Set PANTRY_OAUTH__ISSUER env var or oauth.issuer in config.toml."
            )
        return self

    @model_validator(mode="after")
    def validate_oauth_implementation_available(self):
        if self.enabled:
            raise ValueError(
                "oauth.enabled=true is configured, but v0.1.0 ships API key auth only. "
                "OAuth client_credentials flow ships in v0.2.0. "
                "Set oauth.enabled=false in config.toml or wait for v0.2.0 release. "
                "See src/auth/oauth_middleware.py for v0.2.0 integration scaffolding."
            )
        return self


class TelemetryConfig(BaseModel):
    """OpenTelemetry configuration."""

    model_config = ConfigDict(extra="forbid")

    enabled: bool = True
    otlp_endpoint: str = "http://localhost:4318/v1/traces"
    service_name: str = "pantry-mcp"
    sampling_ratio: float = 1.0


class APIConfig(BaseModel):
    """PantryAPI connection configuration."""

    model_config = ConfigDict(extra="forbid")

    base_url: HttpUrl = "http://localhost:8001"  # type: ignore[assignment]
    api_key: SecretStr = Field(default=SecretStr(""))
    timeout: int = 30
    max_retries: int = 3
    backoff_factor: float = 2.0


class Settings(BaseSettings):
    """Root configuration with hierarchical override.

    Priority: ENV > .env > config.toml > Docker secrets > defaults
    """

    model_config = SettingsConfigDict(
        env_prefix="PANTRY_",
        env_nested_delimiter="__",
        env_file=".env",
        toml_file="config.toml",
        extra="ignore",
    )

    api: APIConfig = Field(default_factory=APIConfig)
    oauth: OAuthConfig = Field(default_factory=OAuthConfig)
    telemetry: TelemetryConfig = Field(default_factory=TelemetryConfig)

    dev_mode: bool = False

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls,
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ):
        """Override priority order: init > env > .env > config.toml > file_secret."""
        return (
            init_settings,
            env_settings,
            dotenv_settings,
            TomlConfigSettingsSource(settings_cls),
            file_secret_settings,
        )

    @model_validator(mode="after")
    def validate_api_key_required(self):
        if not self.dev_mode and not self.api.api_key.get_secret_value():
            raise ValueError(
                "api_key is required. Set PANTRY_API__API_KEY in .env, "
                "OR set dev_mode=true in config.toml for local testing only."
            )
        return self

    @model_validator(mode="after")
    def warn_if_dev_mode(self):
        if self.dev_mode:
            warning_message = (
                "\n"
                "=" * 70 + "\n"
                "⚠️  WARNING: dev_mode=true detected.\n"
                "    API key validation is DISABLED.\n"
                "    This setting is for LOCAL DEVELOPMENT ONLY.\n"
                "    Set dev_mode=false in config.toml before production deployment.\n"
                + "=" * 70 + "\n"
            )
            logger.warning(warning_message)
            print(warning_message, file=sys.stderr)
        return self
