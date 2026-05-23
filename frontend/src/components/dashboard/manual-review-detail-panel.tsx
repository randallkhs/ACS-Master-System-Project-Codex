import type {
  DashboardFetchResult,
  ManualReviewDetailResponse,
} from "@/lib/dashboard-contracts";
import { compactId, formatDateTime, humanizeLabel } from "@/lib/format";
import { CountBucketPanel } from "@/components/dashboard/count-bucket-panel";
import { SectionCard } from "@/components/dashboard/section-card";
import { SectionHeading } from "@/components/dashboard/section-heading";
import {
  badgeVariantForLabel,
  StatusBadge,
} from "@/components/dashboard/status-badge";
import { TimelineList } from "@/components/dashboard/timeline-list";

type ManualReviewDetailPanelProps = {
  result?: DashboardFetchResult<ManualReviewDetailResponse | null>;
};

export function ManualReviewDetailPanel({
  result,
}: ManualReviewDetailPanelProps) {
  if (!result) {
    return null;
  }

  const { data } = result;

  return (
    <section className="space-y-4">
      <SectionHeading
        id="manual-review-detail"
        label="Manual Review Detail"
        title="Read-only detail visibility"
        description="Focused Manual Review investigation context with linked entity, reason, and timeline evidence. This panel does not approve, reject, defer, archive, dispatch, or resolve review items."
      />

      {data ? (
        <ManualReviewDetailContent detail={data} />
      ) : (
        <SectionCard
          title="No Manual Review detail selected"
          description={
            result.errorMessage ??
            "No Manual Review record is currently selected for detail display."
          }
        >
          <div className="rounded-md border border-dashed border-slate-300 bg-slate-50 px-3 py-4 text-sm text-slate-600">
            Selectable workflow controls are intentionally absent in this Phase
            0 foundation. Detail visibility remains read-only and
            backend-driven.
          </div>
        </SectionCard>
      )}
    </section>
  );
}

function ManualReviewDetailContent({
  detail,
}: {
  detail: ManualReviewDetailResponse;
}) {
  const { review_item: item, linked_entity_context: context } = detail;

  return (
    <div className="space-y-4">
      <SectionCard
        title="Review summary"
        description={`${humanizeLabel(item.reason_code)} is displayed as a read-only Manual Review item. Manual Review remains the safety authority for future action modules.`}
      >
        <div className="flex flex-wrap gap-2">
          <StatusBadge
            label={humanizeLabel(item.status)}
            variant={badgeVariantForLabel(item.status)}
          />
          <StatusBadge
            label={humanizeLabel(item.primary_group)}
            variant={badgeVariantForLabel(item.primary_group)}
          />
          <StatusBadge
            label={item.attention_indicator ? "Requires review" : "Historical"}
            variant={item.attention_indicator ? "warning" : "neutral"}
          />
          {context.is_water_emergency_related ? (
            <StatusBadge label="Water Emergency review detail" variant="info" />
          ) : null}
        </div>

        <div className="mt-4 grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
          <DetailMetric label="Severity" value={humanizeLabel(item.severity)} />
          <DetailMetric
            label="Age bucket"
            value={humanizeLabel(item.age_bucket)}
          />
          <DetailMetric
            label="Confidence"
            value={
              item.confidence_score === null
                ? "Not scored"
                : `${item.confidence_score}%`
            }
          />
          <DetailMetric
            label="Created"
            value={formatDateTime(item.created_at)}
          />
        </div>

        <p className="mt-4 text-sm leading-6 text-slate-600">
          {item.recommended_action ??
            "Read-only evidence is available for operator review."}
        </p>
      </SectionCard>

      <SectionCard
        title="Decision Readiness"
        description={
          context.is_water_emergency_related
            ? "Water Emergency-related readiness is shown separately from standard Manual Review context and remains read-only."
            : "Readiness labels explain what evidence suggests for future operator review without executing any Manual Review action."
        }
      >
        <div className="flex flex-wrap gap-2">
          <StatusBadge
            label={humanizeLabel(detail.decision_readiness.label)}
            variant={badgeVariantForLabel(detail.decision_readiness.label)}
          />
          <StatusBadge
            label={
              detail.decision_readiness.is_active_decision_need
                ? "Active decision need"
                : "Historical visibility"
            }
            variant={
              detail.decision_readiness.is_active_decision_need
                ? "warning"
                : "neutral"
            }
          />
          {detail.decision_readiness.is_resolution_candidate ? (
            <StatusBadge label="Resolution review candidate" variant="info" />
          ) : null}
        </div>

        <p className="mt-4 text-sm leading-6 text-slate-600">
          {detail.decision_readiness.summary}
        </p>

        <div className="mt-4 grid gap-4 lg:grid-cols-2">
          <div>
            <div className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-500">
              Readiness reasons
            </div>
            <div className="mt-2 flex flex-wrap gap-2">
              {detail.decision_readiness.reason_codes.map((reasonCode) => (
                <StatusBadge
                  key={reasonCode}
                  label={humanizeLabel(reasonCode)}
                  variant={badgeVariantForLabel(reasonCode)}
                />
              ))}
            </div>
          </div>
          <div>
            <div className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-500">
              Readiness evidence
            </div>
            <div className="mt-2">
              <EvidenceList
                references={detail.decision_readiness.evidence_references}
              />
            </div>
          </div>
        </div>
      </SectionCard>

      <SectionCard
        title="Future Action Preflight"
        description={
          context.is_water_emergency_related
            ? "Water Emergency-related action preflight is separated from standard Manual Review action preparation and remains read-only."
            : "Future action requirements are displayed as preparation notes only. This panel does not execute Manual Review actions."
        }
      >
        <div className="flex flex-wrap gap-2">
          <StatusBadge
            label={humanizeLabel(detail.action_preflight.label)}
            variant={badgeVariantForLabel(detail.action_preflight.label)}
          />
          <StatusBadge
            label={
              detail.action_preflight.is_currently_executable
                ? "Currently executable"
                : "Not executable in Phase 0"
            }
            variant={
              detail.action_preflight.is_currently_executable
                ? "warning"
                : "neutral"
            }
          />
          {detail.action_preflight.requires_operator_identity ? (
            <StatusBadge label="Requires operator identity" variant="info" />
          ) : null}
          {detail.action_preflight.requires_audit_reason ? (
            <StatusBadge label="Requires audit reason" variant="info" />
          ) : null}
        </div>

        <p className="mt-4 text-sm leading-6 text-slate-600">
          {detail.action_preflight.summary}
        </p>

        <div className="mt-4 grid gap-4 lg:grid-cols-3">
          <div>
            <div className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-500">
              Preflight blockers
            </div>
            <div className="mt-2 flex flex-wrap gap-2">
              {detail.action_preflight.blocker_codes.map((blockerCode) => (
                <StatusBadge
                  key={blockerCode}
                  label={humanizeLabel(blockerCode)}
                  variant={badgeVariantForLabel(blockerCode)}
                />
              ))}
            </div>
          </div>
          <div>
            <div className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-500">
              Future requirements
            </div>
            <div className="mt-2 flex flex-wrap gap-2">
              {detail.action_preflight.required_future_controls.map(
                (control) => (
                  <StatusBadge
                    key={control}
                    label={humanizeLabel(control)}
                    variant={badgeVariantForLabel(control)}
                  />
                ),
              )}
            </div>
          </div>
          <div>
            <div className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-500">
              Preflight evidence
            </div>
            <div className="mt-2">
              <EvidenceList
                references={detail.action_preflight.evidence_references}
              />
            </div>
          </div>
        </div>
      </SectionCard>

      <SectionCard
        title="Future Action Preview"
        description={
          context.is_water_emergency_related
            ? "Water Emergency-related future-action preview is separated from standard Manual Review action preparation and remains read-only."
            : "Future action preview explains expected non-binding outcomes for later authenticated action modules without executing anything now."
        }
      >
        <div className="flex flex-wrap gap-2">
          <StatusBadge
            label={humanizeLabel(detail.future_action_preview.label)}
            variant={badgeVariantForLabel(detail.future_action_preview.label)}
          />
          <StatusBadge
            label={
              detail.future_action_preview.is_currently_executable
                ? "Currently executable"
                : "Not executable in Phase 0"
            }
            variant={
              detail.future_action_preview.is_currently_executable
                ? "warning"
                : "neutral"
            }
          />
          {detail.future_action_preview.requires_operator_identity ? (
            <StatusBadge
              label="Requires future operator identity"
              variant="info"
            />
          ) : null}
          {detail.future_action_preview.requires_audit_reason ? (
            <StatusBadge label="Requires future audit reason" variant="info" />
          ) : null}
        </div>

        <p className="mt-4 text-sm leading-6 text-slate-600">
          {detail.future_action_preview.description}
        </p>

        <div className="mt-4 grid gap-4 lg:grid-cols-2">
          <div>
            <div className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-500">
              Expected Outcome
            </div>
            <p className="mt-2 text-sm leading-6 text-slate-600">
              {detail.future_action_preview.expected_outcome_summary}
            </p>
          </div>
          <div>
            <div className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-500">
              Impacted Entities
            </div>
            <p className="mt-2 break-words text-sm leading-6 text-slate-600">
              {detail.future_action_preview.impacted_entity_summary}
            </p>
          </div>
        </div>

        <div className="mt-4 grid gap-4 lg:grid-cols-3">
          <div>
            <div className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-500">
              Preview blockers
            </div>
            <div className="mt-2 flex flex-wrap gap-2">
              {detail.future_action_preview.blocker_codes.map((blockerCode) => (
                <StatusBadge
                  key={blockerCode}
                  label={humanizeLabel(blockerCode)}
                  variant={badgeVariantForLabel(blockerCode)}
                />
              ))}
            </div>
          </div>
          <div>
            <div className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-500">
              Future requirements
            </div>
            <div className="mt-2 flex flex-wrap gap-2">
              {detail.future_action_preview.required_future_controls.map(
                (control) => (
                  <StatusBadge
                    key={control}
                    label={humanizeLabel(control)}
                    variant={badgeVariantForLabel(control)}
                  />
                ),
              )}
            </div>
          </div>
          <div>
            <div className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-500">
              Preview evidence
            </div>
            <div className="mt-2">
              <EvidenceList
                references={detail.future_action_preview.evidence_references}
              />
            </div>
          </div>
        </div>
      </SectionCard>

      <SectionCard
        title="Future Command Contract"
        description={
          context.is_water_emergency_related
            ? "Water Emergency-related command contract requirements remain separated from standard Manual Review command preparation and are read-only."
            : "Future command contract and audit envelope requirements are displayed as read-only Phase 0 preparation only."
        }
      >
        <div className="flex flex-wrap gap-2">
          <StatusBadge
            label={humanizeLabel(detail.command_contract.label)}
            variant={badgeVariantForLabel(detail.command_contract.label)}
          />
          <StatusBadge
            label={
              detail.command_contract.is_currently_executable
                ? "Currently executable: Yes"
                : "Currently executable: No"
            }
            variant={
              detail.command_contract.is_currently_executable
                ? "warning"
                : "neutral"
            }
          />
          {detail.command_contract.requires_operator_identity ? (
            <StatusBadge
              label="Requires future operator identity"
              variant="info"
            />
          ) : null}
          {detail.command_contract.requires_role_authorization ? (
            <StatusBadge
              label="Requires future role authorization"
              variant="info"
            />
          ) : null}
          {detail.command_contract.requires_audit_reason ? (
            <StatusBadge label="Requires future audit reason" variant="info" />
          ) : null}
          {detail.command_contract.requires_idempotency_key ? (
            <StatusBadge
              label="Requires future idempotency key"
              variant="info"
            />
          ) : null}
        </div>

        <p className="mt-4 text-sm leading-6 text-slate-600">
          {detail.command_contract.summary}
        </p>
        <p className="mt-2 text-sm leading-6 text-slate-600">
          {detail.command_contract.not_executable_reason}
        </p>

        <div className="mt-4 grid gap-4 lg:grid-cols-2">
          <div>
            <div className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-500">
              Audit Envelope Requirements
            </div>
            <div className="mt-2 flex flex-wrap gap-2">
              {detail.command_contract.required_contract_labels.map(
                (requirement) => (
                  <StatusBadge
                    key={requirement}
                    label={humanizeLabel(requirement)}
                    variant={badgeVariantForLabel(requirement)}
                  />
                ),
              )}
            </div>
          </div>
          <div>
            <div className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-500">
              Command Candidates
            </div>
            <div className="mt-2 flex flex-wrap gap-2">
              {detail.command_contract.future_command_candidates.length > 0 ? (
                detail.command_contract.future_command_candidates.map(
                  (candidate) => (
                    <StatusBadge
                      key={candidate}
                      label={humanizeLabel(candidate)}
                      variant="neutral"
                    />
                  ),
                )
              ) : (
                <span className="text-sm text-slate-600">
                  No active future command candidate is available.
                </span>
              )}
            </div>
          </div>
        </div>

        <div className="mt-4 grid gap-4 lg:grid-cols-3">
          <div>
            <div className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-500">
              Command blockers
            </div>
            <div className="mt-2 flex flex-wrap gap-2">
              {detail.command_contract.blocker_codes.length > 0 ? (
                detail.command_contract.blocker_codes.map((blockerCode) => (
                  <StatusBadge
                    key={blockerCode}
                    label={humanizeLabel(blockerCode)}
                    variant={badgeVariantForLabel(blockerCode)}
                  />
                ))
              ) : (
                <span className="text-sm text-slate-600">
                  No blocker codes beyond Phase 0 read-only status.
                </span>
              )}
            </div>
          </div>
          <div>
            <div className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-500">
              Impacted Entities
            </div>
            <p className="mt-2 break-words text-sm leading-6 text-slate-600">
              {detail.command_contract.impacted_entity_summary}
            </p>
          </div>
          <div>
            <div className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-500">
              Contract evidence
            </div>
            <div className="mt-2">
              <EvidenceList
                references={detail.command_contract.evidence_references}
              />
            </div>
          </div>
        </div>
      </SectionCard>

      <SectionCard
        title="Command Dry Run"
        description={
          context.is_water_emergency_related
            ? "Water Emergency-related command dry-run context remains separated from standard Manual Review dry-run preparation and is read-only."
            : "Audit Ledger Preparation is displayed as read-only Phase 0 command dry-run context only."
        }
      >
        <div className="flex flex-wrap gap-2">
          <StatusBadge
            label={humanizeLabel(detail.audit_ledger_dry_run.label)}
            variant={badgeVariantForLabel(detail.audit_ledger_dry_run.label)}
          />
          <StatusBadge
            label={
              detail.audit_ledger_dry_run.is_currently_executable
                ? "Currently executable: Yes"
                : "Currently executable: No"
            }
            variant={
              detail.audit_ledger_dry_run.is_currently_executable
                ? "warning"
                : "neutral"
            }
          />
          <StatusBadge
            label={
              detail.audit_ledger_dry_run.phase_allows_execution
                ? "Phase allows execution: Yes"
                : "Phase allows execution: No"
            }
            variant={
              detail.audit_ledger_dry_run.phase_allows_execution
                ? "warning"
                : "neutral"
            }
          />
          {detail.audit_ledger_dry_run.requires_operator_identity ? (
            <StatusBadge
              label="Requires future operator identity"
              variant="info"
            />
          ) : null}
          {detail.audit_ledger_dry_run.requires_audit_reason ? (
            <StatusBadge label="Requires future audit reason" variant="info" />
          ) : null}
          {detail.audit_ledger_dry_run.requires_idempotency_key ? (
            <StatusBadge
              label="Requires future idempotency key"
              variant="info"
            />
          ) : null}
          {detail.audit_ledger_dry_run.requires_immutable_event_recording ? (
            <StatusBadge label="Immutable Event Required" variant="info" />
          ) : null}
          {detail.audit_ledger_dry_run.requires_post_action_consistency_check ? (
            <StatusBadge label="Consistency Check Required" variant="info" />
          ) : null}
        </div>

        <p className="mt-4 text-sm leading-6 text-slate-600">
          {detail.audit_ledger_dry_run.summary}
        </p>
        <p className="mt-2 text-sm leading-6 text-slate-600">
          {detail.audit_ledger_dry_run.execution_unavailable_reason}
        </p>

        <div className="mt-4 grid gap-4 lg:grid-cols-2">
          <div>
            <div className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-500">
              Audit Ledger Preparation
            </div>
            <DetailRow
              label="Proposed future event"
              value={`${detail.audit_ledger_dry_run.proposed_future_event_type} / ${humanizeLabel(detail.audit_ledger_dry_run.proposed_future_event_state)}`}
            />
            <div className="mt-3">
              <DetailRow
                label="Proposed idempotency scope"
                value={detail.audit_ledger_dry_run.proposed_future_idempotency_scope}
              />
            </div>
          </div>
          <div>
            <div className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-500">
              Future Consistency Check
            </div>
            <p className="mt-2 text-sm leading-6 text-slate-600">
              {
                detail.audit_ledger_dry_run
                  .proposed_future_consistency_check_summary
              }
            </p>
          </div>
        </div>

        <div className="mt-4 grid gap-4 lg:grid-cols-3">
          <div>
            <div className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-500">
              Dry-run requirements
            </div>
            <div className="mt-2 flex flex-wrap gap-2">
              {detail.audit_ledger_dry_run.required_labels.map((label) => (
                <StatusBadge
                  key={label}
                  label={humanizeLabel(label)}
                  variant={badgeVariantForLabel(label)}
                />
              ))}
            </div>
          </div>
          <div>
            <div className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-500">
              Audit envelope fields
            </div>
            <div className="mt-2 flex flex-wrap gap-2">
              {detail.audit_ledger_dry_run.proposed_future_audit_envelope_fields.map(
                (field) => (
                  <StatusBadge
                    key={field}
                    label={humanizeLabel(field)}
                    variant="neutral"
                  />
                ),
              )}
            </div>
          </div>
          <div>
            <div className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-500">
              Dry-run evidence
            </div>
            <div className="mt-2">
              <EvidenceList
                references={detail.audit_ledger_dry_run.evidence_references}
              />
            </div>
          </div>
        </div>
      </SectionCard>

      <div className="grid gap-4 xl:grid-cols-[minmax(0,1fr)_minmax(0,1fr)]">
        <SectionCard
          title="Reason And Evidence Context"
          description="Reason fields and evidence references are projected from persisted review data only."
        >
          <div className="space-y-3">
            <DetailRow
              label="Reason code"
              value={humanizeLabel(detail.reason_context.reason_code)}
            />
            <DetailRow
              label="Review reason codes"
              value={
                detail.reason_context.review_reason_codes.length > 0
                  ? detail.reason_context.review_reason_codes
                      .map(humanizeLabel)
                      .join(", ")
                  : "No structured reason list returned"
              }
            />
            <DetailRow
              label="Snapshot evidence"
              value={
                detail.reason_context.snapshot_keys.length > 0
                  ? detail.reason_context.snapshot_keys
                      .map(humanizeLabel)
                      .join(", ")
                  : "No snapshot evidence returned"
              }
            />
            <EvidenceList
              references={detail.reason_context.evidence_references}
            />
          </div>
        </SectionCard>

        <SectionCard
          title="Linked Entity Context"
          description={
            context.is_water_emergency_related
              ? "Water Emergency-related Manual Review detail is separated from standard dispatch review detail."
              : "Standard dispatch, job, work-order, visit, or route context is displayed without workflow authority."
          }
        >
          <div className="grid gap-3 sm:grid-cols-2">
            <DetailMetric
              label="Entity"
              value={`${humanizeLabel(context.entity_type)} ${compactNullableId(
                context.entity_id,
              )}`}
            />
            <DetailMetric
              label="Job"
              value={`${humanizeLabel(context.job_status)} ${compactNullableId(
                context.job_id,
              )}`}
            />
            <DetailMetric
              label="Work order"
              value={`${humanizeLabel(context.work_order_status)} ${compactNullableId(
                context.work_order_id,
              )}`}
            />
            <DetailMetric
              label="Visit"
              value={`${humanizeLabel(context.visit_status)} ${compactNullableId(
                context.visit_id,
              )}`}
            />
            <DetailMetric
              label="Route"
              value={`${humanizeLabel(
                context.route_assignment_status,
              )} ${compactNullableId(context.route_assignment_id)}`}
            />
            <DetailMetric
              label="Water Emergency"
              value={`${humanizeLabel(
                context.water_emergency_status,
              )} ${compactNullableId(context.water_emergency_id)}`}
            />
          </div>

          {context.unknown_indicators.length > 0 ? (
            <div className="mt-4 flex flex-wrap gap-2">
              {context.unknown_indicators.map((indicator) => (
                <StatusBadge
                  key={indicator}
                  label={humanizeLabel(indicator)}
                  variant="warning"
                />
              ))}
            </div>
          ) : null}
        </SectionCard>
      </div>

      <div className="grid gap-4 lg:grid-cols-[minmax(0,0.8fr)_minmax(0,1.2fr)]">
        <CountBucketPanel
          title="Detail Data Gaps"
          buckets={detail.data_gap_counts}
        />
        <SectionCard
          title="Manual Review Evidence Timeline"
          description="Timeline entries are ordered by backend read models and preserve audit correlation references."
        >
          <TimelineList entries={detail.timeline_summary.entries} />
        </SectionCard>
      </div>
    </div>
  );
}

function DetailMetric({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-md border border-slate-200 bg-slate-50 px-3 py-2">
      <div className="text-xs font-semibold text-slate-500">{label}</div>
      <div className="mt-1 break-words text-sm font-semibold text-[#162033]">
        {value}
      </div>
    </div>
  );
}

function DetailRow({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <div className="text-xs font-semibold text-slate-500">{label}</div>
      <div className="mt-1 break-words text-sm font-semibold text-[#162033]">
        {value}
      </div>
    </div>
  );
}

function EvidenceList({ references }: { references: string[] }) {
  if (references.length === 0) {
    return (
      <div className="rounded-md border border-dashed border-slate-300 bg-slate-50 px-3 py-4 text-sm text-slate-600">
        No evidence references returned.
      </div>
    );
  }

  return (
    <div className="flex flex-wrap gap-2">
      {references.map((reference) => (
        <span
          key={reference}
          className="break-all rounded-md border border-slate-200 bg-slate-50 px-2 py-1 font-mono text-xs font-medium text-slate-600"
        >
          {reference}
        </span>
      ))}
    </div>
  );
}

function compactNullableId(value: string | null): string {
  return value ? compactId(value) : "Not linked";
}
