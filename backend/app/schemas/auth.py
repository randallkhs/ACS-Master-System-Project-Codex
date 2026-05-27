from datetime import datetime

from app.schemas.dashboard import DashboardSchema


class AuthCutoverPrerequisiteResponse(DashboardSchema):
    key: str
    label: str
    status: str
    satisfied_now: bool
    owner_review_required: bool
    reason: str


class CurrentRouteAccessibilityAuditItemResponse(DashboardSchema):
    method: str
    route: str
    currently_requires_auth: bool
    future_auth_required: bool
    future_permission: str
    enforcement_enabled: bool
    authorization_header_can_grant_authority: bool
    reason: str


class AuthStatusResponse(DashboardSchema):
    generated_at: datetime
    phase0_auth_boundary_complete: bool
    auth_implemented: bool
    auth_enabled: bool
    auth_provider: str
    auth_mode: str
    token_verification_enabled: bool
    real_token_parsing_enabled: bool
    disabled_token_verifier_available: bool
    backend_auth_core_available: bool
    frontend_disabled_session_available: bool
    auth_status_bridge_available: bool
    auth_status_endpoint_available: bool
    rbac_enforcement_enabled: bool
    rbac_enforced: bool
    route_protection_enforced: bool
    route_guarding_enabled: bool
    current_routes_require_auth: bool
    authorization_header_required: bool
    authorization_header_parsed: bool
    authorization_header_can_grant_authority: bool
    frontend_authorization_headers_emitted: bool
    jwks_fetch_enabled: bool
    login_ui_available: bool
    user_management_available: bool
    manual_review_action_authority_granted: bool
    water_emergency_action_authority_granted: bool
    action_execution_available: bool
    mutation_endpoints_available: bool
    secret_hygiene_helper_available: bool
    committed_credentials_allowed: bool
    real_credentials_required_for_future_auth: bool
    future_auth_cutover_ready: bool
    future_auth_cutover_blocked_by: tuple[str, ...]
    future_auth_cutover_prerequisites: tuple[AuthCutoverPrerequisiteResponse, ...]
    current_route_accessibility_audit: tuple[CurrentRouteAccessibilityAuditItemResponse, ...]
    phase_allows_auth_enforcement: bool
    phase_allows_rbac_enforcement: bool
    phase_allows_route_guarding: bool
    reason: str
