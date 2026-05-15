from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", ".env.local"),
        env_prefix="ACS_FSM_",
        env_nested_delimiter="__",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "ACS FSM Backend"
    app_version: str = "0.1.0"
    service_name: str = "acs-fsm-backend"
    environment: str = "development"
    log_level: str = "INFO"

    api_v1_prefix: str = "/api/v1"
    proxy_root_path: str = ""
    cors_allowed_origins: list[str] = Field(default_factory=list)

    database_url: str = "postgresql+psycopg://acs_user:change-me@localhost:5432/acs_fsm"
    database_echo: bool = False


@lru_cache
def get_settings() -> Settings:
    return Settings()
