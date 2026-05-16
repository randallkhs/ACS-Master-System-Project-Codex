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
    expect(html).toContain("Manual Review");
    expect(html).toContain("Water Emergency");
    expect(html).toContain("Operational Event Timeline");
  });
});
