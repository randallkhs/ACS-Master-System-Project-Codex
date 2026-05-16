from collections.abc import Callable, Sequence
from datetime import UTC, datetime

from app.domain.operational_accountability import (
    AccountabilityAuditEvidence,
    AccountabilityBlocker,
    AccountabilityEscalationType,
    AccountabilityEvidence,
    AccountabilityFailureCode,
    AccountabilityLifecycleState,
    AccountabilityResult,
    AccountabilityTraceability,
    EscalationResult,
    IncidentPreparationResult,
    InterventionEscalationEvidence,
    OperationalIncidentEvidence,
)
from app.models.audit_log import AuditLog
from app.models.operational_event_record import OperationalEventRecord
from app.models.route_assignment import RouteAssignment
from app.models.visit import Visit

DISPATCHED_STATUS = "dispatched"
GOVERNANCE_APPROVED_STATE = "operator_approved"
ACCOUNTABILITY_ROLES = {"admin", "operations_manager", "dispatcher_supervisor"}
INTERVENTION_ESCALATION_ROLES = {"admin", "operations_manager"}
TERMINAL_ACCOUNTABILITY_STATES = {
    AccountabilityLifecycleState.ESCALATION_REQUIRED.value,
    AccountabilityLifecycleState.INCIDENT_PREPARED.value,
    AccountabilityLifecycleState.AWAITING_OPERATIONAL_REVIEW.value,
    AccountabilityLifecycleState.CRITICAL_INTERVENTION_REQUIRED.value,
    AccountabilityLifecycleState.ARCHIVED.value,
}
RECONCILIATION_CONTEXT_STATES = {
    "reconciliation_required",
    "divergence_detected",
    "awaiting_manual_resolution",
}


class OperationalAccountabilityService:
    def __init__(self, *, now: Callable[[], datetime] | None = None) -> None:
        self.now = now or (lambda: datetime.now(UTC))

    def prepare_escalation(
        self,
        route_assignment: RouteAssignment,
        *,
        visit: Visit,
        operator_id: str | None,
        operator_role: str | None,
        escalation_type: AccountabilityEscalationType,
        operational_events: Sequence[OperationalEventRecord] = (),
    ) -> AccountabilityResult:
        target_state = (
            AccountabilityLifecycleState.CRITICAL_INTERVENTION_REQUIRED
            if escalation_type == AccountabilityEscalationType.MANUAL_INTERVENTION
            else AccountabilityLifecycleState.ESCALATION_REQUIRED
        )
        return self._evaluate_accountability(
            route_assignment,
            visit=visit,
            operator_id=operator_id,
            operator_role=operator_role,
            escalation_type=escalation_type,
            incident_type=None,
            operational_events=operational_events,
            target_state=target_state,
        )

    def prepare_incident(
        self,
        route_assignment: RouteAssignment,
        *,
        visit: Visit,
        operator_id: str | None,
        operator_role: str | None,
        incident_type: str,
        operational_events: Sequence[OperationalEventRecord] = (),
    ) -> AccountabilityResult:
        return self._evaluate_accountability(
            route_assignment,
            visit=visit,
            operator_id=operator_id,
            operator_role=operator_role,
            escalation_type=AccountabilityEscalationType.CRITICAL_DIVERGENCE,
            incident_type=incident_type,
            operational_events=operational_events,
            target_state=AccountabilityLifecycleState.INCIDENT_PREPARED,
        )

    def _evaluate_accountability(
        self,
        route_assignment: RouteAssignment,
        *,
        visit: Visit,
        operator_id: str | None,
        operator_role: str | None,
        escalation_type: AccountabilityEscalationType,
        incident_type: str | None,
        operational_events: Sequence[OperationalEventRecord],
        target_state: AccountabilityLifecycleState,
    ) -> AccountabilityResult:
        timestamp = self.now()
        traceability = accountability_traceability(route_assignment, visit, operator_id)
        escalation = escalation_result(route_assignment, escalation_type, target_state)
        incident = incident_preparation_result(route_assignment, incident_type, target_state)
        intervention = intervention_escalation_evidence(
            route_assignment,
            escalation_type=escalation_type,
            operator_role=operator_role,
            target_state=target_state,
        )
        operational_incident = operational_incident_evidence(
            route_assignment,
            incident_type,
            target_state,
        )
        audit = accountability_audit_evidence(
            route_assignment,
            state=target_state,
            escalation_type=escalation_type,
            incident_type=incident_type,
            operator_id=operator_id,
            operator_role=operator_role,
        )
        blockers = accountability_blockers(
            route_assignment,
            visit,
            operator_id=operator_id,
            operator_role=operator_role,
            escalation_type=escalation_type,
            target_state=target_state,
            operational_events=operational_events,
        )
        if any(
            blocker.code == AccountabilityFailureCode.DUPLICATE_ESCALATION for blocker in blockers
        ):
            return failed_accountability_result(
                route_assignment,
                state=AccountabilityLifecycleState.ACCOUNTABILITY_BLOCKED,
                traceability=traceability,
                escalation=escalation,
                incident=incident,
                intervention=intervention,
                operational_incident=operational_incident,
                audit=audit,
                blockers=blockers,
            )
        if blockers:
            apply_accountability_blocked(
                route_assignment,
                escalation,
                incident,
                intervention,
                operational_incident,
                audit,
                blockers,
                timestamp,
            )
            return failed_accountability_result(
                route_assignment,
                state=AccountabilityLifecycleState.ACCOUNTABILITY_BLOCKED,
                traceability=traceability,
                escalation=escalation,
                incident=incident,
                intervention=intervention,
                operational_incident=operational_incident,
                audit=audit,
                blockers=blockers,
            )

        apply_accountability_prepared(
            route_assignment,
            escalation,
            incident,
            intervention,
            operational_incident,
            audit,
            target_state,
            timestamp,
        )
        return AccountabilityResult(
            succeeded=True,
            state=target_state,
            traceability=traceability,
            evidence=accountability_evidence(route_assignment),
            escalation=escalation,
            incident=incident,
            intervention_escalation=intervention,
            operational_incident=operational_incident,
            audit=audit,
        )

    @staticmethod
    def build_accountability_audit_log(route_assignment: RouteAssignment) -> AuditLog:
        audit_snapshot = route_assignment.accountability_audit_snapshot or {}
        return AuditLog(
            action=audit_snapshot.get("action") or "operational_accountability.recorded",
            entity_type="route_assignment",
            entity_id=route_assignment.id,
            audit_correlation_id=route_assignment.audit_correlation_id,
            details={
                "route_assignment_id": str(route_assignment.id),
                "visit_id": str(route_assignment.visit_id) if route_assignment.visit_id else None,
                "job_id": str(route_assignment.job_id) if route_assignment.job_id else None,
                "technician_id": str(route_assignment.technician_id)
                if route_assignment.technician_id
                else None,
                "accountability_state": route_assignment.accountability_state,
                "operator_id": audit_snapshot.get("operator_id"),
                "escalation_type": audit_snapshot.get("escalation_type"),
                "incident_type": audit_snapshot.get("incident_type"),
                "escalation_execution": audit_snapshot.get("escalation_execution"),
                "incident_execution": audit_snapshot.get("incident_execution"),
                "external_api_calls": audit_snapshot.get("external_api_calls"),
            },
        )


def accountability_blockers(
    route_assignment: RouteAssignment,
    visit: Visit,
    *,
    operator_id: str | None,
    operator_role: str | None,
    escalation_type: AccountabilityEscalationType,
    target_state: AccountabilityLifecycleState,
    operational_events: Sequence[OperationalEventRecord],
) -> tuple[AccountabilityBlocker, ...]:
    blockers: list[AccountabilityBlocker] = []
    if route_assignment.id is None or route_assignment.visit_id != visit.id:
        blockers.append(
            AccountabilityBlocker(
                code=AccountabilityFailureCode.MISSING_ROUTE_ASSIGNMENT_LINKAGE,
                message="Route assignment must be linked to the Visit under accountability.",
            ),
        )
    if not (route_assignment.audit_correlation_id or visit.audit_correlation_id):
        blockers.append(
            AccountabilityBlocker(
                code=AccountabilityFailureCode.MISSING_AUDIT_CORRELATION,
                message="Operational accountability requires audit correlation continuity.",
            ),
        )
    if not operator_id:
        blockers.append(
            AccountabilityBlocker(
                code=AccountabilityFailureCode.MISSING_OPERATOR_ID,
                message="Operational accountability requires an explicit operator identity.",
            ),
        )
    if visit.visit_type == "water_emergency":
        blockers.append(
            AccountabilityBlocker(
                code=AccountabilityFailureCode.WATER_EMERGENCY_VISIT,
                message="Water Emergency work requires a separated accountability path.",
            ),
        )
    if visit.status == "review_required":
        blockers.append(
            AccountabilityBlocker(
                code=AccountabilityFailureCode.REVIEW_REQUIRED,
                message="Manual Review remains authoritative before accountability escalation.",
            ),
        )
    if visit.status != DISPATCHED_STATUS or route_assignment.dispatch_execution_state != (
        DISPATCHED_STATUS
    ):
        blockers.append(
            AccountabilityBlocker(
                code=AccountabilityFailureCode.INVALID_LIFECYCLE,
                message="Accountability preparation requires a dispatched operational lifecycle.",
                metadata={
                    "visit_status": visit.status,
                    "dispatch_execution_state": route_assignment.dispatch_execution_state,
                },
            ),
        )
    if not route_assignment_authorized(route_assignment):
        blockers.append(
            AccountabilityBlocker(
                code=AccountabilityFailureCode.UNAUTHORIZED_ROUTE_ASSIGNMENT,
                message="Only authorized Route Assignments can prepare accountability records.",
            ),
        )
    if not governance_approved(route_assignment):
        blockers.append(
            AccountabilityBlocker(
                code=AccountabilityFailureCode.GOVERNANCE_REQUIRED,
                message="Accountability escalation requires prior governance approval.",
                metadata={"governance_state": route_assignment.governance_state},
            ),
        )
    if escalation_type == AccountabilityEscalationType.MANUAL_INTERVENTION:
        if operator_role not in INTERVENTION_ESCALATION_ROLES:
            blockers.append(
                AccountabilityBlocker(
                    code=AccountabilityFailureCode.UNAUTHORIZED_INTERVENTION_ESCALATION,
                    message="Operator role cannot escalate manual intervention.",
                    metadata={"operator_role": operator_role},
                ),
            )
    elif operator_role not in ACCOUNTABILITY_ROLES:
        blockers.append(
            AccountabilityBlocker(
                code=AccountabilityFailureCode.UNAUTHORIZED_OPERATOR_ACTION,
                message="Operator role is not authorized for accountability preparation.",
                metadata={"operator_role": operator_role},
            ),
        )
    if route_assignment.accountability_state in TERMINAL_ACCOUNTABILITY_STATES:
        blockers.append(
            AccountabilityBlocker(
                code=AccountabilityFailureCode.DUPLICATE_ESCALATION,
                message="Accountability escalation or incident preparation already exists.",
                metadata={"accountability_state": route_assignment.accountability_state},
            ),
        )
    mutable_events = [
        str(event.id)
        for event in operational_events
        if not event.is_immutable or event.immutable_evidence_snapshot is None
    ]
    if mutable_events:
        blockers.append(
            AccountabilityBlocker(
                code=AccountabilityFailureCode.IMMUTABLE_HISTORY_VIOLATION,
                message="Operational event history must remain immutable during accountability.",
                metadata={"mutable_event_ids": mutable_events},
            ),
        )
    if not has_accountability_context(route_assignment, escalation_type, target_state):
        blockers.append(
            AccountabilityBlocker(
                code=AccountabilityFailureCode.NO_ACCOUNTABILITY_CONTEXT,
                message=(
                    "Accountability preparation requires escalation, incident, "
                    "or divergence context."
                ),
                metadata={
                    "escalation_type": escalation_type.value,
                    "target_state": target_state.value,
                },
            ),
        )
    return tuple(dedupe_blockers(blockers))


def apply_accountability_prepared(
    route_assignment: RouteAssignment,
    escalation: EscalationResult,
    incident: IncidentPreparationResult,
    intervention: InterventionEscalationEvidence,
    operational_incident: OperationalIncidentEvidence,
    audit: AccountabilityAuditEvidence,
    state: AccountabilityLifecycleState,
    timestamp: datetime,
) -> None:
    route_assignment.accountability_state = state.value
    route_assignment.escalation_preparation_snapshot = escalation.evidence
    route_assignment.incident_preparation_snapshot = incident.evidence
    route_assignment.operational_incident_snapshot = operational_incident.evidence
    route_assignment.intervention_escalation_snapshot = intervention.evidence
    route_assignment.accountability_evidence_snapshot = accountability_snapshot(
        route_assignment,
        state,
        timestamp,
    )
    route_assignment.escalation_blocker_snapshot = {}
    route_assignment.accountability_audit_snapshot = audit.evidence
    if state == AccountabilityLifecycleState.INCIDENT_PREPARED:
        route_assignment.incident_prepared_at = timestamp
    elif state == AccountabilityLifecycleState.CRITICAL_INTERVENTION_REQUIRED:
        route_assignment.critical_intervention_required_at = timestamp
    else:
        route_assignment.escalation_required_at = timestamp


def apply_accountability_blocked(
    route_assignment: RouteAssignment,
    escalation: EscalationResult,
    incident: IncidentPreparationResult,
    intervention: InterventionEscalationEvidence,
    operational_incident: OperationalIncidentEvidence,
    audit: AccountabilityAuditEvidence,
    blockers: tuple[AccountabilityBlocker, ...],
    timestamp: datetime,
) -> None:
    state = AccountabilityLifecycleState.ACCOUNTABILITY_BLOCKED
    route_assignment.accountability_state = state.value
    route_assignment.escalation_preparation_snapshot = escalation.evidence
    route_assignment.incident_preparation_snapshot = incident.evidence
    route_assignment.operational_incident_snapshot = operational_incident.evidence
    route_assignment.intervention_escalation_snapshot = intervention.evidence
    route_assignment.accountability_evidence_snapshot = accountability_snapshot(
        route_assignment,
        state,
        timestamp,
    )
    route_assignment.escalation_blocker_snapshot = blocker_snapshot(blockers, timestamp)
    route_assignment.accountability_audit_snapshot = audit.evidence | {
        "state": state.value,
        "action": "operational_accountability.blocked",
    }
    route_assignment.accountability_blocked_at = timestamp


def failed_accountability_result(
    route_assignment: RouteAssignment,
    *,
    state: AccountabilityLifecycleState,
    traceability: AccountabilityTraceability,
    escalation: EscalationResult,
    incident: IncidentPreparationResult,
    intervention: InterventionEscalationEvidence,
    operational_incident: OperationalIncidentEvidence,
    audit: AccountabilityAuditEvidence,
    blockers: tuple[AccountabilityBlocker, ...],
) -> AccountabilityResult:
    return AccountabilityResult(
        succeeded=False,
        state=state,
        traceability=traceability,
        escalation=escalation,
        incident=incident,
        intervention_escalation=intervention,
        operational_incident=operational_incident,
        audit=audit,
        failure_reasons=blockers,
        evidence=AccountabilityEvidence(
            accountability=route_assignment.accountability_evidence_snapshot or {},
            escalation=route_assignment.escalation_preparation_snapshot or escalation.evidence,
            incident=route_assignment.incident_preparation_snapshot or incident.evidence,
            intervention_escalation=route_assignment.intervention_escalation_snapshot
            or intervention.evidence,
            blockers=route_assignment.escalation_blocker_snapshot or {},
            audit=route_assignment.accountability_audit_snapshot or audit.evidence,
            failure_reasons=blockers,
        ),
    )


def escalation_result(
    route_assignment: RouteAssignment,
    escalation_type: AccountabilityEscalationType,
    state: AccountabilityLifecycleState,
) -> EscalationResult:
    required = state in {
        AccountabilityLifecycleState.ESCALATION_REQUIRED,
        AccountabilityLifecycleState.CRITICAL_INTERVENTION_REQUIRED,
    }
    evidence = {
        "state": state.value,
        "escalation_type": escalation_type.value,
        "escalation_required": required,
        "critical_divergence_detected": critical_divergence_detected(route_assignment),
        "source_replay_recovery_state": route_assignment.replay_recovery_state,
        "source_reconciliation_state": route_assignment.dispatch_reconciliation_state,
        "governance_state": route_assignment.governance_state,
        "escalation_execution": "not_executed",
        "automatic_escalation_execution": "not_executed",
        "incident_execution": "not_executed",
        "workflow_engine": "not_executed",
        "external_api_calls": "not_executed",
        "ai_authority": "none",
    }
    return EscalationResult(
        escalation_required=required,
        escalation_type=escalation_type,
        escalation_execution="not_executed",
        evidence=evidence,
    )


def incident_preparation_result(
    route_assignment: RouteAssignment,
    incident_type: str | None,
    state: AccountabilityLifecycleState,
) -> IncidentPreparationResult:
    prepared = state == AccountabilityLifecycleState.INCIDENT_PREPARED
    evidence = {
        "state": state.value,
        "incident_prepared": prepared,
        "incident_type": incident_type,
        "critical_divergence_detected": critical_divergence_detected(route_assignment),
        "source_replay_recovery_state": route_assignment.replay_recovery_state,
        "source_reconciliation_state": route_assignment.dispatch_reconciliation_state,
        "incident_execution": "not_executed",
        "automatic_incident_execution": "not_executed",
        "incident_engine": "not_executed",
        "external_api_calls": "not_executed",
        "ai_authority": "none",
    }
    return IncidentPreparationResult(
        incident_prepared=prepared,
        incident_type=incident_type,
        incident_execution="not_executed",
        evidence=evidence,
    )


def intervention_escalation_evidence(
    route_assignment: RouteAssignment,
    *,
    escalation_type: AccountabilityEscalationType,
    operator_role: str | None,
    target_state: AccountabilityLifecycleState,
) -> InterventionEscalationEvidence:
    required = (
        escalation_type == AccountabilityEscalationType.MANUAL_INTERVENTION
        or target_state == AccountabilityLifecycleState.CRITICAL_INTERVENTION_REQUIRED
    )
    authorized = bool(required and operator_role in INTERVENTION_ESCALATION_ROLES)
    evidence = {
        "intervention_escalation_required": required,
        "authorized_for_intervention_escalation": authorized,
        "operator_role": operator_role,
        "source_governance_state": route_assignment.governance_state,
        "source_replay_recovery_state": route_assignment.replay_recovery_state,
        "intervention_execution": "not_executed",
        "automatic_intervention_execution": "not_executed",
        "workflow_engine": "not_executed",
        "external_api_calls": "not_executed",
        "ai_authority": "none",
    }
    return InterventionEscalationEvidence(
        intervention_escalation_required=required,
        authorized_for_intervention_escalation=authorized,
        intervention_execution="not_executed",
        evidence=evidence,
    )


def operational_incident_evidence(
    route_assignment: RouteAssignment,
    incident_type: str | None,
    state: AccountabilityLifecycleState,
) -> OperationalIncidentEvidence:
    prepared = state == AccountabilityLifecycleState.INCIDENT_PREPARED
    evidence = {
        "incident_prepared": prepared,
        "incident_type": incident_type,
        "operational_incident_required": prepared or critical_divergence_detected(route_assignment),
        "source_reconciliation_state": route_assignment.dispatch_reconciliation_state,
        "source_replay_recovery_state": route_assignment.replay_recovery_state,
        "incident_execution": "not_executed",
        "automatic_incident_workflow": "not_executed",
        "workflow_engine": "not_executed",
        "external_api_calls": "not_executed",
        "ai_authority": "none",
    }
    return OperationalIncidentEvidence(
        incident_prepared=prepared,
        incident_type=incident_type,
        incident_execution="not_executed",
        evidence=evidence,
    )


def accountability_audit_evidence(
    route_assignment: RouteAssignment,
    *,
    state: AccountabilityLifecycleState,
    escalation_type: AccountabilityEscalationType,
    incident_type: str | None,
    operator_id: str | None,
    operator_role: str | None,
) -> AccountabilityAuditEvidence:
    action_by_state = {
        AccountabilityLifecycleState.ESCALATION_REQUIRED: (
            "operational_accountability.escalation_required"
        ),
        AccountabilityLifecycleState.INCIDENT_PREPARED: (
            "operational_accountability.incident_prepared"
        ),
        AccountabilityLifecycleState.CRITICAL_INTERVENTION_REQUIRED: (
            "operational_accountability.critical_intervention_required"
        ),
        AccountabilityLifecycleState.ACCOUNTABILITY_BLOCKED: ("operational_accountability.blocked"),
    }
    action = action_by_state.get(state, "operational_accountability.recorded")
    evidence = {
        "action": action,
        "state": state.value,
        "escalation_type": escalation_type.value,
        "incident_type": incident_type,
        "route_assignment_id": str(route_assignment.id) if route_assignment.id else None,
        "visit_id": str(route_assignment.visit_id) if route_assignment.visit_id else None,
        "job_id": str(route_assignment.job_id) if route_assignment.job_id else None,
        "audit_correlation_id": route_assignment.audit_correlation_id,
        "operator_id": operator_id,
        "operator_role": operator_role,
        "governance_state": route_assignment.governance_state,
        "escalation_execution": "not_executed",
        "incident_execution": "not_executed",
        "intervention_execution": "not_executed",
        "external_api_calls": "not_executed",
        "immutable_history_mutated": False,
        "manual_review_bypassed": False,
        "ai_authority": "none",
    }
    return AccountabilityAuditEvidence(
        action=action,
        operator_id=operator_id,
        operator_role=operator_role,
        evidence=evidence,
    )


def accountability_snapshot(
    route_assignment: RouteAssignment,
    state: AccountabilityLifecycleState,
    timestamp: datetime,
) -> dict[str, object]:
    governance_snapshot = route_assignment.governance_approval_snapshot or {}
    return {
        "state": state.value,
        "prepared_at": timestamp.isoformat(),
        "governance_state": route_assignment.governance_state,
        "governance_approved": governance_snapshot.get("approved") is True,
        "replay_recovery_state": route_assignment.replay_recovery_state,
        "dispatch_reconciliation_state": route_assignment.dispatch_reconciliation_state,
        "critical_divergence_detected": critical_divergence_detected(route_assignment),
        "manual_review_bypassed": False,
        "escalation_execution": "not_executed",
        "incident_execution": "not_executed",
        "intervention_execution": "not_executed",
        "workflow_engine": "not_executed",
        "external_api_calls": "not_executed",
        "immutable_history_mutated": False,
    }


def blocker_snapshot(
    blockers: tuple[AccountabilityBlocker, ...],
    timestamp: datetime,
) -> dict[str, object]:
    return {
        "state": AccountabilityLifecycleState.ACCOUNTABILITY_BLOCKED.value,
        "blocked_at": timestamp.isoformat(),
        "escalation_execution": "not_executed",
        "incident_execution": "not_executed",
        "intervention_execution": "not_executed",
        "external_api_calls": "not_executed",
        "immutable_history_mutated": False,
        "blockers": [
            {
                "code": blocker.code.value,
                "message": blocker.message,
                "metadata": blocker.metadata or {},
            }
            for blocker in blockers
        ],
    }


def accountability_evidence(route_assignment: RouteAssignment) -> AccountabilityEvidence:
    return AccountabilityEvidence(
        accountability=route_assignment.accountability_evidence_snapshot or {},
        escalation=route_assignment.escalation_preparation_snapshot or {},
        incident=route_assignment.incident_preparation_snapshot or {},
        intervention_escalation=route_assignment.intervention_escalation_snapshot or {},
        blockers=route_assignment.escalation_blocker_snapshot or {},
        audit=route_assignment.accountability_audit_snapshot or {},
    )


def accountability_traceability(
    route_assignment: RouteAssignment,
    visit: Visit,
    operator_id: str | None,
) -> AccountabilityTraceability:
    return AccountabilityTraceability(
        route_assignment_id=route_assignment.id,
        visit_id=visit.id,
        work_order_id=visit.work_order_id,
        job_id=route_assignment.job_id or visit.job_id,
        technician_id=route_assignment.technician_id or visit.technician_id,
        audit_correlation_id=route_assignment.audit_correlation_id or visit.audit_correlation_id,
        operator_id=operator_id,
    )


def route_assignment_authorized(route_assignment: RouteAssignment) -> bool:
    authorization_snapshot = route_assignment.dispatch_authorization_snapshot or {}
    execution_boundary_snapshot = route_assignment.dispatch_execution_boundary_snapshot or {}
    return bool(
        authorization_snapshot.get("authorized_for_dispatch")
        and execution_boundary_snapshot.get("authorized_for_dispatch")
    )


def governance_approved(route_assignment: RouteAssignment) -> bool:
    governance_snapshot = route_assignment.governance_approval_snapshot or {}
    return bool(
        route_assignment.governance_state == GOVERNANCE_APPROVED_STATE
        and governance_snapshot.get("approved") is True
    )


def critical_divergence_detected(route_assignment: RouteAssignment) -> bool:
    divergence_snapshot = route_assignment.dispatch_divergence_snapshot or {}
    mismatch_snapshot = route_assignment.dispatch_mismatch_snapshot or {}
    return bool(
        divergence_snapshot.get("critical_divergence")
        or divergence_snapshot.get("manual_resolution_required")
        or mismatch_snapshot.get("mismatch_count", 0)
        or route_assignment.dispatch_reconciliation_state in RECONCILIATION_CONTEXT_STATES
        or route_assignment.external_execution_failure_snapshot
        or route_assignment.external_failure_snapshot
    )


def has_accountability_context(
    route_assignment: RouteAssignment,
    escalation_type: AccountabilityEscalationType,
    target_state: AccountabilityLifecycleState,
) -> bool:
    if target_state == AccountabilityLifecycleState.INCIDENT_PREPARED:
        return critical_divergence_detected(route_assignment)
    if escalation_type == AccountabilityEscalationType.REPLAY_RECOVERY:
        return bool(
            route_assignment.replay_recovery_state
            in {
                "replay_prepared",
                "replay_blocked",
                "recovery_required",
                "awaiting_manual_recovery",
            }
            or route_assignment.replay_preparation_snapshot
            or route_assignment.recovery_coordination_snapshot
        )
    if escalation_type == AccountabilityEscalationType.ROLLBACK:
        return bool(
            route_assignment.replay_recovery_state == "rollback_prepared"
            or route_assignment.rollback_preparation_snapshot
        )
    if escalation_type == AccountabilityEscalationType.RECONCILIATION:
        return bool(
            route_assignment.dispatch_reconciliation_state in RECONCILIATION_CONTEXT_STATES
            or route_assignment.dispatch_divergence_snapshot
            or route_assignment.dispatch_mismatch_snapshot
        )
    return critical_divergence_detected(route_assignment)


def dedupe_blockers(
    blockers: list[AccountabilityBlocker],
) -> tuple[AccountabilityBlocker, ...]:
    deduped: list[AccountabilityBlocker] = []
    seen: set[AccountabilityFailureCode] = set()
    for blocker in blockers:
        if blocker.code in seen:
            continue
        deduped.append(blocker)
        seen.add(blocker.code)
    return tuple(deduped)
