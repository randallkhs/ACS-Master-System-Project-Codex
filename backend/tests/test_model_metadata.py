from app.db.base import Base


def test_foundational_domain_tables_are_registered() -> None:
    expected_tables = {
        "customers",
        "properties",
        "jobs",
        "work_orders",
        "visits",
        "technicians",
        "route_assignments",
        "water_emergencies",
        "review_items",
        "intake_processing_records",
        "job_creation_records",
        "operational_event_records",
        "audit_logs",
    }

    assert expected_tables.issubset(set(Base.metadata.tables))


def test_manual_review_table_keeps_safety_fields() -> None:
    columns = Base.metadata.tables["review_items"].columns

    assert "reason_code" in columns
    assert "confidence_score" in columns
    assert "status" in columns
    assert "operator_decision" in columns


def test_customer_table_supports_documented_contacts_and_tags() -> None:
    columns = Base.metadata.tables["customers"].columns

    assert "billing_contact" in columns
    assert "property_manager_contact" in columns
    assert "tags" in columns


def test_technician_table_supports_vehicle_and_availability_context() -> None:
    columns = Base.metadata.tables["technicians"].columns

    assert "vehicle_label" in columns
    assert "availability_status" in columns


def test_work_orders_and_visits_support_multiple_technicians() -> None:
    tables = Base.metadata.tables

    assert "work_order_technicians" in tables
    assert "work_order_id" in tables["work_order_technicians"].columns
    assert "technician_id" in tables["work_order_technicians"].columns

    assert "visit_technicians" in tables
    assert "visit_id" in tables["visit_technicians"].columns
    assert "technician_id" in tables["visit_technicians"].columns


def test_route_assignments_can_store_drive_time_estimates() -> None:
    columns = Base.metadata.tables["route_assignments"].columns

    assert "estimated_drive_time_minutes" in columns


def test_route_assignments_store_dispatch_authorization_traceability() -> None:
    columns = Base.metadata.tables["route_assignments"].columns

    expected_columns = {
        "route_group_key",
        "audit_correlation_id",
        "route_grouping_snapshot",
        "route_assignment_readiness_snapshot",
        "technician_route_compatibility_snapshot",
        "dispatch_authorization_snapshot",
        "dispatch_execution_boundary_snapshot",
        "deterministic_evidence_snapshot",
        "authorization_prepared_at",
        "authorized_for_dispatch_at",
    }

    assert expected_columns.issubset(set(columns.keys()))


def test_route_assignments_store_dispatch_execution_traceability() -> None:
    columns = Base.metadata.tables["route_assignments"].columns

    expected_columns = {
        "dispatch_execution_state",
        "dispatch_execution_snapshot",
        "dispatch_lifecycle_snapshot",
        "dispatch_audit_snapshot",
        "dispatched_at",
        "dispatch_failed_at",
    }

    assert expected_columns.issubset(set(columns.keys()))


def test_route_assignments_store_external_adapter_traceability() -> None:
    columns = Base.metadata.tables["route_assignments"].columns

    expected_columns = {
        "external_adapter_state",
        "external_adapter_request_snapshot",
        "external_adapter_payload_snapshot",
        "external_adapter_lifecycle_snapshot",
        "external_adapter_evidence_snapshot",
        "external_adapter_audit_snapshot",
        "external_adapter_prepared_at",
        "external_adapter_failed_at",
    }

    assert expected_columns.issubset(set(columns.keys()))


def test_route_assignments_store_external_confirmation_and_recovery_traceability() -> None:
    columns = Base.metadata.tables["route_assignments"].columns

    expected_columns = {
        "external_confirmation_state",
        "external_confirmation_snapshot",
        "external_confirmation_lifecycle_snapshot",
        "external_confirmation_audit_snapshot",
        "external_failure_snapshot",
        "retry_preparation_snapshot",
        "reconciliation_snapshot",
        "external_confirmed_at",
        "external_confirmation_failed_at",
        "retry_prepared_at",
        "reconciliation_required_at",
    }

    assert expected_columns.issubset(set(columns.keys()))


def test_manual_review_items_can_target_non_job_entities() -> None:
    columns = Base.metadata.tables["review_items"].columns

    assert "entity_type" in columns
    assert "entity_id" in columns


def test_manual_review_table_supports_persistent_queue_traceability() -> None:
    columns = Base.metadata.tables["review_items"].columns

    expected_columns = {
        "severity",
        "review_reasons",
        "confidence_snapshot",
        "operator_notes",
        "reviewed_at",
        "deferred_until",
        "intake_processing_state",
        "source_system",
        "source_id",
        "warning_snapshot",
        "normalization_snapshot",
        "validation_snapshot",
        "audit_correlation_id",
        "review_metadata",
    }

    assert expected_columns.issubset(set(columns.keys()))


def test_audit_logs_timestamp_events_by_default() -> None:
    columns = Base.metadata.tables["audit_logs"].columns

    assert columns["occurred_at"].server_default is not None
    assert "audit_correlation_id" in columns


def test_intake_processing_records_store_orchestration_traceability() -> None:
    columns = Base.metadata.tables["intake_processing_records"].columns

    expected_columns = {
        "source_system",
        "source_id",
        "lifecycle_state",
        "orchestration_state",
        "review_item_id",
        "audit_correlation_id",
        "raw_payload_snapshot",
        "orchestration_result_snapshot",
        "dispatch_eligibility_snapshot",
        "normalized_snapshot",
        "validation_snapshot",
        "confidence_snapshot",
        "review_snapshot",
        "warning_snapshot",
        "deterministic_evidence_snapshot",
        "review_linkage_snapshot",
        "dispatch_eligible",
        "requires_review",
        "blocked",
        "unsafe",
        "water_emergency_separated",
    }

    assert expected_columns.issubset(set(columns.keys()))


def test_job_creation_records_link_intake_to_jobs_with_traceability() -> None:
    columns = Base.metadata.tables["job_creation_records"].columns

    expected_columns = {
        "intake_processing_record_id",
        "job_id",
        "review_item_id",
        "lifecycle_state",
        "audit_correlation_id",
        "creation_snapshot",
        "intake_snapshot",
        "orchestration_snapshot",
        "dispatch_eligibility_snapshot",
        "review_linkage_snapshot",
        "deterministic_evidence_snapshot",
        "lifecycle_metadata",
        "created_from_intake_at",
    }

    assert expected_columns.issubset(set(columns.keys()))


def test_work_orders_store_generation_traceability() -> None:
    columns = Base.metadata.tables["work_orders"].columns

    expected_columns = {
        "job_creation_record_id",
        "review_item_id",
        "audit_correlation_id",
        "generation_snapshot",
        "intake_snapshot",
        "orchestration_snapshot",
        "dispatch_eligibility_snapshot",
        "review_linkage_snapshot",
        "deterministic_evidence_snapshot",
        "lifecycle_metadata",
        "generated_from_job_at",
    }

    assert expected_columns.issubset(set(columns.keys()))


def test_visits_store_work_order_linkage_and_generation_traceability() -> None:
    columns = Base.metadata.tables["visits"].columns

    expected_columns = {
        "work_order_id",
        "audit_correlation_id",
        "generation_snapshot",
        "work_order_snapshot",
        "review_linkage_snapshot",
        "deterministic_evidence_snapshot",
        "lifecycle_metadata",
        "generated_from_work_order_at",
    }

    assert expected_columns.issubset(set(columns.keys()))


def test_visits_store_assignment_and_scheduling_preparation_snapshots() -> None:
    columns = Base.metadata.tables["visits"].columns

    expected_columns = {
        "assignment_readiness_snapshot",
        "technician_compatibility_snapshot",
        "scheduling_readiness_snapshot",
        "operational_readiness_snapshot",
        "assignment_prepared_at",
        "scheduling_prepared_at",
    }

    assert expected_columns.issubset(set(columns.keys()))


def test_visits_store_routing_and_dispatch_preparation_snapshots() -> None:
    columns = Base.metadata.tables["visits"].columns

    expected_columns = {
        "routing_readiness_snapshot",
        "dispatch_readiness_snapshot",
        "technician_readiness_snapshot",
        "visit_dispatch_readiness_snapshot",
        "routing_prepared_at",
        "dispatch_prepared_at",
    }

    assert expected_columns.issubset(set(columns.keys()))
