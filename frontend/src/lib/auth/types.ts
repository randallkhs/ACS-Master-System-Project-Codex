export type FrontendAuthMode = "disabled";

export type FrontendAuthProvider = "disabled";

export type FrontendTokenState = {
  token_available: boolean;
  token_verified: boolean;
  token_storage_available: boolean;
  real_token_parsing_enabled: boolean;
  reason: string;
};

export type FrontendAuthPrincipal = {
  subject: string | null;
  email: string | null;
  display_name: string;
  roles: string[];
  permissions: string[];
  authenticated: boolean;
  manual_review_action_authority_granted: boolean;
  water_emergency_action_authority_granted: boolean;
};

export type FrontendAuthSession = {
  mode: FrontendAuthMode;
  provider: FrontendAuthProvider;
  auth_enabled: boolean;
  authenticated: boolean;
  session_available: boolean;
  token_available: boolean;
  token_verified: boolean;
  phase_allows_auth_enforcement: boolean;
  rbac_enforced: boolean;
  route_protection_enforced: boolean;
  authorization_headers_emitted: boolean;
  login_ui_available: boolean;
  logout_ui_available: boolean;
  user_management_available: boolean;
  manual_review_action_authority_granted: boolean;
  water_emergency_action_authority_granted: boolean;
  principal: FrontendAuthPrincipal;
  token_state: FrontendTokenState;
  reason: string;
};

export type DisabledFrontendAuthSession = FrontendAuthSession & {
  mode: "disabled";
  provider: "disabled";
  auth_enabled: false;
  authenticated: false;
  session_available: false;
  token_available: false;
  token_verified: false;
  phase_allows_auth_enforcement: false;
  rbac_enforced: false;
  route_protection_enforced: false;
  authorization_headers_emitted: false;
  login_ui_available: false;
  logout_ui_available: false;
  user_management_available: false;
  manual_review_action_authority_granted: false;
  water_emergency_action_authority_granted: false;
};

export type AnonymousPhase0FrontendPrincipal = FrontendAuthPrincipal & {
  subject: null;
  email: null;
  authenticated: false;
  roles: [];
  permissions: [];
  manual_review_action_authority_granted: false;
  water_emergency_action_authority_granted: false;
};

export type FrontendAuthStatus = {
  mode: FrontendAuthMode;
  provider: FrontendAuthProvider;
  auth_enabled: boolean;
  login_ui_available: boolean;
  logout_ui_available: boolean;
  user_management_available: boolean;
  authorization_headers_emitted: boolean;
  future_auth_integration_planned: boolean;
  reason: string;
};
