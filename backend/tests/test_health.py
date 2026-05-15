from fastapi.testclient import TestClient

from app.core.config import Settings
from app.main import create_app


def test_health_endpoint_reports_service_status_without_database_connection() -> None:
    settings = Settings(
        environment="testing",
        database_url="postgresql+psycopg://acs_user:acs_pass@db.internal:5432/acs_fsm_test",
    )
    with TestClient(create_app(settings)) as client:
        response = client.get("/api/v1/health")

    payload = response.json()
    assert response.status_code == 200
    assert payload == {
        "status": "ok",
        "service": "acs-fsm-backend",
        "environment": "testing",
        "version": "0.1.0",
        "ready": True,
        "started_at": payload["started_at"],
    }
    assert payload["started_at"] is not None


def test_health_endpoint_marks_response_with_request_id() -> None:
    settings = Settings(
        environment="testing",
        database_url="postgresql+psycopg://acs_user:acs_pass@db.internal:5432/acs_fsm_test",
    )
    with TestClient(create_app(settings)) as client:
        response = client.get("/api/v1/health", headers={"X-Request-ID": "req-test-123"})

    assert response.headers["X-Request-ID"] == "req-test-123"


def test_app_openapi_metadata_uses_versioned_urls() -> None:
    settings = Settings(
        environment="testing",
        app_name="ACS FSM Test API",
        database_url="postgresql+psycopg://acs_user:acs_pass@db.internal:5432/acs_fsm_test",
    )
    app = create_app(settings)

    assert app.title == "ACS FSM Test API"
    assert app.version == "0.1.0"
    assert app.openapi_url == "/api/v1/openapi.json"
    assert app.docs_url == "/api/v1/docs"
