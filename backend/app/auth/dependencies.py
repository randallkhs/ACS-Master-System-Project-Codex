from typing import Annotated

from fastapi import Header, HTTPException, status

from app.auth.token_verifier import disabled_token_verifier
from app.auth.types import (
    AuthMode,
    AuthProvider,
    AuthStatus,
    DisabledAuthContext,
    build_anonymous_phase0_principal,
)

AuthorizationHeader = Annotated[str | None, Header(alias="Authorization")]


def current_phase_allows_auth_enforcement() -> bool:
    return False


def get_disabled_auth_context(
    authorization_header: str | None = None,
) -> DisabledAuthContext:
    verification_result = disabled_token_verifier.verify_authorization_header(
        authorization_header,
    )
    principal = build_anonymous_phase0_principal()

    return DisabledAuthContext(
        auth_mode=AuthMode.READ_ONLY_PHASE_0,
        auth_provider=AuthProvider.DISABLED,
        status=AuthStatus.ANONYMOUS_PHASE_0,
        principal=principal,
        authenticated=False,
        auth_enabled=False,
        token_verified=verification_result.verified,
        rbac_enforced=False,
        phase_allows_enforcement=current_phase_allows_auth_enforcement(),
        authorization_header_present=verification_result.token_present,
        manual_review_action_authority_granted=False,
        water_emergency_action_authority_granted=False,
        token_verification_result=verification_result,
        reason=(
            "Phase 0 exposes a non-enforcing auth context for future planning only. "
            "Current routes remain public read-only routes and no action authority is granted."
        ),
    )


def get_phase0_auth_context(
    authorization_header: AuthorizationHeader = None,
) -> DisabledAuthContext:
    return get_disabled_auth_context(authorization_header)


def get_optional_auth_context(
    authorization_header: AuthorizationHeader = None,
) -> DisabledAuthContext:
    return get_disabled_auth_context(authorization_header)


def require_auth_future_not_enabled() -> None:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Authentication enforcement is not implemented or enabled in Phase 0.",
    )
