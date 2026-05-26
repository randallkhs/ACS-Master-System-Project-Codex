import { afterEach, describe, expect, it, vi } from "vitest";
import {
  DASHBOARD_ENDPOINTS,
  dashboardEndpointUrl,
  getDashboardDispatch,
  getDashboardLifecycle,
  getDashboardManualReviewDetail,
  getDashboardManualReviewQueue,
  getDashboardOverview,
  getDashboardReview,
  getDashboardWaterEmergencyDetail,
  getDashboardWaterEmergency,
  getAuthStatus
} from "@/lib/dashboard-api";
import {
  mockAuthStatus,
  mockDashboardOverview,
  mockManualReviewDetail,
  mockManualReviewQueue,
  mockWaterEmergencyDetail,
  mockWaterEmergencyDashboard
} from "@/lib/mock-dashboard";

const originalApiBaseUrl = process.env.ACS_DASHBOARD_API_BASE_URL;

afterEach(() => {
  process.env.ACS_DASHBOARD_API_BASE_URL = originalApiBaseUrl;
  vi.unstubAllGlobals();
});

describe("dashboard API client", () => {
  it("returns typed fallback data when the API base URL is not configured", async () => {
    delete process.env.ACS_DASHBOARD_API_BASE_URL;

    const result = await getDashboardOverview();

    expect(result.source).toBe("mock");
    expect(result.data.operational_summary.total_jobs).toBe(
      mockDashboardOverview.operational_summary.total_jobs
    );
    expect(result.errorMessage).toContain("ACS_DASHBOARD_API_BASE_URL");
  });

  it("builds read-only dashboard endpoint URLs from environment configuration", () => {
    process.env.ACS_DASHBOARD_API_BASE_URL = "http://127.0.0.1:8000/";

    expect(dashboardEndpointUrl(DASHBOARD_ENDPOINTS.overview)).toBe(
      "http://127.0.0.1:8000/api/v1/dashboard/overview"
    );
    expect(dashboardEndpointUrl(DASHBOARD_ENDPOINTS.waterEmergency)).toBe(
      "http://127.0.0.1:8000/api/v1/dashboard/water-emergency"
    );
    expect(dashboardEndpointUrl(DASHBOARD_ENDPOINTS.manualReviewQueue)).toBe(
      "http://127.0.0.1:8000/api/v1/dashboard/manual-review/queue"
    );
    expect(dashboardEndpointUrl(DASHBOARD_ENDPOINTS.authStatus)).toBe(
      "http://127.0.0.1:8000/api/v1/auth/status"
    );
    expect(
      dashboardEndpointUrl(
        DASHBOARD_ENDPOINTS.manualReviewDetail(
          "41000000-0000-4000-8000-000000000001"
        )
      )
    ).toBe(
      "http://127.0.0.1:8000/api/v1/dashboard/manual-review/queue/41000000-0000-4000-8000-000000000001"
    );
    expect(
      dashboardEndpointUrl(
        DASHBOARD_ENDPOINTS.waterEmergencyDetail(
          "e9acb112-409f-4d4f-b98f-4b61a437c4c7"
        )
      )
    ).toBe(
      "http://127.0.0.1:8000/api/v1/dashboard/water-emergency/e9acb112-409f-4d4f-b98f-4b61a437c4c7"
    );
  });

  it("falls back clearly when the configured backend is unavailable", async () => {
    process.env.ACS_DASHBOARD_API_BASE_URL = "http://127.0.0.1:8000";
    vi.stubGlobal(
      "fetch",
      vi.fn().mockRejectedValue(new Error("connect ECONNREFUSED"))
    );

    const result = await getDashboardOverview();

    expect(result.source).toBe("mock");
    expect(result.requestedUrl).toBe(
      "http://127.0.0.1:8000/api/v1/dashboard/overview"
    );
    expect(result.errorMessage).toBe("connect ECONNREFUSED");
    expect(result.data.operational_summary.total_jobs).toBe(
      mockDashboardOverview.operational_summary.total_jobs
    );
  });

  it("uses GET with no-store caching for live dashboard reads", async () => {
    process.env.ACS_DASHBOARD_API_BASE_URL = "https://api.acs.example.com";
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(JSON.stringify(mockDashboardOverview), {
        status: 200,
        headers: { "content-type": "application/json" }
      })
    );
    vi.stubGlobal("fetch", fetchMock);

    const result = await getDashboardOverview();

    expect(result.source).toBe("api");
    expect(fetchMock).toHaveBeenCalledWith(
      "https://api.acs.example.com/api/v1/dashboard/overview",
      expect.objectContaining({
        method: "GET",
        cache: "no-store"
      })
    );
    const requestInit = fetchMock.mock.calls[0]?.[1] as RequestInit;
    expect(requestInit.headers).toEqual({ accept: "application/json" });
    expect(requestInit.headers).not.toHaveProperty("Authorization");
    expect(requestInit.headers).not.toHaveProperty("authorization");
  });

  it("fetches auth status as a GET-only read with no Authorization header", async () => {
    process.env.ACS_DASHBOARD_API_BASE_URL = "https://api.acs.example.com";
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(JSON.stringify(mockAuthStatus), {
        status: 200,
        headers: { "content-type": "application/json" }
      })
    );
    vi.stubGlobal("fetch", fetchMock);

    const result = await getAuthStatus();

    expect(result.source).toBe("api");
    expect(result.data.auth_enabled).toBe(false);
    expect(result.data.authorization_header_parsed).toBe(false);
    expect(result.data.authorization_header_can_grant_authority).toBe(false);
    expect(fetchMock).toHaveBeenCalledWith(
      "https://api.acs.example.com/api/v1/auth/status",
      expect.objectContaining({
        method: "GET",
        cache: "no-store"
      })
    );
    const requestInit = fetchMock.mock.calls[0]?.[1] as RequestInit;
    expect(requestInit.headers).toEqual({ accept: "application/json" });
    expect(requestInit.headers).not.toHaveProperty("Authorization");
    expect(requestInit.headers).not.toHaveProperty("authorization");
  });

  it("returns a disabled auth-status fallback without reporting auth success", async () => {
    process.env.ACS_DASHBOARD_API_BASE_URL = "http://127.0.0.1:8000";
    vi.stubGlobal(
      "fetch",
      vi.fn().mockRejectedValue(new Error("connect ECONNREFUSED"))
    );

    const result = await getAuthStatus();

    expect(result.source).toBe("mock");
    expect(result.data.auth_enabled).toBe(false);
    expect(result.data.token_verification_enabled).toBe(false);
    expect(result.data.rbac_enforcement_enabled).toBe(false);
    expect(result.data.authorization_header_required).toBe(false);
    expect(result.data.authorization_header_parsed).toBe(false);
    expect(result.data.manual_review_action_authority_granted).toBe(false);
    expect(result.data.water_emergency_action_authority_granted).toBe(false);
    expect(result.errorMessage).toBe("connect ECONNREFUSED");
  });

  it("keeps all dashboard client helpers read-only", async () => {
    process.env.ACS_DASHBOARD_API_BASE_URL = "https://api.acs.example.com";
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(JSON.stringify(mockDashboardOverview), {
        status: 200,
        headers: { "content-type": "application/json" }
      })
    );
    vi.stubGlobal("fetch", fetchMock);

    await getDashboardOverview();
    await getDashboardLifecycle();
    await getDashboardReview();
    await getDashboardManualReviewQueue();
    await getDashboardManualReviewDetail(
      "41000000-0000-4000-8000-000000000001"
    );
    await getDashboardDispatch();
    await getDashboardWaterEmergency();
    await getDashboardWaterEmergencyDetail(
      "e9acb112-409f-4d4f-b98f-4b61a437c4c7"
    );
    await getAuthStatus();

    const calls = fetchMock.mock.calls.map(([url, init]) => ({
      url: String(url),
      method: init?.method,
      headers: init?.headers
    }));

    expect(calls).toEqual([
      {
        url: "https://api.acs.example.com/api/v1/dashboard/overview",
        method: "GET",
        headers: { accept: "application/json" }
      },
      {
        url: "https://api.acs.example.com/api/v1/dashboard/lifecycle",
        method: "GET",
        headers: { accept: "application/json" }
      },
      {
        url: "https://api.acs.example.com/api/v1/dashboard/review",
        method: "GET",
        headers: { accept: "application/json" }
      },
      {
        url: "https://api.acs.example.com/api/v1/dashboard/manual-review/queue",
        method: "GET",
        headers: { accept: "application/json" }
      },
      {
        url: "https://api.acs.example.com/api/v1/dashboard/manual-review/queue/41000000-0000-4000-8000-000000000001",
        method: "GET",
        headers: { accept: "application/json" }
      },
      {
        url: "https://api.acs.example.com/api/v1/dashboard/dispatch",
        method: "GET",
        headers: { accept: "application/json" }
      },
      {
        url: "https://api.acs.example.com/api/v1/dashboard/water-emergency",
        method: "GET",
        headers: { accept: "application/json" }
      },
      {
        url: "https://api.acs.example.com/api/v1/dashboard/water-emergency/e9acb112-409f-4d4f-b98f-4b61a437c4c7",
        method: "GET",
        headers: { accept: "application/json" }
      },
      {
        url: "https://api.acs.example.com/api/v1/auth/status",
        method: "GET",
        headers: { accept: "application/json" }
      }
    ]);
    calls.forEach((call) => {
      expect(call.headers).not.toHaveProperty("Authorization");
      expect(call.headers).not.toHaveProperty("authorization");
    });
  });

  it("returns the typed Water Emergency fallback when the dedicated read model is unavailable", async () => {
    delete process.env.ACS_DASHBOARD_API_BASE_URL;

    const result = await getDashboardWaterEmergency();

    expect(result.source).toBe("mock");
    expect(result.data.open_count).toBe(mockWaterEmergencyDashboard.open_count);
    expect(result.data.records[0].status).toBe("drying_in_progress");
  });

  it("returns the typed Manual Review queue fallback when the queue read model is unavailable", async () => {
    delete process.env.ACS_DASHBOARD_API_BASE_URL;

    const result = await getDashboardManualReviewQueue();

    expect(result.source).toBe("mock");
    expect(result.data.total_items).toBe(mockManualReviewQueue.total_items);
    expect(result.data.items[0].reason_code).toBe("missing_customer_data");
    expect(result.data.command_validation_counts[0].label).toBe(
      "validation_warning_requires_review"
    );
    expect(result.data.permission_readiness_counts[0].label).toBe(
      "permission_ready_for_future_auth_phase"
    );
    expect(result.data.items[0].command_validation.phase_allows_execution).toBe(
      false
    );
    expect(result.data.items[0].permission_readiness.phase_allows_execution).toBe(
      false
    );
    expect(
      result.data.items[0].permission_readiness.future_operator_identity_required
    ).toBe(true);
    expect(
      result.data.items[0].permission_readiness.future_role_authorization_required
    ).toBe(true);
    expect(result.data.items[0].permission_readiness.service_account_allowed).toBe(
      false
    );
    expect(result.data.auth_boundary_readiness.auth_implemented).toBe(false);
    expect(result.data.auth_boundary_readiness.rbac_enforced).toBe(false);
    expect(result.data.auth_boundary_readiness.action_execution_available).toBe(
      false
    );
    expect(
      result.data.auth_boundary_readiness.service_accounts_blocked_for_manual_review_actions
    ).toBe(true);
    expect(
      result.data.auth_boundary_readiness.provisional_roles.some(
        (role) => role.key === "system_service" && role.is_service_account_role
      )
    ).toBe(true);
    expect(
      result.data.auth_boundary_readiness.future_permissions.some(
        (permission) =>
          permission.key === "manual_review.approve.future" &&
          permission.authorizes_actions_now === false
      )
    ).toBe(true);
    expect(
      result.data.auth_boundary_readiness.auth_configuration_readiness
        .auth_provider_configured
    ).toBe(false);
    expect(
      result.data.auth_boundary_readiness.auth_configuration_readiness
        .auth_provider
    ).toBe("disabled");
    expect(
      result.data.auth_boundary_readiness.auth_configuration_readiness
        .token_verification_enabled
    ).toBe(false);
    expect(
      result.data.auth_boundary_readiness.auth_configuration_readiness
        .committed_credentials_allowed
    ).toBe(false);
    expect(
      result.data.auth_boundary_readiness.auth_configuration_readiness
        .runtime_safety_diagnostics.auth_enabled
    ).toBe(false);
    expect(
      result.data.auth_boundary_readiness.auth_configuration_readiness
        .runtime_safety_diagnostics.auth_headers_required
    ).toBe(false);
    expect(
      result.data.auth_boundary_readiness.auth_configuration_readiness
        .runtime_safety_diagnostics.auth_headers_emitted_by_frontend
    ).toBe(false);
    expect(
      result.data.auth_boundary_readiness.auth_configuration_readiness
        .runtime_safety_diagnostics.service_account_json_tracked
    ).toBe(false);
    expect(
      result.data.auth_boundary_readiness.auth_configuration_readiness
        .runtime_safety_diagnostics.env_file_tracked
    ).toBe(false);
    expect(
      result.data.auth_boundary_readiness.auth_configuration_readiness
        .runtime_safety_diagnostics.env_local_file_tracked
    ).toBe(false);
    expect(
      result.data.auth_boundary_readiness.auth_configuration_readiness
        .runtime_safety_diagnostics.private_key_detected
    ).toBe(false);
    expect(
      result.data.auth_boundary_readiness.auth_configuration_readiness
        .runtime_safety_diagnostics.placeholder_values_only
    ).toBe(true);
    expect(
      result.data.auth_boundary_readiness.auth_configuration_readiness
        .runtime_safety_diagnostics.diagnostic_checks.some(
          (check) => check.key === "frontend_auth_headers_not_emitted" && check.passed
        )
    ).toBe(true);
    expect(
      result.data.auth_boundary_readiness.auth_configuration_readiness.backend_variables.some(
        (variable) =>
          variable.name === "ACS_FSM_AUTH_PROVIDER" &&
          variable.safe_placeholder === "disabled"
      )
    ).toBe(true);
    expect(
      result.data.auth_boundary_readiness.auth_configuration_readiness.frontend_variables.some(
        (variable) =>
          variable.name === "NEXT_PUBLIC_ACS_AUTH_ENABLED" &&
          variable.safe_placeholder === "false"
      )
    ).toBe(true);
    expect(
      result.data.auth_boundary_readiness.auth_claims_mapping_readiness
        .token_verification_dry_run_available
    ).toBe(true);
    expect(
      result.data.auth_boundary_readiness.auth_claims_mapping_readiness
        .token_verification_enabled
    ).toBe(false);
    expect(
      result.data.auth_boundary_readiness.auth_claims_mapping_readiness
        .real_token_parsing_enabled
    ).toBe(false);
    expect(
      result.data.auth_boundary_readiness.auth_claims_mapping_readiness
        .jwks_fetch_enabled
    ).toBe(false);
    expect(
      result.data.auth_boundary_readiness.auth_claims_mapping_readiness
        .auth_headers_required
    ).toBe(false);
    expect(
      result.data.auth_boundary_readiness.auth_claims_mapping_readiness
        .auth_headers_emitted_by_frontend
    ).toBe(false);
    expect(
      result.data.auth_boundary_readiness.auth_claims_mapping_readiness
        .required_claims_documented
    ).toBe(true);
    expect(
      result.data.auth_boundary_readiness.auth_claims_mapping_readiness
        .service_account_block_rule_documented
    ).toBe(true);
    expect(
      result.data.auth_boundary_readiness.auth_claims_mapping_readiness
        .technician_block_rule_documented
    ).toBe(true);
    expect(
      result.data.auth_boundary_readiness.auth_claims_mapping_readiness.claim_contracts.some(
        (claim) => claim.key === "subject" && claim.claim_name === "sub"
      )
    ).toBe(true);
    expect(
      result.data.auth_boundary_readiness.auth_claims_mapping_readiness.role_resolution_rules.some(
        (rule) =>
          rule.key === "unknown_role_maps_to_unknown_operator" &&
          rule.resolved_role === "unknown_operator" &&
          rule.blocked_for_manual_review_actions
      )
    ).toBe(true);
    expect(
      result.data.auth_boundary_readiness.auth_claims_mapping_readiness.example_claim_fixtures.some(
        (fixture) =>
          fixture.key === "phase0_example_operator_claims" &&
          fixture.email_domain === "example.com" &&
          fixture.contains_token === false
      )
    ).toBe(true);
    expect(
      result.data.auth_boundary_readiness.route_protection_readiness
        .access_decision_dry_run.enforcement_enabled
    ).toBe(false);
    expect(
      result.data.auth_boundary_readiness.route_protection_readiness
        .access_decision_dry_run.phase_allows_enforcement
    ).toBe(false);
    expect(
      result.data.auth_boundary_readiness.route_protection_readiness
        .access_decision_dry_run.route_guarding_enabled
    ).toBe(false);
    expect(
      result.data.auth_boundary_readiness.route_protection_readiness.matrix_items.some(
        (item) =>
          item.route_or_section_key === "api_manual_review_queue" &&
          item.future_required_permissions.includes("manual_review.view") &&
          item.enforcement_enabled === false
      )
    ).toBe(true);
    expect(
      result.data.auth_boundary_readiness.route_protection_readiness.matrix_items.some(
        (item) =>
          item.route_or_section_key === "api_water_emergency_dashboard" &&
          item.future_required_permissions.includes("water_emergency.view") &&
          item.water_emergency_sensitive
      )
    ).toBe(true);
    expect(
      result.data.auth_boundary_readiness.route_protection_readiness.matrix_items.some(
        (item) =>
          item.route_or_section_key === "future_manual_review_action_execution" &&
          item.type === "future_action" &&
          item.currently_public_in_phase_0 === false &&
          item.mutation_sensitive &&
          item.phase_allows_enforcement === false
      )
    ).toBe(true);
    expect(
      result.data.auth_boundary_readiness.auth_rbac_readiness_audit
        .auth_implemented
    ).toBe(false);
    expect(
      result.data.auth_boundary_readiness.auth_rbac_readiness_audit
        .auth_enabled
    ).toBe(false);
    expect(
      result.data.auth_boundary_readiness.auth_rbac_readiness_audit
        .token_verification_enabled
    ).toBe(false);
    expect(
      result.data.auth_boundary_readiness.auth_rbac_readiness_audit
        .real_token_parsing_enabled
    ).toBe(false);
    expect(
      result.data.auth_boundary_readiness.auth_rbac_readiness_audit
        .jwks_fetch_enabled
    ).toBe(false);
    expect(
      result.data.auth_boundary_readiness.auth_rbac_readiness_audit
        .rbac_enforced
    ).toBe(false);
    expect(
      result.data.auth_boundary_readiness.auth_rbac_readiness_audit
        .route_guarding_enabled
    ).toBe(false);
    expect(
      result.data.auth_boundary_readiness.auth_rbac_readiness_audit
        .manual_review_action_execution_available
    ).toBe(false);
    expect(
      result.data.auth_boundary_readiness.auth_rbac_readiness_audit
        .water_emergency_action_execution_available
    ).toBe(false);
    expect(
      result.data.auth_boundary_readiness.auth_rbac_readiness_audit
        .auth_core_module_available
    ).toBe(true);
    expect(
      result.data.auth_boundary_readiness.auth_rbac_readiness_audit
        .disabled_token_verifier_available
    ).toBe(true);
    expect(
      result.data.auth_boundary_readiness.auth_rbac_readiness_audit
        .optional_auth_context_available
    ).toBe(true);
    expect(
      result.data.auth_boundary_readiness.auth_rbac_readiness_audit
        .token_verification_result
    ).toBe("disabled");
    expect(
      result.data.auth_boundary_readiness.auth_rbac_readiness_audit
        .current_routes_require_auth
    ).toBe(false);
    expect(
      result.data.auth_boundary_readiness.auth_rbac_readiness_audit
        .manual_review_action_authority_granted
    ).toBe(false);
    expect(
      result.data.auth_boundary_readiness.auth_rbac_readiness_audit
        .water_emergency_action_authority_granted
    ).toBe(false);
    expect(
      result.data.auth_boundary_readiness.auth_rbac_readiness_audit
        .enforcement_boundary_lock.phase_allows_auth_enforcement
    ).toBe(false);
    expect(
      result.data.auth_boundary_readiness.auth_rbac_readiness_audit
        .enforcement_boundary_lock.phase_allows_rbac_enforcement
    ).toBe(false);
    expect(
      result.data.auth_boundary_readiness.auth_rbac_readiness_audit
        .enforcement_boundary_lock.phase_allows_route_guarding
    ).toBe(false);
    expect(
      result.data.auth_boundary_readiness.auth_rbac_readiness_audit
        .future_transition_prerequisites.some(
          (prerequisite) =>
            prerequisite.key === "provider_selected_by_randall" &&
            prerequisite.status === "blocked_by_provider_selection"
        )
    ).toBe(true);
    expect(
      result.data.auth_boundary_readiness.auth_rbac_readiness_audit
        .future_transition_prerequisites.some(
          (prerequisite) =>
            prerequisite.key === "secret_hygiene_check_included_in_verification" &&
            prerequisite.status === "satisfied_now"
        )
    ).toBe(true);
    expect(
      result.data.auth_boundary_readiness.auth_rbac_readiness_audit
        .future_transition_prerequisites.some(
          (prerequisite) =>
            prerequisite.key === "water_emergency_action_permissions_approved" &&
            prerequisite.requires_alfonso_owner_review
        )
    ).toBe(true);
    expect(
      result.data.items[0].command_validation.safety_gates.at(-1)?.key
    ).toBe("phase_allows_execution");
    expect(result.data.taxonomy_metadata.randall_authorized_phase_0_baseline).toBe(
      true
    );
  });

  it("returns typed Manual Review detail fallback when the detail read model is unavailable", async () => {
    delete process.env.ACS_DASHBOARD_API_BASE_URL;

    const result = await getDashboardManualReviewDetail(
      "41000000-0000-4000-8000-000000000001"
    );

    expect(result.source).toBe("mock");
    expect(result.data?.review_item.review_item_id).toBe(
      mockManualReviewDetail.review_item.review_item_id
    );
    expect(result.data?.linked_entity_context.is_dispatch_related).toBe(true);
    expect(result.data?.command_validation.is_currently_executable).toBe(false);
    expect(result.data?.permission_readiness.is_currently_executable).toBe(false);
    expect(result.data?.permission_readiness.phase_allows_execution).toBe(false);
    expect(result.data?.command_validation.safety_gates.at(-1)?.key).toBe(
      "phase_allows_execution"
    );
  });

  it("keeps no-selected Manual Review detail as live null data when an API base URL is configured", async () => {
    process.env.ACS_DASHBOARD_API_BASE_URL = "https://api.acs.example.com";

    const result = await getDashboardManualReviewDetail(null);

    expect(result.source).toBe("api");
    expect(result.data).toBeNull();
    expect(result.errorMessage).toBe("No Manual Review detail record is selected.");
  });

  it("returns a live null result when the Manual Review detail record is not found", async () => {
    process.env.ACS_DASHBOARD_API_BASE_URL = "https://api.acs.example.com";
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(JSON.stringify({ detail: "Manual Review item not found" }), {
        status: 404,
        headers: { "content-type": "application/json" }
      })
    );
    vi.stubGlobal("fetch", fetchMock);

    const result = await getDashboardManualReviewDetail("missing-review");

    expect(result.source).toBe("api");
    expect(result.data).toBeNull();
    expect(result.data).not.toBe(mockManualReviewDetail);
    expect(result.errorMessage).toBe("Manual Review detail record was not found.");
    expect(fetchMock).toHaveBeenCalledWith(
      "https://api.acs.example.com/api/v1/dashboard/manual-review/queue/missing-review",
      expect.objectContaining({
        method: "GET",
        cache: "no-store"
      })
    );
  });

  it("returns typed Water Emergency detail fallback when the detail read model is unavailable", async () => {
    delete process.env.ACS_DASHBOARD_API_BASE_URL;

    const result = await getDashboardWaterEmergencyDetail(
      "e9acb112-409f-4d4f-b98f-4b61a437c4c7"
    );

    expect(result.source).toBe("mock");
    expect(result.data?.record.water_emergency_id).toBe(
      mockWaterEmergencyDetail.record.water_emergency_id
    );
    expect(result.data?.timeline_summary.entries[0].event_type).toBe(
      "water_emergency.extraction_started"
    );
  });

  it("keeps no-selected Water Emergency detail as live null data when an API base URL is configured", async () => {
    process.env.ACS_DASHBOARD_API_BASE_URL = "https://api.acs.example.com";

    const result = await getDashboardWaterEmergencyDetail(null);

    expect(result.source).toBe("api");
    expect(result.data).toBeNull();
    expect(result.errorMessage).toBe(
      "No Water Emergency detail record is selected."
    );
  });

  it("returns a live null result when the Water Emergency detail record is not found", async () => {
    process.env.ACS_DASHBOARD_API_BASE_URL = "https://api.acs.example.com";
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(JSON.stringify({ detail: "Water Emergency record not found" }), {
        status: 404,
        headers: { "content-type": "application/json" }
      })
    );
    vi.stubGlobal("fetch", fetchMock);

    const result = await getDashboardWaterEmergencyDetail(
      "missing-water-emergency"
    );

    expect(result.source).toBe("api");
    expect(result.data).toBeNull();
    expect(result.data).not.toBe(mockWaterEmergencyDetail);
    expect(result.errorMessage).toBe(
      "Water Emergency detail record was not found."
    );
    expect(fetchMock).toHaveBeenCalledWith(
      "https://api.acs.example.com/api/v1/dashboard/water-emergency/missing-water-emergency",
      expect.objectContaining({
        method: "GET",
        cache: "no-store"
      })
    );
  });
});
