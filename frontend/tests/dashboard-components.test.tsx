import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";
import { DashboardView } from "@/components/dashboard/dashboard-view";
import { ScenarioStoryboard } from "@/components/dashboard/scenario-storyboard";
import {
  mockDashboardOverview,
  mockWaterEmergencyDetail,
  mockWaterEmergencyDashboard
} from "@/lib/mock-dashboard";

const mockWaterEmergencyResult = {
  data: mockWaterEmergencyDashboard,
  source: "mock" as const
};

const mockWaterEmergencyDetailResult = {
  data: mockWaterEmergencyDetail,
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
        waterEmergencyDetailResult={mockWaterEmergencyDetailResult}
      />
    );

    expect(html).toContain("Operational Control View");
    expect(html).toContain("Read-only operational dashboard");
    expect(html).toContain("Safety signals and readiness");
    expect(html).toContain("Scenario Storyboard");
    expect(html).toContain("Water Emergency Command View");
    expect(html).toContain("Water Emergency Detail");
    expect(html).toContain("Evidence Timeline");
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
        waterEmergencyDetailResult={mockWaterEmergencyDetailResult}
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
        waterEmergencyDetailResult={{
          data: mockWaterEmergencyDetail,
          source: "api",
          requestedUrl:
            "http://127.0.0.1:8000/api/v1/dashboard/water-emergency/e9acb112-409f-4d4f-b98f-4b61a437c4c7"
        }}
      />
    );

    expect(html).toContain("Live backend");
    expect(html).toContain("Live backend read models");
    expect(html).not.toContain("Mock fallback");
  });

  it("keeps live backend status when no Water Emergency detail is selected", () => {
    const html = renderToStaticMarkup(
      <DashboardView
        result={{
          data: mockDashboardOverview,
          source: "api",
          requestedUrl: "http://127.0.0.1:8000/api/v1/dashboard/overview"
        }}
        waterEmergencyResult={{
          data: {
            ...mockWaterEmergencyDashboard,
            open_count: 0,
            total_records: 0,
            records: []
          },
          source: "api",
          requestedUrl:
            "http://127.0.0.1:8000/api/v1/dashboard/water-emergency"
        }}
        waterEmergencyDetailResult={{
          data: null,
          source: "api",
          errorMessage: "No Water Emergency record is available for detail display."
        }}
      />
    );

    expect(html).toContain("Live backend");
    expect(html).toContain("No Water Emergency detail selected");
    expect(html).not.toContain("Mock fallback");
    expect(html).not.toMatch(/<button|role="button"/);
    expect(html).not.toContain("Close Water Emergency");
    expect(html).not.toContain("Resolve Water Emergency");
    expect(html).not.toContain("Dispatch Water Emergency");
    expect(html).not.toContain("Approve Water Emergency");
  });

  it("keeps Water Emergency visually separated from standard dispatch scenarios", () => {
    const html = renderToStaticMarkup(
      <DashboardView
        result={{
          data: mockDashboardOverview,
          source: "mock"
        }}
        waterEmergencyResult={mockWaterEmergencyResult}
        waterEmergencyDetailResult={mockWaterEmergencyDetailResult}
      />
    );

    expect(html).toContain("Water Emergency separated path");
    expect(html).toContain("Water Emergency Command View");
    expect(html).toContain("Dedicated Water Emergency visibility");
    expect(html).toContain("first-class separated operational path");
    expect(html).toContain("Standard dispatch-ready work");
  });

  it("renders Water Emergency equipment, visit-chain, and drying-stage visibility", () => {
    const html = renderToStaticMarkup(
      <DashboardView
        result={{
          data: mockDashboardOverview,
          source: "mock"
        }}
        waterEmergencyResult={mockWaterEmergencyResult}
        waterEmergencyDetailResult={mockWaterEmergencyDetailResult}
      />
    );

    expect(html).toContain("Equipment Context");
    expect(html).toContain("Visit Chain");
    expect(html).toContain("Drying Stage Visibility");
    expect(html).toContain("Detail Equipment Context");
    expect(html).toContain("Detail Visit Chain");
    expect(html).toContain("Detail Drying Stage");
    expect(html).toContain("Equipment Inventory Not Modeled");
    expect(html).not.toMatch(/<button|role="button"/);
  });

  it("renders timeline events in stable read-model order", () => {
    const html = renderToStaticMarkup(
      <DashboardView
        result={{
          data: mockDashboardOverview,
          source: "mock"
        }}
        waterEmergencyResult={mockWaterEmergencyResult}
        waterEmergencyDetailResult={mockWaterEmergencyDetailResult}
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
        waterEmergencyDetailResult={mockWaterEmergencyDetailResult}
      />
    );

    expect(html).toContain("Read-only Water Emergency visibility");
    expect(html).toContain("Read-only detail visibility");
    expect(html).not.toContain("Close Water Emergency");
    expect(html).not.toContain("Resolve Water Emergency");
    expect(html).not.toContain("Dispatch Water Emergency");
    expect(html).not.toContain("Approve Water Emergency");
    expect(html).not.toContain("Create Water Emergency");
    expect(html).not.toContain("Edit Water Emergency");
  });

  it("renders Water Emergency detail evidence separately from standard dispatch", () => {
    const html = renderToStaticMarkup(
      <DashboardView
        result={{
          data: mockDashboardOverview,
          source: "mock"
        }}
        waterEmergencyResult={mockWaterEmergencyResult}
        waterEmergencyDetailResult={mockWaterEmergencyDetailResult}
      />
    );

    expect(html).toContain("Water Emergency Detail");
    expect(html).toContain("Focused read-only record");
    expect(html).toContain("Related Work Orders");
    expect(html).toContain("Related Visits");
    expect(html).toContain("Scoped Manual Review");
    expect(html).toContain("Water Emergency Extraction Started");
    expect(html).toContain("Separated from standard dispatch");
  });
});
