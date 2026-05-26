import type {
  AnonymousPhase0FrontendPrincipal,
  DisabledFrontendAuthSession,
  FrontendAuthStatus,
} from "@/lib/auth/types";

const PHASE_0_DISABLED_AUTH_REASON =
  "Frontend auth is disabled in Phase 0. No session, token, login UI, RBAC, route protection, or action authority is available.";

export function getAnonymousPhase0Principal(): AnonymousPhase0FrontendPrincipal {
  return {
    subject: null,
    email: null,
    display_name: "Anonymous Phase 0 viewer",
    roles: [],
    permissions: [],
    authenticated: false,
    manual_review_action_authority_granted: false,
    water_emergency_action_authority_granted: false,
  };
}

export function getDisabledFrontendAuthSession(): DisabledFrontendAuthSession {
  const principal = getAnonymousPhase0Principal();

  return {
    mode: "disabled",
    provider: "disabled",
    auth_enabled: false,
    authenticated: false,
    session_available: false,
    token_available: false,
    token_verified: false,
    phase_allows_auth_enforcement: false,
    rbac_enforced: false,
    route_protection_enforced: false,
    authorization_headers_emitted: false,
    login_ui_available: false,
    logout_ui_available: false,
    user_management_available: false,
    manual_review_action_authority_granted: false,
    water_emergency_action_authority_granted: false,
    principal,
    token_state: {
      token_available: false,
      token_verified: false,
      token_storage_available: false,
      real_token_parsing_enabled: false,
      reason: PHASE_0_DISABLED_AUTH_REASON,
    },
    reason: PHASE_0_DISABLED_AUTH_REASON,
  };
}

export function getFrontendAuthStatus(): FrontendAuthStatus {
  return {
    mode: "disabled",
    provider: "disabled",
    auth_enabled: false,
    login_ui_available: false,
    logout_ui_available: false,
    user_management_available: false,
    authorization_headers_emitted: false,
    future_auth_integration_planned: true,
    reason: PHASE_0_DISABLED_AUTH_REASON,
  };
}

export function currentFrontendPhaseAllowsAuth(): false {
  return false;
}
