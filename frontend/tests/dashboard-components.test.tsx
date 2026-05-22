import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";
import { DashboardView } from "@/components/dashboard/dashboard-view";
import { ScenarioStoryboard } from "@/components/dashboard/scenario-storyboard";
import {
  mockDashboardOverview,
  mockWaterEmergencyDetail,
  mockWaterEmergencyDashboard
} from "@/lib/mock-dashboard";
import type {
  WaterEmergencyAgingFollowUpItemResponse,
  WaterEmergencyQueueItemResponse
} from "@/lib/dashboard-contracts";

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

  it("renders Water Emergency review exceptions, critical alerts, and blocker labels", () => {
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

    expect(html).toContain("Review Exception Visibility");
    expect(html).toContain("Critical Alerts");
    expect(html).toContain("Blocker Unknowns");
    expect(html).toContain("Detail Review Exceptions");
    expect(html).toContain("Water Detail Unknown Blocker");
    expect(html).not.toMatch(/<button|role="button"/);
    expect(html).not.toContain("Approve Water Emergency");
    expect(html).not.toContain("Resolve review");
  });

  it("renders Water Emergency next-step readiness and evidence without actions", () => {
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

    expect(html).toContain("Next-Step Readiness");
    expect(html).toContain("Needs Manual Review");
    expect(html).toContain("Needs Operator Decision");
    expect(html).toContain("Read-only readiness visibility");
    expect(html).toContain("Operator attention");
    expect(html).toContain("Evidence");
    expect(html).not.toMatch(/<button|role="button"/);
    expect(html).not.toContain("Approve Water Emergency");
    expect(html).not.toContain("Close Water Emergency");
    expect(html).not.toContain("Dispatch Water Emergency");
  });

  it("renders Water Emergency operator queue attention groups without action controls", () => {
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

    expect(html).toContain("Operator Queue");
    expect(html).toContain("Critical Attention");
    expect(html).toContain("Active Attention");
    expect(html).toContain("Closed Or Resolved");
    expect(html).toContain("Read-only triage visibility");
    expect(html).not.toMatch(/<button|role="button"/);
    expect(html).not.toContain("Approve Water Emergency");
    expect(html).not.toContain("Close Water Emergency");
    expect(html).not.toContain("Dispatch Water Emergency");
  });

  it("renders Water Emergency aging and follow-up timing visibility without actions", () => {
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

    expect(html).toContain("Aging &amp; Follow-Up Risk");
    expect(html).toContain("Read-only timing visibility");
    expect(html).toContain("Not an SLA engine");
    expect(html).toContain("Stale Evidence");
    expect(html).toContain("Missing Last Evidence At");
    expect(html).not.toMatch(/<button|role="button"/);
    expect(html).not.toContain("Approve Water Emergency");
    expect(html).not.toContain("Close Water Emergency");
    expect(html).not.toContain("Dispatch Water Emergency");
  });

  it("keeps closed Water Emergency queue records visible after active queue limits", () => {
    const activeBase =
      mockWaterEmergencyDashboard.operator_queue_summary.items[0];
    const closedBase =
      mockWaterEmergencyDashboard.operator_queue_summary.items.find(
        (item) => item.queue_group === "closed_or_resolved"
      ) ?? activeBase;
    const activeItems: WaterEmergencyQueueItemResponse[] = Array.from(
      { length: 7 },
      (_, index) => ({
        ...activeBase,
        water_emergency_id: `1000000${index}-0000-4000-8000-00000000000${index}`,
        attention_label: index === 0 ? "critical_attention" : "needs_manual_review",
        queue_group: "active_attention",
        attention_rank: index === 0 ? 10 : 20,
        summary: `Active queue test record ${index + 1}.`,
        related_job_id: `2000000${index}-0000-4000-8000-00000000000${index}`,
        related_visit_ids: [],
        evidence_references: [`water_emergency:active-${index}`]
      })
    );
    const closedTailItem: WaterEmergencyQueueItemResponse = {
      ...closedBase,
      water_emergency_id: "99999999-0000-4000-8000-000000000099",
      attention_label: "closed_or_resolved",
      queue_group: "closed_or_resolved",
      attention_rank: 90,
      summary:
        "Closed tail Water Emergency record remains visible outside active attention limits.",
      reason_codes: ["water_emergency_closed_or_resolved"],
      evidence_references: ["water_emergency:closed-tail"],
      current_status: "closed",
      current_stage: "closed_after_monitoring",
      open_review_count: 0,
      critical_alert_count: 0,
      blocker_count: 0,
      unknown_count: 0,
      related_job_id: "99999998-0000-4000-8000-000000000098",
      related_work_order_ids: [],
      related_visit_ids: [],
      audit_correlation_ids: []
    };

    const html = renderToStaticMarkup(
      <DashboardView
        result={{
          data: mockDashboardOverview,
          source: "mock"
        }}
        waterEmergencyResult={{
          data: {
            ...mockWaterEmergencyDashboard,
            operator_queue_summary: {
              ...mockWaterEmergencyDashboard.operator_queue_summary,
              total_records: activeItems.length + 1,
              active_attention_count: activeItems.length,
              closed_or_resolved_count: 1,
              critical_attention_count: 1,
              queue_group_counts: [
                { label: "active_attention", count: activeItems.length },
                { label: "closed_or_resolved", count: 1 }
              ],
              attention_label_counts: [
                { label: "critical_attention", count: 1 },
                { label: "needs_manual_review", count: activeItems.length - 1 },
                { label: "closed_or_resolved", count: 1 }
              ],
              items: [...activeItems, closedTailItem]
            }
          },
          source: "mock"
        }}
        waterEmergencyDetailResult={mockWaterEmergencyDetailResult}
      />
    );

    expect(html).toContain("Operator Queue");
    expect(html).toContain("Showing first 6 active attention records.");
    expect(html).toContain("Closed Or Resolved");
    expect(html).toContain(
      "Closed tail Water Emergency record remains visible outside active attention limits."
    );
    expect(html).not.toMatch(/<button|role="button"/);
    expect(html).not.toContain("Approve Water Emergency");
    expect(html).not.toContain("Close Water Emergency");
    expect(html).not.toContain("Dispatch Water Emergency");
  });

  it("keeps closed Water Emergency timing records visible after active timing limits", () => {
    const activeBase =
      mockWaterEmergencyDashboard.aging_followup_summary.items[0];
    const closedBase =
      mockWaterEmergencyDashboard.aging_followup_summary.items.find(
        (item) => item.timing_group === "closed_or_resolved"
      ) ?? activeBase;
    const activeItems: WaterEmergencyAgingFollowUpItemResponse[] = Array.from(
      { length: 7 },
      (_, index) => ({
        ...activeBase,
        water_emergency_id: `3000000${index}-0000-4000-8000-00000000000${index}`,
        time_sensitivity_label: index === 0 ? "followup_overdue" : "followup_due",
        timing_group: "followup_attention",
        timing_rank: index === 0 ? 10 : 40,
        summary: `Active timing test record ${index + 1}.`,
        related_job_id: `4000000${index}-0000-4000-8000-00000000000${index}`,
        related_visit_ids: [],
        evidence_references: [`water_emergency:timing-active-${index}`]
      })
    );
    const closedTailItem: WaterEmergencyAgingFollowUpItemResponse = {
      ...closedBase,
      water_emergency_id: "39999999-0000-4000-8000-000000000099",
      time_sensitivity_label: "closed_or_resolved",
      timing_group: "closed_or_resolved",
      timing_rank: 90,
      summary:
        "Closed tail Water Emergency timing record remains visible outside active timing limits.",
      reason_codes: ["closed_or_resolved"],
      requires_operator_attention: false,
      related_job_id: "39999998-0000-4000-8000-000000000098",
      related_work_order_ids: [],
      related_visit_ids: [],
      audit_correlation_ids: [],
      evidence_references: ["water_emergency:timing-closed-tail"]
    };

    const html = renderToStaticMarkup(
      <DashboardView
        result={{
          data: mockDashboardOverview,
          source: "mock"
        }}
        waterEmergencyResult={{
          data: {
            ...mockWaterEmergencyDashboard,
            aging_followup_summary: {
              ...mockWaterEmergencyDashboard.aging_followup_summary,
              total_records: activeItems.length + 1,
              active_timing_risk_count: activeItems.length,
              closed_or_resolved_count: 1,
              followup_due_count: activeItems.length - 1,
              followup_overdue_count: 1,
              stale_evidence_count: 0,
              unknown_timing_count: 0,
              label_counts: [
                { label: "followup_overdue", count: 1 },
                { label: "followup_due", count: activeItems.length - 1 },
                { label: "closed_or_resolved", count: 1 }
              ],
              items: [...activeItems, closedTailItem]
            }
          },
          source: "mock"
        }}
        waterEmergencyDetailResult={mockWaterEmergencyDetailResult}
      />
    );

    expect(html).toContain("Aging &amp; Follow-Up Risk");
    expect(html).toContain("Showing first 6 active timing records.");
    expect(html).toContain("Closed Or Resolved");
    expect(html).toContain(
      "Closed tail Water Emergency timing record remains visible outside active timing limits."
    );
    expect(html).not.toMatch(/<button|role="button"/);
    expect(html).not.toContain("Approve Water Emergency");
    expect(html).not.toContain("Close Water Emergency");
    expect(html).not.toContain("Dispatch Water Emergency");
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
