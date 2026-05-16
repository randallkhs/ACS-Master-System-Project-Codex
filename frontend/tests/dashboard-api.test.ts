import { afterEach, describe, expect, it, vi } from "vitest";
import {
  DASHBOARD_ENDPOINTS,
  dashboardEndpointUrl,
  getDashboardDispatch,
  getDashboardLifecycle,
  getDashboardOverview,
  getDashboardReview
} from "@/lib/dashboard-api";
import { mockDashboardOverview } from "@/lib/mock-dashboard";

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
    process.env.ACS_DASHBOARD_API_BASE_URL = "https://api.acs.example.com/";

    expect(dashboardEndpointUrl(DASHBOARD_ENDPOINTS.overview)).toBe(
      "https://api.acs.example.com/api/v1/dashboard/overview"
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
      }
    ]);
  });
});
