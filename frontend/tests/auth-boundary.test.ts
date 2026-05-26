import { describe, expect, it } from "vitest";
import {
  currentFrontendPhaseAllowsAuth,
  frontendAuthHeadersForRequest,
  getAnonymousPhase0Principal,
  getDisabledFrontendAuthSession,
  getFrontendAuthStatus,
} from "@/lib/auth";

describe("frontend auth boundary", () => {
  it("reports a disabled anonymous Phase 0 session", () => {
    const session = getDisabledFrontendAuthSession();

    expect(session.auth_enabled).toBe(false);
    expect(session.authenticated).toBe(false);
    expect(session.session_available).toBe(false);
    expect(session.token_available).toBe(false);
    expect(session.token_verified).toBe(false);
    expect(session.phase_allows_auth_enforcement).toBe(false);
    expect(session.rbac_enforced).toBe(false);
    expect(session.route_protection_enforced).toBe(false);
    expect(session.manual_review_action_authority_granted).toBe(false);
    expect(session.water_emergency_action_authority_granted).toBe(false);
    expect(session.principal.authenticated).toBe(false);
    expect(session.principal.roles).toEqual([]);
    expect(session.principal.permissions).toEqual([]);
  });

  it("keeps the anonymous principal non-authoritative", () => {
    const principal = getAnonymousPhase0Principal();

    expect(principal.subject).toBeNull();
    expect(principal.email).toBeNull();
    expect(principal.authenticated).toBe(false);
    expect(principal.roles).toEqual([]);
    expect(principal.permissions).toEqual([]);
    expect(principal.manual_review_action_authority_granted).toBe(false);
    expect(principal.water_emergency_action_authority_granted).toBe(false);
  });

  it("returns no authorization headers for Phase 0 API reads", () => {
    const headers = frontendAuthHeadersForRequest();

    expect(headers).toEqual({});
    expect("Authorization" in headers).toBe(false);
    expect("authorization" in headers).toBe(false);
  });

  it("reports frontend auth status as disabled and non-enforcing", () => {
    const status = getFrontendAuthStatus();

    expect(status.auth_enabled).toBe(false);
    expect(status.login_ui_available).toBe(false);
    expect(status.logout_ui_available).toBe(false);
    expect(status.user_management_available).toBe(false);
    expect(status.authorization_headers_emitted).toBe(false);
    expect(status.future_auth_integration_planned).toBe(true);
    expect(currentFrontendPhaseAllowsAuth()).toBe(false);
  });
});
