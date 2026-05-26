import type {
  AuthStatusResponse,
  DashboardFetchResult,
  DashboardOverviewResponse,
  DashboardSource,
  ManualReviewDetailResponse,
  ManualReviewQueueResponse,
  WaterEmergencyDashboardResponse,
  WaterEmergencyDetailResponse
} from "@/lib/dashboard-contracts";
import { AppShell } from "@/components/layout/app-shell";
import { AlertStrip } from "@/components/dashboard/alert-strip";
import { CountBucketPanel } from "@/components/dashboard/count-bucket-panel";
import { ManualReviewDetailPanel } from "@/components/dashboard/manual-review-detail-panel";
import { ManualReviewQueue } from "@/components/dashboard/manual-review-queue";
import { OperationalHealthPanel } from "@/components/dashboard/operational-health-panel";
import { ScenarioStoryboard } from "@/components/dashboard/scenario-storyboard";
import { SectionCard } from "@/components/dashboard/section-card";
import { SectionHeading } from "@/components/dashboard/section-heading";
import { StatCard } from "@/components/dashboard/stat-card";
import { TimelineList } from "@/components/dashboard/timeline-list";
import { WaterEmergencyDashboard } from "@/components/dashboard/water-emergency-dashboard";
import { WaterEmergencyDetailPanel } from "@/components/dashboard/water-emergency-detail-panel";

type DashboardViewProps = {
  result: DashboardFetchResult<DashboardOverviewResponse>;
  waterEmergencyResult: DashboardFetchResult<WaterEmergencyDashboardResponse>;
  waterEmergencyDetailResult: DashboardFetchResult<WaterEmergencyDetailResponse | null>;
  manualReviewQueueResult?: DashboardFetchResult<ManualReviewQueueResponse>;
  manualReviewDetailResult?: DashboardFetchResult<ManualReviewDetailResponse | null>;
  authStatusResult?: DashboardFetchResult<AuthStatusResponse>;
};

export function DashboardView({
  result,
  waterEmergencyResult,
  waterEmergencyDetailResult,
  manualReviewQueueResult,
  manualReviewDetailResult,
  authStatusResult
}: DashboardViewProps) {
  const { data, source, errorMessage } = result;
  const { operational_summary: summary } = data;
  const { lifecycle_summary: lifecycle } = data;
  const { manual_review_summary: review } = data;
  const { dispatch_summary: dispatch } = data;
  const dashboardSource: DashboardSource =
    source === "api" &&
    waterEmergencyResult.source === "api" &&
    waterEmergencyDetailResult.source === "api" &&
    (!manualReviewQueueResult || manualReviewQueueResult.source === "api") &&
    (!manualReviewDetailResult || manualReviewDetailResult.source === "api") &&
    (!authStatusResult || authStatusResult.source === "api")
      ? "api"
      : "mock";
  const fallbackMessage =
    [
      errorMessage,
      waterEmergencyResult.errorMessage,
      waterEmergencyDetailResult.errorMessage,
      manualReviewQueueResult?.errorMessage,
      manualReviewDetailResult?.errorMessage,
      authStatusResult?.errorMessage
    ]
      .filter(Boolean)
      .join(" ") || undefined;

  return (
    <AppShell generatedAt={data.generated_at} source={dashboardSource}>
      <div className="space-y-8">
        <div className="grid gap-4 xl:grid-cols-2">
          <AlertStrip title="Read-only operational dashboard" tone="info">
            This screen displays backend dashboard read models only. It does not
            dispatch jobs, resolve Manual Review, trigger integrations, call AI,
            or infer hidden lifecycle transitions.
          </AlertStrip>

          {dashboardSource === "mock" ? (
            <AlertStrip title="Fallback data is active" tone="warning">
              {fallbackMessage ??
                "The backend dashboard API was not available, so typed local fallback data is shown for layout validation."}
            </AlertStrip>
          ) : null}
        </div>

        <OperationalHealthPanel summary={summary} lifecycle={lifecycle} />

        <ScenarioStoryboard data={data} source={source} />

        <WaterEmergencyDashboard result={waterEmergencyResult} />

        <WaterEmergencyDetailPanel result={waterEmergencyDetailResult} />

        <section className="space-y-4">
          <SectionHeading
            id="overview"
            label="Overview"
            title="Operational Summary"
            description="Top-level counts from persisted backend state, including safety blockers, Manual Review, Water Emergency, and audit correlation evidence."
          />
          <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
            <StatCard label="Jobs" value={summary.total_jobs} detail="Persisted job records" />
            <StatCard
              label="Work Orders"
              value={summary.total_work_orders}
              detail="Generated operational work"
            />
            <StatCard label="Visits" value={summary.total_visits} detail="Scheduled or prepared visits" />
            <StatCard
              label="Route Assignments"
              value={summary.total_route_assignments}
              detail="Prepared routing records"
            />
            <StatCard
              label="Manual Review Open"
              value={summary.open_manual_reviews}
              detail="Human review remains authoritative"
              tone={summary.open_manual_reviews > 0 ? "warning" : "good"}
            />
            <StatCard
              label="Blocked Operations"
              value={summary.blocked_operations}
              detail="Backend blocker evidence"
              tone={summary.blocked_operations > 0 ? "danger" : "good"}
            />
            <StatCard
              label="Escalation Indicators"
              value={summary.escalation_indicators}
              detail="Prepared escalation evidence"
              tone={summary.escalation_indicators > 0 ? "warning" : "good"}
            />
            <StatCard
              label="Open Water Emergencies"
              value={summary.open_water_emergencies}
              detail="Separated first-class workflow records"
              tone={summary.open_water_emergencies > 0 ? "info" : "neutral"}
            />
            <StatCard
              label="Audit Correlations"
              value={summary.audit_correlation_count}
              detail="Traceability references"
              tone="info"
            />
          </div>
        </section>

        <section className="space-y-4">
          <SectionHeading
            id="lifecycle"
            label="Lifecycle"
            title="Dispatch Lifecycle Summary"
            description="Lifecycle counts are displayed exactly as the backend contract provides them. The frontend does not decide lifecycle transitions."
          />
          <div className="grid gap-4 lg:grid-cols-2 xl:grid-cols-3">
            <CountBucketPanel title="Intake Lifecycle" buckets={lifecycle.intake_lifecycle_counts} />
            <CountBucketPanel title="Job Status" buckets={lifecycle.job_status_counts} />
            <CountBucketPanel title="Work Order Status" buckets={lifecycle.work_order_status_counts} />
            <CountBucketPanel title="Visit Status" buckets={lifecycle.visit_status_counts} />
            <CountBucketPanel title="Route Status" buckets={lifecycle.route_status_counts} />
            <CountBucketPanel
              title="Dispatch Execution State"
              buckets={lifecycle.dispatch_execution_state_counts}
            />
          </div>
          <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-5">
            <StatCard label="Dispatch Ready Visits" value={lifecycle.dispatch_ready_visits} tone="good" />
            <StatCard
              label="Dispatched Assignments"
              value={lifecycle.dispatched_route_assignments}
              tone="info"
            />
            <StatCard
              label="Water Emergency Records"
              value={lifecycle.water_emergency_records}
              tone="info"
            />
            <StatCard
              label="Separated Intake"
              value={lifecycle.water_emergency_separated_intake}
              tone="info"
            />
            <StatCard
              label="Lifecycle Blockers"
              value={lifecycle.blocker_count}
              tone={lifecycle.blocker_count > 0 ? "danger" : "good"}
            />
          </div>
        </section>

        <section className="space-y-4">
          <SectionHeading
            id="manual-review"
            label="Manual Review"
            title="Safety Review Summary"
            description="Manual Review remains the core safety system. This UI exposes review counts and indicators without resolving or overriding them."
          />
          <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-5">
            <StatCard label="Total Items" value={review.total_items} />
            <StatCard label="Open" value={review.open_items} tone={review.open_items > 0 ? "warning" : "good"} />
            <StatCard label="Deferred" value={review.deferred_items} tone="warning" />
            <StatCard label="Resolved" value={review.resolved_items} tone="good" />
            <StatCard label="Archived" value={review.archived_items} />
          </div>
          <div className="grid gap-4 lg:grid-cols-2">
            <CountBucketPanel title="Severity Counts" buckets={review.severity_counts} />
            <CountBucketPanel title="Reason Counts" buckets={review.reason_counts} />
          </div>
        </section>

        {manualReviewQueueResult ? (
          <ManualReviewQueue
            result={manualReviewQueueResult}
            authStatusResult={authStatusResult}
          />
        ) : null}

        <ManualReviewDetailPanel result={manualReviewDetailResult} />

        <section className="space-y-4">
          <SectionHeading
            id="dispatch"
            label="Dispatch"
            title="Route Assignment Summary"
            description="Dispatch data is projected from backend route-assignment state. No dispatch execution control is present in this foundation."
          />
          <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
            <StatCard
              label="Total Assignments"
              value={dispatch.route_assignments.total_assignments}
            />
            <StatCard
              label="Awaiting Execution"
              value={dispatch.route_assignments.awaiting_dispatch_execution_count}
              tone="warning"
            />
            <StatCard
              label="Blocked Assignments"
              value={dispatch.route_assignments.blocked_count}
              tone={dispatch.route_assignments.blocked_count > 0 ? "danger" : "good"}
            />
          </div>
          <div className="grid gap-4 lg:grid-cols-2 xl:grid-cols-4">
            <CountBucketPanel
              title="Assignment Status"
              buckets={dispatch.route_assignments.status_counts}
            />
            <CountBucketPanel
              title="Region Counts"
              buckets={dispatch.route_assignments.region_counts}
            />
            <CountBucketPanel
              title="Time Windows"
              buckets={dispatch.route_assignments.time_window_counts}
            />
            <CountBucketPanel
              title="Authorization State"
              buckets={dispatch.route_assignments.authorization_state_counts}
            />
          </div>
        </section>

        <section className="space-y-4">
          <SectionHeading
            id="external-execution"
            label="External Execution"
            title="Adapter Execution Evidence"
            description="External systems remain adapters. This view displays persisted execution and confirmation summaries without calling vendors."
          />
          <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
            <StatCard
              label="Prepared"
              value={dispatch.external_execution.prepared_count}
              tone="info"
            />
            <StatCard
              label="Completed"
              value={dispatch.external_execution.execution_completed_count}
              tone="good"
            />
            <StatCard
              label="Execution Failed"
              value={dispatch.external_execution.execution_failed_count}
              tone={dispatch.external_execution.execution_failed_count > 0 ? "danger" : "good"}
            />
            <StatCard
              label="Confirmation Failed"
              value={dispatch.external_execution.confirmation_failed_count}
              tone={dispatch.external_execution.confirmation_failed_count > 0 ? "danger" : "good"}
            />
            <StatCard
              label="Retry Prepared"
              value={dispatch.external_execution.retry_prepared_count}
              tone="warning"
            />
            <StatCard
              label="Reconciliation Required"
              value={dispatch.external_execution.reconciliation_required_count}
              tone={
                dispatch.external_execution.reconciliation_required_count > 0
                  ? "warning"
                  : "good"
              }
            />
          </div>
          <div className="grid gap-4 lg:grid-cols-3">
            <CountBucketPanel
              title="Adapter State"
              buckets={dispatch.external_execution.adapter_state_counts}
            />
            <CountBucketPanel
              title="Execution State"
              buckets={dispatch.external_execution.execution_state_counts}
            />
            <CountBucketPanel
              title="Confirmation State"
              buckets={dispatch.external_execution.confirmation_state_counts}
            />
          </div>
        </section>

        <section className="space-y-4">
          <SectionHeading
            id="recovery"
            label="Recovery"
            title="Reconciliation And Recovery"
            description="Recovery counts reflect backend preparation evidence only. Replay, rollback, and reconciliation execution are intentionally absent."
          />
          <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-5">
            <StatCard
              label="Mismatches"
              value={dispatch.reconciliation_recovery.mismatch_count}
              tone={dispatch.reconciliation_recovery.mismatch_count > 0 ? "danger" : "good"}
            />
            <StatCard
              label="Divergences"
              value={dispatch.reconciliation_recovery.divergence_count}
              tone={dispatch.reconciliation_recovery.divergence_count > 0 ? "danger" : "good"}
            />
            <StatCard
              label="Replay Prepared"
              value={dispatch.reconciliation_recovery.replay_prepared_count}
              tone="warning"
            />
            <StatCard
              label="Rollback Prepared"
              value={dispatch.reconciliation_recovery.rollback_prepared_count}
              tone="warning"
            />
            <StatCard
              label="Recovery Blocked"
              value={dispatch.reconciliation_recovery.recovery_blocked_count}
              tone={
                dispatch.reconciliation_recovery.recovery_blocked_count > 0
                  ? "danger"
                  : "good"
              }
            />
          </div>
          <div className="grid gap-4 lg:grid-cols-2">
            <CountBucketPanel
              title="Reconciliation State"
              buckets={dispatch.reconciliation_recovery.reconciliation_state_counts}
            />
            <CountBucketPanel
              title="Recovery State"
              buckets={dispatch.reconciliation_recovery.recovery_state_counts}
            />
          </div>
        </section>

        <section className="space-y-4">
          <SectionHeading
            id="governance"
            label="Governance"
            title="Accountability And Intervention"
            description="Governance and accountability summaries surface approval, intervention, escalation, and incident-preparation indicators without performing those actions."
          />
          <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-5">
            <StatCard
              label="Operator Approved"
              value={dispatch.governance_accountability.operator_approved_count}
              tone="good"
            />
            <StatCard
              label="Intervention Required"
              value={dispatch.governance_accountability.intervention_required_count}
              tone={
                dispatch.governance_accountability.intervention_required_count > 0
                  ? "warning"
                  : "good"
              }
            />
            <StatCard
              label="Escalation Required"
              value={dispatch.governance_accountability.escalation_required_count}
              tone={
                dispatch.governance_accountability.escalation_required_count > 0
                  ? "warning"
                  : "good"
              }
            />
            <StatCard
              label="Incident Prepared"
              value={dispatch.governance_accountability.incident_prepared_count}
              tone="warning"
            />
            <StatCard
              label="Accountability Blocked"
              value={dispatch.governance_accountability.accountability_blocked_count}
              tone={
                dispatch.governance_accountability.accountability_blocked_count > 0
                  ? "danger"
                  : "good"
              }
            />
          </div>
          <div className="grid gap-4 lg:grid-cols-2">
            <CountBucketPanel
              title="Governance State"
              buckets={dispatch.governance_accountability.governance_state_counts}
            />
            <CountBucketPanel
              title="Accountability State"
              buckets={dispatch.governance_accountability.accountability_state_counts}
            />
          </div>
        </section>

        <SectionCard
          id="timeline"
          title="Operational Event Timeline"
          description="Timeline evidence is ordered by backend read models and preserves audit-correlation references."
        >
          <div className="mb-5 grid gap-4 sm:grid-cols-3">
            <StatCard label="Total Events" value={data.timeline_summary.total_events} tone="info" />
            <StatCard label="Returned Events" value={data.timeline_summary.returned_events} />
            <StatCard
              label="Mutable Events"
              value={data.timeline_summary.mutable_event_count}
              tone={data.timeline_summary.mutable_event_count > 0 ? "danger" : "good"}
            />
          </div>
          <TimelineList entries={data.timeline_summary.entries} />
        </SectionCard>
      </div>
    </AppShell>
  );
}
