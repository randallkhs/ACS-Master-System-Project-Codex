import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.auth.dependencies import (
    current_phase_allows_auth_enforcement,
    get_disabled_auth_context,
    get_optional_auth_context,
    get_phase0_auth_context,
    require_auth_future_not_enabled,
)
from app.auth.token_verifier import AuthNotImplementedError, DisabledTokenVerifier
from app.auth.types import AuthStatus
from app.core.config import Settings
from app.main import create_app


def jwt_like_header_value() -> str:
    unsigned_segments = ("header", "payload", "signature")
    return "Bearer " + ".".join(unsigned_segments)


def test_disabled_token_verifier_returns_not_verified_without_header() -> None:
    result = DisabledTokenVerifier().verify_authorization_header()

    assert result.status == AuthStatus.DISABLED
    assert result.verified is False
    assert result.token_present is False
    assert result.token_parsed is False
    assert result.signature_verified is False
    assert result.jwks_fetch_attempted is False
    assert result.provider_contacted is False
    assert result.subject is None


def test_disabled_token_verifier_does_not_parse_header_values() -> None:
    header_value = jwt_like_header_value()
    result = DisabledTokenVerifier().verify_authorization_header(header_value)

    assert result.status == AuthStatus.DISABLED
    assert result.verified is False
    assert result.token_present is True
    assert result.token_parsed is False
    assert result.signature_verified is False
    assert result.jwks_fetch_attempted is False
    assert result.provider_contacted is False
    assert result.subject is None
    assert header_value not in result.reason


def test_disabled_token_verifier_strict_method_is_not_wired_for_phase0() -> None:
    verifier = DisabledTokenVerifier()

    with pytest.raises(AuthNotImplementedError):
        verifier.require_verified_token(jwt_like_header_value())


def test_phase0_auth_context_is_anonymous_and_non_enforcing() -> None:
    context = get_phase0_auth_context(jwt_like_header_value())

    assert context.authenticated is False
    assert context.auth_enabled is False
    assert context.token_verified is False
    assert context.rbac_enforced is False
    assert context.phase_allows_enforcement is False
    assert context.authorization_header_present is True
    assert context.principal.authenticated is False
    assert context.principal.roles == ()
    assert context.principal.permissions == ()
    assert context.manual_review_action_authority_granted is False
    assert context.water_emergency_action_authority_granted is False
    assert context.token_verification_result.token_parsed is False


def test_optional_auth_context_without_header_does_not_require_authorization() -> None:
    context = get_optional_auth_context()

    assert context.authenticated is False
    assert context.authorization_header_present is False
    assert context.token_verified is False
    assert context.manual_review_action_authority_granted is False


def test_disabled_auth_context_never_grants_action_authority() -> None:
    context = get_disabled_auth_context(jwt_like_header_value())

    assert context.manual_review_action_authority_granted is False
    assert context.water_emergency_action_authority_granted is False
    assert context.principal.manual_review_action_authority_granted is False
    assert context.principal.water_emergency_action_authority_granted is False


def test_phase0_auth_enforcement_switch_remains_false() -> None:
    assert current_phase_allows_auth_enforcement() is False


def test_future_auth_requirement_helper_is_not_implemented() -> None:
    with pytest.raises(HTTPException) as exc_info:
        require_auth_future_not_enabled()

    assert exc_info.value.status_code == 501


def test_default_settings_keep_auth_disabled() -> None:
    settings = Settings(
        environment="testing",
        database_url="postgresql+psycopg://acs_user:acs_pass@db.internal:5432/acs_fsm_test",
    )

    assert settings.auth_provider == "disabled"
    assert settings.auth_enabled is False
    assert settings.auth_token_verification_enabled is False
    assert settings.auth_rbac_enforcement_enabled is False
    assert settings.auth_phase_allows_enforcement is False


def test_phase0_settings_reject_accidental_auth_enforcement() -> None:
    with pytest.raises(ValueError, match="Phase 0 auth scaffolding is non-enforcing"):
        Settings(
            environment="testing",
            database_url="postgresql+psycopg://acs_user:acs_pass@db.internal:5432/acs_fsm_test",
            auth_enabled=True,
        )


def test_existing_health_route_remains_accessible_without_auth() -> None:
    settings = Settings(
        environment="testing",
        database_url="postgresql+psycopg://acs_user:acs_pass@db.internal:5432/acs_fsm_test",
    )
    with TestClient(create_app(settings)) as client:
        response = client.get("/api/v1/health")

    assert response.status_code == 200


def test_authorization_header_does_not_grant_route_authority() -> None:
    settings = Settings(
        environment="testing",
        database_url="postgresql+psycopg://acs_user:acs_pass@db.internal:5432/acs_fsm_test",
    )
    with TestClient(create_app(settings)) as client:
        response = client.get("/api/v1/health", headers={"Authorization": jwt_like_header_value()})

    assert response.status_code == 200
