from datetime import datetime

from app.schemas.dashboard import DashboardSchema


class AuthStatusResponse(DashboardSchema):
    generated_at: datetime
    auth_enabled: bool
    auth_provider: str
    auth_mode: str
    token_verification_enabled: bool
    disabled_token_verifier_available: bool
    rbac_enforcement_enabled: bool
    route_protection_enforced: bool
    current_routes_require_auth: bool
    authorization_header_required: bool
    authorization_header_parsed: bool
    authorization_header_can_grant_authority: bool
    jwks_fetch_enabled: bool
    real_token_parsing_enabled: bool
    login_ui_available: bool
    user_management_available: bool
    manual_review_action_authority_granted: bool
    water_emergency_action_authority_granted: bool
    action_execution_available: bool
    phase_allows_auth_enforcement: bool
    phase_allows_rbac_enforcement: bool
    phase_allows_route_guarding: bool
    reason: str
