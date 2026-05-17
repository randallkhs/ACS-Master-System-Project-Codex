import type {
  DashboardOverviewResponse,
  DashboardSource
} from "@/lib/dashboard-contracts";
import { formatCount } from "@/lib/format";
import {
  StatusBadge,
  type StatusBadgeVariant
} from "@/components/dashboard/status-badge";

type ScenarioStoryboardProps = {
  data: DashboardOverviewResponse;
  source: DashboardSource;
};

type ScenarioMetric = {
  label: string;
  value: number;
  variant?: StatusBadgeVariant;
};

type ScenarioCard = {
  key: string;
  title: string;
  stateLabel: string;
  variant: StatusBadgeVariant;
  description: string;
  metrics: ScenarioMetric[];
};

export function ScenarioStoryboard({
  data,
  source
}: ScenarioStoryboardProps) {
  const scenarios = buildScenarioCards(data);
  const sourceLabel =
    source === "api" ? "Live backend read models" : "Mock fallback sample";
  const sourceVariant: StatusBadgeVariant =
    source === "api" ? "success" : "warning";

  return (
    <section
      id="scenario-storyboard"
      aria-labelledby="scenario-storyboard-title"
      className="scroll-mt-[26rem] rounded-md border border-slate-200 bg-white p-5 shadow-sm ring-1 ring-black/[0.02] sm:scroll-mt-44"
    >
      <div className="flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-between">
        <div>
          <div className="text-xs font-semibold uppercase tracking-[0.16em] text-[#2563eb]">
            Scenario Storyboard
          </div>
          <h2
            id="scenario-storyboard-title"
            className="mt-2 text-xl font-semibold tracking-normal text-[#162033]"
          >
            Live operational states at a glance
          </h2>
          <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-600">
            These cards group existing dashboard read-model counts into the
            scenario families used for local Module 29 seed verification. They
            do not create workflow state, trigger actions, or present synthetic
            examples as production data.
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          <StatusBadge label={sourceLabel} variant={sourceVariant} />
          <StatusBadge label="Display-only context" variant="info" />
        </div>
      </div>

      <div className="mt-5 grid gap-4 md:grid-cols-2 2xl:grid-cols-4">
        {scenarios.map((scenario) => (
          <article
            key={scenario.key}
            className="flex min-h-[17rem] flex-col rounded-md border border-slate-200 bg-slate-50/70 p-4"
          >
            <div className="flex items-start justify-between gap-3">
              <h3 className="text-base font-semibold leading-6 text-[#162033]">
                {scenario.title}
              </h3>
              <StatusBadge
                label={scenario.stateLabel}
                variant={scenario.variant}
              />
            </div>
            <p className="mt-3 text-sm leading-6 text-slate-600">
              {scenario.description}
            </p>
            <dl className="mt-4 grid grid-cols-2 gap-2">
              {scenario.metrics.map((metric) => (
                <div
                  key={`${scenario.key}-${metric.label}`}
                  className="rounded-md border border-slate-200 bg-white px-3 py-2.5"
                >
                  <dt className="text-xs font-semibold leading-5 text-slate-500">
                    {metric.label}
                  </dt>
                  <dd className="mt-1 flex items-center justify-between gap-2">
                    <span className="text-lg font-semibold leading-none text-[#162033]">
                      {formatCount(metric.value)}
                    </span>
                    <span
                      className={`h-2.5 w-2.5 shrink-0 rounded-full ${dotClassForVariant(
                        metric.variant ?? scenario.variant
                      )}`}
                      aria-hidden="true"
                    />
                  </dd>
                </div>
              ))}
            </dl>
          </article>
        ))}
      </div>
    </section>
  );
}

function buildScenarioCards(data: DashboardOverviewResponse): ScenarioCard[] {
  const { dispatch_summary: dispatch } = data;
  const { lifecycle_summary: lifecycle } = data;
  const { manual_review_summary: review } = data;
  const { operational_summary: summary } = data;
  const { timeline_summary: timeline } = data;

  return [
    {
      key: "dispatch-ready",
      title: "Standard dispatch-ready work",
      stateLabel:
        lifecycle.dispatch_ready_visits > 0 ? "Ready evidence" : "No ready visits",
      variant: lifecycle.dispatch_ready_visits > 0 ? "success" : "neutral",
      description:
        "Highlights standard work that backend read models already classify as dispatch-ready or awaiting dispatch execution.",
      metrics: [
        {
          label: "Ready visits",
          value: lifecycle.dispatch_ready_visits,
          variant: "success"
        },
        {
          label: "Awaiting execution",
          value:
            dispatch.route_assignments.awaiting_dispatch_execution_count,
          variant: "warning"
        },
        {
          label: "Dispatched",
          value: lifecycle.dispatched_route_assignments,
          variant: "info"
        },
        {
          label: "Assignments",
          value: dispatch.route_assignments.total_assignments,
          variant: "neutral"
        }
      ]
    },
    {
      key: "manual-review",
      title: "Manual Review safety queue",
      stateLabel: review.open_items > 0 ? "Review open" : "Clear",
      variant: review.open_items > 0 ? "warning" : "success",
      description:
        "Surfaces human-review workload and completed review examples without resolving or overriding Manual Review.",
      metrics: [
        { label: "Open", value: review.open_items, variant: "warning" },
        { label: "Deferred", value: review.deferred_items, variant: "warning" },
        { label: "Resolved", value: review.resolved_items, variant: "success" },
        { label: "Archived", value: review.archived_items, variant: "neutral" }
      ]
    },
    {
      key: "blocked",
      title: "Blocked operation evidence",
      stateLabel: summary.blocked_operations > 0 ? "Blocked" : "Clear",
      variant: summary.blocked_operations > 0 ? "danger" : "success",
      description:
        "Groups blocker counts already returned by the backend so operators can scan where work cannot safely continue.",
      metrics: [
        {
          label: "Operations",
          value: summary.blocked_operations,
          variant: "danger"
        },
        {
          label: "Lifecycle",
          value: lifecycle.blocker_count,
          variant: "danger"
        },
        {
          label: "Route blocks",
          value: dispatch.route_assignments.blocked_count,
          variant: "danger"
        },
        {
          label: "Escalation",
          value: summary.escalation_indicators,
          variant: "warning"
        }
      ]
    },
    {
      key: "external-execution",
      title: "External execution evidence",
      stateLabel:
        dispatch.external_execution.confirmation_failed_count > 0 ||
        dispatch.external_execution.execution_failed_count > 0
          ? "Failure evidence"
          : "Adapter evidence",
      variant:
        dispatch.external_execution.confirmation_failed_count > 0 ||
        dispatch.external_execution.execution_failed_count > 0
          ? "danger"
          : "info",
      description:
        "Shows adapter and confirmation state as persisted evidence only. Vendors are not called from the dashboard.",
      metrics: [
        {
          label: "Prepared",
          value: dispatch.external_execution.prepared_count,
          variant: "info"
        },
        {
          label: "Completed",
          value: dispatch.external_execution.execution_completed_count,
          variant: "success"
        },
        {
          label: "Failed",
          value:
            dispatch.external_execution.execution_failed_count +
            dispatch.external_execution.confirmation_failed_count,
          variant: "danger"
        },
        {
          label: "Retry ready",
          value: dispatch.external_execution.retry_prepared_count,
          variant: "warning"
        }
      ]
    },
    {
      key: "recovery",
      title: "Recovery and reconciliation",
      stateLabel:
        dispatch.reconciliation_recovery.replay_prepared_count > 0 ||
        dispatch.reconciliation_recovery.rollback_prepared_count > 0
          ? "Recovery prepared"
          : "No recovery",
      variant:
        dispatch.reconciliation_recovery.mismatch_count > 0 ||
        dispatch.reconciliation_recovery.divergence_count > 0
          ? "warning"
          : "success",
      description:
        "Frames mismatch, divergence, replay, and rollback evidence without exposing replay or rollback controls.",
      metrics: [
        {
          label: "Mismatches",
          value: dispatch.reconciliation_recovery.mismatch_count,
          variant: "danger"
        },
        {
          label: "Divergences",
          value: dispatch.reconciliation_recovery.divergence_count,
          variant: "danger"
        },
        {
          label: "Replay",
          value: dispatch.reconciliation_recovery.replay_prepared_count,
          variant: "warning"
        },
        {
          label: "Rollback",
          value: dispatch.reconciliation_recovery.rollback_prepared_count,
          variant: "warning"
        }
      ]
    },
    {
      key: "governance",
      title: "Governance and accountability",
      stateLabel:
        dispatch.governance_accountability.incident_prepared_count > 0
          ? "Incident evidence"
          : "Governance evidence",
      variant:
        dispatch.governance_accountability.accountability_blocked_count > 0
          ? "danger"
          : "warning",
      description:
        "Keeps approvals, intervention, escalation, and incident-preparation indicators visible as read-only evidence.",
      metrics: [
        {
          label: "Approved",
          value: dispatch.governance_accountability.operator_approved_count,
          variant: "success"
        },
        {
          label: "Intervention",
          value: dispatch.governance_accountability.intervention_required_count,
          variant: "warning"
        },
        {
          label: "Escalation",
          value: dispatch.governance_accountability.escalation_required_count,
          variant: "warning"
        },
        {
          label: "Incident",
          value: dispatch.governance_accountability.incident_prepared_count,
          variant: "warning"
        }
      ]
    },
    {
      key: "water-emergency",
      title: "Water Emergency separated path",
      stateLabel:
        summary.open_water_emergencies > 0 ? "Separated" : "No open records",
      variant: summary.open_water_emergencies > 0 ? "info" : "neutral",
      description:
        "Shows Water Emergency as a first-class separated operational path, not a standard dispatch action.",
      metrics: [
        {
          label: "Open",
          value: summary.open_water_emergencies,
          variant: "info"
        },
        {
          label: "Records",
          value: lifecycle.water_emergency_records,
          variant: "info"
        },
        {
          label: "Separated",
          value: lifecycle.water_emergency_separated_intake,
          variant: "info"
        },
        {
          label: "Review",
          value: review.reason_counts
            .filter((bucket) => bucket.label.toLowerCase().includes("water"))
            .reduce((total, bucket) => total + bucket.count, 0),
          variant: "warning"
        }
      ]
    },
    {
      key: "timeline",
      title: "Immutable timeline evidence",
      stateLabel: timeline.mutable_event_count > 0 ? "Check mutable" : "Immutable",
      variant: timeline.mutable_event_count > 0 ? "danger" : "success",
      description:
        "Summarizes ordered event evidence and audit-correlation references returned by backend read models.",
      metrics: [
        { label: "Returned", value: timeline.returned_events, variant: "info" },
        { label: "Total", value: timeline.total_events, variant: "neutral" },
        {
          label: "Mutable",
          value: timeline.mutable_event_count,
          variant: timeline.mutable_event_count > 0 ? "danger" : "success"
        },
        {
          label: "Audits",
          value: timeline.audit_correlation_ids.length,
          variant: "info"
        }
      ]
    }
  ];
}

function dotClassForVariant(variant: StatusBadgeVariant): string {
  const dotClasses: Record<StatusBadgeVariant, string> = {
    neutral: "bg-slate-400",
    success: "bg-emerald-500",
    warning: "bg-amber-500",
    danger: "bg-rose-500",
    info: "bg-blue-500"
  };

  return dotClasses[variant];
}
