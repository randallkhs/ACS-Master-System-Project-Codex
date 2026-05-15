import pytest
from pydantic import ValidationError

from app.core.config import Settings


def test_settings_support_environment_based_runtime_configuration() -> None:
    settings = Settings(
        environment="production",
        database_url="postgresql+psycopg://acs_user:acs_pass@db.internal:5432/acs_fsm",
        cors_allowed_origins=["https://app.applecleaningsystems.net"],
        proxy_root_path="/api",
    )

    assert settings.environment == "production"
    assert str(settings.database_url).startswith("postgresql+psycopg://")
    assert settings.api_v1_prefix == "/api/v1"
    assert settings.cors_allowed_origins == ["https://app.applecleaningsystems.net"]
    assert settings.proxy_root_path == "/api"


def test_settings_normalize_test_environment_alias() -> None:
    settings = Settings(
        environment="test",
        database_url="postgresql+psycopg://acs_user:acs_pass@db.internal:5432/acs_fsm_test",
    )

    assert settings.environment == "testing"
    assert settings.is_testing
    assert not settings.is_production


@pytest.mark.parametrize(
    "database_url",
    [
        "postgresql+psycopg://acs_user:secure-pass@localhost:5432/acs_fsm",
        "postgresql+psycopg://acs_user:change-me@db.internal:5432/acs_fsm",
        "postgresql+psycopg://acs_user:secure-pass@db.example.internal:5432/acs_fsm",
    ],
)
def test_production_database_url_rejects_unsafe_values(database_url: str) -> None:
    with pytest.raises(ValidationError):
        Settings(environment="production", database_url=database_url)


def test_settings_expose_versioned_documentation_urls() -> None:
    settings = Settings(
        environment="development",
        database_url="postgresql+psycopg://acs_user:change-me@db.internal:5432/acs_fsm",
    )

    assert settings.openapi_url == "/api/v1/openapi.json"
    assert settings.docs_url == "/api/v1/docs"
    assert settings.redoc_url == "/api/v1/redoc"


def test_settings_can_disable_api_documentation() -> None:
    settings = Settings(
        environment="production",
        api_docs_enabled=False,
        database_url="postgresql+psycopg://acs_user:secure-pass@db.internal:5432/acs_fsm",
    )

    assert settings.openapi_url is None
    assert settings.docs_url is None
    assert settings.redoc_url is None
