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
