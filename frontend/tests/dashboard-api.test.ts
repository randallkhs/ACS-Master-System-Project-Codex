import { afterEach, describe, expect, it, vi } from "vitest";
import {
  DASHBOARD_ENDPOINTS,
  dashboardEndpointUrl,
  getDashboardDispatch,
  getDashboardLifecycle,
  getDashboardOverview,
  getDashboardReview,
  getDashboardWaterEmergency
} from "@/lib/dashboard-api";
import {
  mockDashboardOverview,
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
    await getDashboardDispatch();
    await getDashboardWaterEmergency();

    const calls = fetchMock.mock.calls.map(([url, init]) => ({
      url: String(url),
      method: init?.method
    }));

    expect(calls).toEqual([
      {
        url: "https://api.acs.example.com/api/v1/dashboard/overview",
        method: "GET"
      },
      {
        url: "https://api.acs.example.com/api/v1/dashboard/lifecycle",
        method: "GET"
      },
      {
        url: "https://api.acs.example.com/api/v1/dashboard/review",
        method: "GET"
      },
      {
        url: "https://api.acs.example.com/api/v1/dashboard/dispatch",
        method: "GET"
      },
      {
        url: "https://api.acs.example.com/api/v1/dashboard/water-emergency",
        method: "GET"
      }
    ]);
  });

  it("returns the typed Water Emergency fallback when the dedicated read model is unavailable", async () => {
    delete process.env.ACS_DASHBOARD_API_BASE_URL;

    const result = await getDashboardWaterEmergency();

    expect(result.source).toBe("mock");
    expect(result.data.open_count).toBe(mockWaterEmergencyDashboard.open_count);
    expect(result.data.records[0].status).toBe("drying_in_progress");
  });
});
