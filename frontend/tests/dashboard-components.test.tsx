import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";
import { DashboardView } from "@/components/dashboard/dashboard-view";
import { mockDashboardOverview } from "@/lib/mock-dashboard";

describe("DashboardView", () => {
  it("renders the read-only dashboard shell and key operational sections", () => {
    const html = renderToStaticMarkup(
      <DashboardView
        result={{
          data: mockDashboardOverview,
          source: "mock",
          errorMessage: "Fallback state for component smoke testing."
        }}
      />
    );

    expect(html).toContain("Operational Control View");
    expect(html).toContain("Read-only operational dashboard");
    expect(html).toContain("Safety signals and readiness");
    expect(html).toContain("Manual Review");
    expect(html).toContain("Water Emergency");
    expect(html).toContain("Operational Event Timeline");
  });

  it("does not render operational action buttons or mutation controls", () => {
    const html = renderToStaticMarkup(
      <DashboardView
        result={{
          data: mockDashboardOverview,
          source: "mock"
        }}
      />
    );

    expect(html).not.toMatch(/<button|role="button"/);
    expect(html).not.toContain("Resolve review");
    expect(html).not.toContain("Dispatch now");
    expect(html).not.toContain("Execute dispatch");
    expect(html).not.toContain("Run integration");
  });

  it("labels successful backend reads as live backend data", () => {
    const html = renderToStaticMarkup(
      <DashboardView
        result={{
          data: mockDashboardOverview,
          source: "api",
          requestedUrl: "http://127.0.0.1:8000/api/v1/dashboard/overview"
        }}
      />
    );

    expect(html).toContain("Live backend");
    expect(html).not.toContain("Mock fallback");
  });
});
