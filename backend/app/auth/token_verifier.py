from __future__ import annotations

from typing import Protocol

from app.auth.types import AuthStatus, TokenVerificationResult


class AuthNotImplementedError(RuntimeError):
    """Raised only by strict future-auth helpers that are not wired to Phase 0 routes."""


class TokenVerifier(Protocol):
    def verify_authorization_header(
        self,
        authorization_header: str | None = None,
    ) -> TokenVerificationResult:
        """Return token verification evidence without exposing credential values."""


class DisabledTokenVerifier:
    def verify_authorization_header(
        self,
        authorization_header: str | None = None,
    ) -> TokenVerificationResult:
        return TokenVerificationResult(
            status=AuthStatus.DISABLED,
            verified=False,
            token_present=bool(authorization_header),
            token_parsed=False,
            signature_verified=False,
            jwks_fetch_attempted=False,
            provider_contacted=False,
            subject=None,
            reason=(
                "Token verification is disabled in Phase 0. Authorization header "
                "presence is recorded only as redacted readiness context and never "
                "grants authentication or action authority."
            ),
        )

    def require_verified_token(
        self,
        authorization_header: str | None = None,
    ) -> TokenVerificationResult:
        self.verify_authorization_header(authorization_header)
        raise AuthNotImplementedError(
            "Strict authentication is not implemented or enabled in Phase 0."
        ) from None


disabled_token_verifier = DisabledTokenVerifier()
