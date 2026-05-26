from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class AuthMode(StrEnum):
    DISABLED = "disabled"
    READ_ONLY_PHASE_0 = "read_only_phase_0"


class AuthProvider(StrEnum):
    DISABLED = "disabled"


class AuthStatus(StrEnum):
    DISABLED = "disabled"
    NOT_VERIFIED = "not_verified"
    ANONYMOUS_PHASE_0 = "anonymous_phase_0"
    FUTURE_AUTH_NOT_ENABLED = "future_auth_not_enabled"


@dataclass(frozen=True, slots=True)
class AuthPrincipal:
    subject: str | None
    email: str | None
    display_name: str
    roles: tuple[str, ...]
    permissions: tuple[str, ...]
    provider: AuthProvider
    authenticated: bool
    is_service_account: bool
    manual_review_action_authority_granted: bool
    water_emergency_action_authority_granted: bool
    reason: str


@dataclass(frozen=True, slots=True)
class AnonymousPhase0Principal(AuthPrincipal):
    pass


@dataclass(frozen=True, slots=True)
class TokenVerificationResult:
    status: AuthStatus
    verified: bool
    token_present: bool
    token_parsed: bool
    signature_verified: bool
    jwks_fetch_attempted: bool
    provider_contacted: bool
    subject: str | None
    reason: str


@dataclass(frozen=True, slots=True)
class AuthContext:
    auth_mode: AuthMode
    auth_provider: AuthProvider
    status: AuthStatus
    principal: AuthPrincipal
    authenticated: bool
    auth_enabled: bool
    token_verified: bool
    rbac_enforced: bool
    phase_allows_enforcement: bool
    authorization_header_present: bool
    manual_review_action_authority_granted: bool
    water_emergency_action_authority_granted: bool
    token_verification_result: TokenVerificationResult
    reason: str


@dataclass(frozen=True, slots=True)
class DisabledAuthContext(AuthContext):
    pass


def build_anonymous_phase0_principal() -> AnonymousPhase0Principal:
    return AnonymousPhase0Principal(
        subject=None,
        email=None,
        display_name="Anonymous Phase 0 viewer",
        roles=(),
        permissions=(),
        provider=AuthProvider.DISABLED,
        authenticated=False,
        is_service_account=False,
        manual_review_action_authority_granted=False,
        water_emergency_action_authority_granted=False,
        reason=(
            "Authentication is disabled in Phase 0; this principal is not an "
            "authenticated operator and grants no action authority."
        ),
    )
