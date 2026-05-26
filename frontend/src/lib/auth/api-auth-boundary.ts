import { getDisabledFrontendAuthSession } from "@/lib/auth/session";

export type FrontendAuthHeaders = Record<string, string>;

export type FrontendApiAuthBoundaryReadiness = {
  authorization_headers_emitted: boolean;
  api_client_authenticated: boolean;
  token_available: boolean;
  session_available: boolean;
  future_auth_header_integration_planned: boolean;
  reason: string;
};

export function frontendAuthHeadersForRequest(): FrontendAuthHeaders {
  return {};
}

export function getFrontendApiAuthBoundaryReadiness(): FrontendApiAuthBoundaryReadiness {
  const session = getDisabledFrontendAuthSession();

  return {
    authorization_headers_emitted: false,
    api_client_authenticated: false,
    token_available: session.token_available,
    session_available: session.session_available,
    future_auth_header_integration_planned: true,
    reason:
      "Dashboard API reads remain unauthenticated in Phase 0. The frontend auth boundary does not emit Authorization headers.",
  };
}
