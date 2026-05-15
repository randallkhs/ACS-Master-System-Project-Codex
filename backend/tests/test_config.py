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
