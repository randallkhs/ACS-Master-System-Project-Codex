import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";
import { DashboardView } from "@/components/dashboard/dashboard-view";
import { ScenarioStoryboard } from "@/components/dashboard/scenario-storyboard";
import {
  mockDashboardOverview,
  mockWaterEmergencyDashboard
} from "@/lib/mock-dashboard";

const mockWaterEmergencyResult = {
  data: mockWaterEmergencyDashboard,
  source: "mock" as const
};

describe("DashboardView", () => {
  it("renders the read-only dashboard shell and key operational sections", () => {
    const html = renderToStaticMarkup(
      <DashboardView
        result={{
          data: mockDashboardOverview,
          source: "mock",
          errorMessage: "Fallback state for component smoke testing."
        }}
        waterEmergencyResult={mockWaterEmergencyResult}
      />
    );

    expect(html).toContain("Operational Control View");
    expect(html).toContain("Read-only operational dashboard");
    expect(html).toContain("Safety signals and readiness");
    expect(html).toContain("Scenario Storyboard");
    expect(html).toContain("Water Emergency Command View");
    expect(html).toContain("Standard dispatch-ready work");
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
        waterEmergencyResult={mockWaterEmergencyResult}
      />
    );

    expect(html).not.toMatch(/<button|role="button"/);
    expect(html).not.toContain("Resolve review");
    expect(html).not.toContain("Dispatch now");
    expect(html).not.toContain("Execute dispatch");
    expect(html).not.toContain("Run integration");
    expect(html).not.toContain("Replay now");
    expect(html).not.toContain("Rollback now");
  });

  it("labels successful backend reads as live backend data", () => {
    const html = renderToStaticMarkup(
      <DashboardView
        result={{
          data: mockDashboardOverview,
          source: "api",
          requestedUrl: "http://127.0.0.1:8000/api/v1/dashboard/overview"
        }}
        waterEmergencyResult={{
          data: mockWaterEmergencyDashboard,
          source: "api",
          requestedUrl:
            "http://127.0.0.1:8000/api/v1/dashboard/water-emergency"
        }}
      />
    );

    expect(html).toContain("Live backend");
    expect(html).toContain("Live backend read models");
    expect(html).not.toContain("Mock fallback");
  });

  it("keeps Water Emergency visually separated from standard dispatch scenarios", () => {
    const html = renderToStaticMarkup(
      <DashboardView
        result={{
          data: mockDashboardOverview,
          source: "mock"
        }}
        waterEmergencyResult={mockWaterEmergencyResult}
      />
    );

    expect(html).toContain("Water Emergency separated path");
    expect(html).toContain("Water Emergency Command View");
    expect(html).toContain("Dedicated Water Emergency visibility");
    expect(html).toContain("first-class separated operational path");
    expect(html).toContain("Standard dispatch-ready work");
  });

  it("renders timeline events in stable read-model order", () => {
    const html = renderToStaticMarkup(
      <DashboardView
        result={{
          data: mockDashboardOverview,
          source: "mock"
        }}
        waterEmergencyResult={mockWaterEmergencyResult}
      />
    );
    const timelineStart = html.indexOf("Operational Event Timeline");
    const firstEvent = html.indexOf(
      "Operational Accountability Escalation Required",
      timelineStart
    );
    const laterEvent = html.indexOf(
      "Operational Intake Water Emergency Separated",
      timelineStart
    );

    expect(timelineStart).toBeGreaterThan(-1);
    expect(firstEvent).toBeGreaterThan(-1);
    expect(laterEvent).toBeGreaterThan(firstEvent);
  });

  it("counts capitalized Water Emergency review labels in the storyboard metric", () => {
    const html = renderToStaticMarkup(
      <ScenarioStoryboard
        data={{
          ...mockDashboardOverview,
          manual_review_summary: {
            ...mockDashboardOverview.manual_review_summary,
            reason_counts: [
              { label: "Water Emergency", count: 7 },
              { label: "Address Validation", count: 3 }
            ]
          }
        }}
        source="mock"
      />
    );

    expect(html).toContain("Water Emergency separated path");
    expect(html).toMatch(/<dt[^>]*>Review<\/dt><dd[^>]*><span[^>]*>7<\/span>/);
  });

  it("does not render Water Emergency mutation or workflow controls", () => {
    const html = renderToStaticMarkup(
      <DashboardView
        result={{
          data: mockDashboardOverview,
          source: "mock"
        }}
        waterEmergencyResult={mockWaterEmergencyResult}
      />
    );

    expect(html).toContain("Read-only Water Emergency visibility");
    expect(html).not.toContain("Close Water Emergency");
    expect(html).not.toContain("Resolve Water Emergency");
    expect(html).not.toContain("Dispatch Water Emergency");
    expect(html).not.toContain("Approve Water Emergency");
  });
});
