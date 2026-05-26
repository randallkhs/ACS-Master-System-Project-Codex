from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from app.auth.dependencies import get_disabled_auth_context


def build_phase0_auth_status() -> dict[str, Any]:
    auth_context = get_disabled_auth_context()

    return {
        "generated_at": datetime.now(UTC),
        "auth_enabled": auth_context.auth_enabled,
        "auth_provider": auth_context.auth_provider.value,
        "auth_mode": auth_context.auth_mode.value,
        "token_verification_enabled": False,
        "disabled_token_verifier_available": True,
        "rbac_enforcement_enabled": auth_context.rbac_enforced,
        "route_protection_enforced": False,
        "current_routes_require_auth": False,
        "authorization_header_required": False,
        "authorization_header_parsed": False,
        "authorization_header_can_grant_authority": False,
        "jwks_fetch_enabled": False,
        "real_token_parsing_enabled": False,
        "login_ui_available": False,
        "user_management_available": False,
        "manual_review_action_authority_granted": (
            auth_context.manual_review_action_authority_granted
        ),
        "water_emergency_action_authority_granted": (
            auth_context.water_emergency_action_authority_granted
        ),
        "action_execution_available": False,
        "phase_allows_auth_enforcement": auth_context.phase_allows_enforcement,
        "phase_allows_rbac_enforcement": False,
        "phase_allows_route_guarding": False,
        "reason": (
            "Phase 0 auth status is a read-only bridge between the disabled "
            "backend auth scaffold and disabled frontend auth boundary. It does "
            "not parse Authorization headers, verify tokens, enforce RBAC, guard "
            "routes, or grant Manual Review or Water Emergency action authority."
        ),
    }
