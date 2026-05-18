import type {
  DashboardDispatchSummaryResponse,
  DashboardFetchResult,
  DashboardOverviewResponse,
  DispatchLifecycleSummaryResponse,
  ManualReviewSummaryResponse,
  WaterEmergencyDashboardResponse,
  WaterEmergencyDetailResponse
} from "@/lib/dashboard-contracts";
import {
  mockDashboardOverview,
  mockWaterEmergencyDetail,
  mockWaterEmergencyDashboard
} from "@/lib/mock-dashboard";

export const DASHBOARD_ENDPOINTS = {
  overview: "/api/v1/dashboard/overview",
  lifecycle: "/api/v1/dashboard/lifecycle",
  review: "/api/v1/dashboard/review",
  dispatch: "/api/v1/dashboard/dispatch",
  waterEmergency: "/api/v1/dashboard/water-emergency",
  waterEmergencyDetail: (waterEmergencyId: string) =>
    `/api/v1/dashboard/water-emergency/${encodeURIComponent(waterEmergencyId)}`
} as const;

export function dashboardApiBaseUrl(): string | null {
  const rawBaseUrl = process.env.ACS_DASHBOARD_API_BASE_URL?.trim();

  if (!rawBaseUrl) {
    return null;
  }

  return rawBaseUrl.replace(/\/+$/, "");
}

export function dashboardEndpointUrl(path: string): string | null {
  const baseUrl = dashboardApiBaseUrl();

  if (!baseUrl) {
    return null;
  }

  return `${baseUrl}${path}`;
}

export async function getDashboardOverview(): Promise<
  DashboardFetchResult<DashboardOverviewResponse>
> {
  return fetchDashboardReadModel(
    DASHBOARD_ENDPOINTS.overview,
    mockDashboardOverview
  );
}

export async function getDashboardLifecycle(): Promise<
  DashboardFetchResult<DispatchLifecycleSummaryResponse>
> {
  return fetchDashboardReadModel(
    DASHBOARD_ENDPOINTS.lifecycle,
    mockDashboardOverview.lifecycle_summary
  );
}

export async function getDashboardReview(): Promise<
  DashboardFetchResult<ManualReviewSummaryResponse>
> {
  return fetchDashboardReadModel(
    DASHBOARD_ENDPOINTS.review,
    mockDashboardOverview.manual_review_summary
  );
}

export async function getDashboardDispatch(): Promise<
  DashboardFetchResult<DashboardDispatchSummaryResponse>
> {
  return fetchDashboardReadModel(
    DASHBOARD_ENDPOINTS.dispatch,
    mockDashboardOverview.dispatch_summary
  );
}

export async function getDashboardWaterEmergency(): Promise<
  DashboardFetchResult<WaterEmergencyDashboardResponse>
> {
  return fetchDashboardReadModel(
    DASHBOARD_ENDPOINTS.waterEmergency,
    mockWaterEmergencyDashboard
  );
}

export async function getDashboardWaterEmergencyDetail(
  waterEmergencyId: string | null
): Promise<DashboardFetchResult<WaterEmergencyDetailResponse | null>> {
  if (!waterEmergencyId) {
    const baseUrl = dashboardApiBaseUrl();

    return {
      data: null,
      source: baseUrl ? "api" : "mock",
      errorMessage: baseUrl
        ? "No Water Emergency detail record is selected."
        : "No Water Emergency record is available for detail display."
    };
  }

  return fetchWaterEmergencyDetailReadModel(waterEmergencyId);
}

async function fetchDashboardReadModel<T>(
  path: string,
  fallbackData: T
): Promise<DashboardFetchResult<T>> {
  const requestedUrl = dashboardEndpointUrl(path);

  if (!requestedUrl) {
    return {
      data: fallbackData,
      source: "mock",
      errorMessage:
        "ACS_DASHBOARD_API_BASE_URL is not set, so typed local fallback data is displayed."
    };
  }

  try {
    const response = await fetch(requestedUrl, {
      method: "GET",
      cache: "no-store",
      headers: {
        accept: "application/json"
      }
    });

    if (!response.ok) {
      throw new Error(`Dashboard API returned ${response.status}`);
    }

    return {
      data: (await response.json()) as T,
      source: "api",
      requestedUrl
    };
  } catch (error) {
    return {
      data: fallbackData,
      source: "mock",
      requestedUrl,
      errorMessage:
        error instanceof Error
          ? error.message
          : "Dashboard API could not be reached."
    };
  }
}

async function fetchWaterEmergencyDetailReadModel(
  waterEmergencyId: string
): Promise<DashboardFetchResult<WaterEmergencyDetailResponse | null>> {
  const path = DASHBOARD_ENDPOINTS.waterEmergencyDetail(waterEmergencyId);
  const requestedUrl = dashboardEndpointUrl(path);

  if (!requestedUrl) {
    return {
      data: mockWaterEmergencyDetail,
      source: "mock",
      errorMessage:
        "ACS_DASHBOARD_API_BASE_URL is not set, so typed local fallback data is displayed."
    };
  }

  try {
    const response = await fetch(requestedUrl, {
      method: "GET",
      cache: "no-store",
      headers: {
        accept: "application/json"
      }
    });

    if (response.status === 404) {
      return {
        data: null,
        source: "api",
        requestedUrl,
        errorMessage: "Water Emergency detail record was not found."
      };
    }

    if (!response.ok) {
      throw new Error(`Dashboard API returned ${response.status}`);
    }

    return {
      data: (await response.json()) as WaterEmergencyDetailResponse,
      source: "api",
      requestedUrl
    };
  } catch (error) {
    return {
      data: mockWaterEmergencyDetail,
      source: "mock",
      requestedUrl,
      errorMessage:
        error instanceof Error
          ? error.message
          : "Dashboard API could not be reached."
    };
  }
}
