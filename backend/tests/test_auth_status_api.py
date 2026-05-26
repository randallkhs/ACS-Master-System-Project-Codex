from fastapi.testclient import TestClient

from app.core.config import Settings
from app.main import create_app


def authorization_header_value() -> str:
    return "Bearer opaque-phase0-non-token"


def test_auth_status_endpoint_reports_disabled_phase0_without_authorization() -> None:
    settings = Settings(
        environment="testing",
        database_url="postgresql+psycopg://acs_user:acs_pass@db.internal:5432/acs_fsm_test",
    )
    with TestClient(create_app(settings)) as client:
        response = client.get("/api/v1/auth/status")

    assert response.status_code == 200
    payload = response.json()
    assert payload["auth_enabled"] is False
    assert payload["auth_provider"] == "disabled"
    assert payload["auth_mode"] == "read_only_phase_0"
    assert payload["token_verification_enabled"] is False
    assert payload["disabled_token_verifier_available"] is True
    assert payload["rbac_enforcement_enabled"] is False
    assert payload["route_protection_enforced"] is False
    assert payload["current_routes_require_auth"] is False
    assert payload["authorization_header_required"] is False
    assert payload["authorization_header_parsed"] is False
    assert payload["authorization_header_can_grant_authority"] is False
    assert payload["jwks_fetch_enabled"] is False
    assert payload["real_token_parsing_enabled"] is False
    assert payload["login_ui_available"] is False
    assert payload["user_management_available"] is False
    assert payload["manual_review_action_authority_granted"] is False
    assert payload["water_emergency_action_authority_granted"] is False
    assert payload["action_execution_available"] is False
    assert payload["phase_allows_auth_enforcement"] is False
    assert payload["phase_allows_rbac_enforcement"] is False
    assert payload["phase_allows_route_guarding"] is False


def test_auth_status_endpoint_does_not_parse_authorization_header_or_grant_authority() -> None:
    settings = Settings(
        environment="testing",
        database_url="postgresql+psycopg://acs_user:acs_pass@db.internal:5432/acs_fsm_test",
    )
    header_value = authorization_header_value()

    with TestClient(create_app(settings)) as client:
        response = client.get(
            "/api/v1/auth/status",
            headers={"Authorization": header_value},
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["authorization_header_required"] is False
    assert payload["authorization_header_parsed"] is False
    assert payload["authorization_header_can_grant_authority"] is False
    assert payload["token_verification_enabled"] is False
    assert payload["manual_review_action_authority_granted"] is False
    assert payload["water_emergency_action_authority_granted"] is False
    assert header_value not in response.text


def test_current_dashboard_routes_still_require_no_authorization_headers() -> None:
    settings = Settings(
        environment="testing",
        database_url="postgresql+psycopg://acs_user:acs_pass@db.internal:5432/acs_fsm_test",
    )
    with TestClient(create_app(settings)) as client:
        response = client.get("/api/v1/health")
        auth_status_response = client.get("/api/v1/auth/status")

    assert response.status_code == 200
    assert auth_status_response.status_code == 200
    assert auth_status_response.json()["current_routes_require_auth"] is False
