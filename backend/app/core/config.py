from functools import lru_cache
from typing import Literal, Self

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import make_url
from sqlalchemy.exc import ArgumentError

EnvironmentName = Literal["development", "testing", "production"]
LogFormat = Literal["json", "plain"]

LOCAL_DATABASE_HOSTS = {"localhost", "127.0.0.1", "::1", "0.0.0.0"}
PLACEHOLDER_DATABASE_PASSWORDS = {"change-me", "changeme", "password", "secret"}


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", ".env.local"),
        env_prefix="ACS_FSM_",
        env_nested_delimiter="__",
        case_sensitive=False,
        env_ignore_empty=True,
        validate_default=True,
        extra="ignore",
    )

    app_name: str = "ACS FSM Backend"
    app_version: str = "0.1.0"
    service_name: str = "acs-fsm-backend"
    environment: EnvironmentName = "development"
    log_level: str = "INFO"
    log_format: LogFormat = "json"

    api_v1_prefix: str = "/api/v1"
    api_summary: str = "Backend API foundation for the ACS Field Service Management platform."
    api_description: str = (
        "Phase 0 backend foundation. Business workflows, live integrations, auth, and frontend "
        "UI are intentionally deferred."
    )
    api_docs_enabled: bool = True
    proxy_root_path: str = ""
    cors_allowed_origins: list[str] = Field(default_factory=list)
    request_id_header: str = "X-Request-ID"

    database_url: str = "postgresql+psycopg://acs_user:change-me@db.example.internal:5432/acs_fsm"
    database_echo: bool = False
    database_pool_pre_ping: bool = True

    @field_validator("environment", mode="before")
    @classmethod
    def normalize_environment(cls, value: str) -> str:
        normalized = value.strip().lower()
        if normalized == "test":
            return "testing"
        return normalized

    @field_validator("api_v1_prefix")
    @classmethod
    def validate_api_prefix(cls, value: str) -> str:
        normalized = value.rstrip("/")
        if not normalized.startswith("/"):
            msg = "api_v1_prefix must start with /"
            raise ValueError(msg)
        return normalized or "/api/v1"

    @model_validator(mode="after")
    def validate_database_settings(self) -> Self:
        database_url = self._parse_database_url()

        if not database_url.get_backend_name().startswith("postgresql"):
            msg = "database_url must use a PostgreSQL SQLAlchemy driver"
            raise ValueError(msg)

        if self.environment == "production":
            host = (database_url.host or "").lower()
            password = database_url.password

            if host in LOCAL_DATABASE_HOSTS:
                msg = "production database_url must not use a local database host"
                raise ValueError(msg)
            if ".example." in host or host.startswith("db.example"):
                msg = "production database_url must not use placeholder example hosts"
                raise ValueError(msg)
            if password is None or password in PLACEHOLDER_DATABASE_PASSWORDS:
                msg = "production database_url must not use placeholder database credentials"
                raise ValueError(msg)
            if self.database_echo:
                msg = "database_echo must be disabled in production"
                raise ValueError(msg)

        return self

    @property
    def is_development(self) -> bool:
        return self.environment == "development"

    @property
    def is_testing(self) -> bool:
        return self.environment == "testing"

    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    @property
    def openapi_url(self) -> str | None:
        return self._versioned_url("openapi.json") if self.api_docs_enabled else None

    @property
    def docs_url(self) -> str | None:
        return self._versioned_url("docs") if self.api_docs_enabled else None

    @property
    def redoc_url(self) -> str | None:
        return self._versioned_url("redoc") if self.api_docs_enabled else None

    @property
    def redacted_database_url(self) -> str:
        return self._parse_database_url().render_as_string(hide_password=True)

    def _versioned_url(self, path: str) -> str:
        return f"{self.api_v1_prefix}/{path.lstrip('/')}"

    def _parse_database_url(self):
        try:
            return make_url(self.database_url)
        except ArgumentError as exc:
            msg = "database_url must be a valid SQLAlchemy database URL"
            raise ValueError(msg) from exc


@lru_cache
def get_settings() -> Settings:
    return Settings()
