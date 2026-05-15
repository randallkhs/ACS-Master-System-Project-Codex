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
