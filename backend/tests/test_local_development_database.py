from __future__ import annotations

import pytest

from app.core.config import Settings
from scripts.check_local_database import _read_alembic_revision, validate_local_database_settings
from scripts.seed_dashboard_dev_data import (
    SEED_SOURCE_SYSTEM,
    build_dashboard_dev_seed_records,
    validate_seed_settings,
)
from scripts.verify_dashboard_endpoints import verify_endpoint


def test_dashboard_dev_seed_refuses_production() -> None:
    settings = Settings(
        environment="production",
        database_url="postgresql+psycopg://acs_user:secure-pass@db.internal:5432/acs_fsm",
    )

    with pytest.raises(RuntimeError, match="production"):
        validate_seed_settings(settings)


def test_dashboard_dev_seed_requires_local_database_host() -> None:
    settings = Settings(
        environment="development",
        database_url="postgresql+psycopg://acs_user:secure-pass@db.internal:5432/acs_fsm_dev",
    )

    with pytest.raises(RuntimeError, match="local PostgreSQL host"):
        validate_seed_settings(settings)


def test_dashboard_dev_seed_refuses_placeholder_credentials() -> None:
    settings = Settings(
        environment="development",
        database_url="postgresql+psycopg://acs_user:change-me@127.0.0.1:5432/acs_fsm_dev",
    )

    with pytest.raises(RuntimeError, match="placeholder database credentials"):
        validate_seed_settings(settings)


def test_dashboard_dev_seed_accepts_local_development_database_url() -> None:
    settings = Settings(
        environment="development",
        database_url="postgresql+psycopg://acs_fsm_dev:acs_fsm_dev@127.0.0.1:5432/acs_fsm_dev",
    )

    validate_seed_settings(settings)


def test_local_database_check_uses_same_local_safety_boundary() -> None:
    settings = Settings(
        environment="development",
        database_url="postgresql+psycopg://acs_fsm_dev:acs_fsm_dev@127.0.0.1:5432/acs_fsm_dev",
    )

    validate_local_database_settings(settings)

    unsafe_settings = Settings(
        environment="development",
        database_url="postgresql+psycopg://acs_user:secure-pass@db.internal:5432/acs_fsm_dev",
    )

    with pytest.raises(RuntimeError, match="local PostgreSQL host"):
        validate_local_database_settings(unsafe_settings)


def test_local_database_check_reports_unmigrated_database_as_connected() -> None:
    class FakeScalarResult:
        def __init__(self, value: str | None) -> None:
            self.value = value

        def scalar_one_or_none(self) -> str | None:
            return self.value

    class FakeConnection:
        def __init__(self) -> None:
            self.queries: list[str] = []

        def execute(self, statement):
            query = str(statement)
            self.queries.append(query)
            if "to_regclass" in query:
                return FakeScalarResult(None)
            msg = "version table must not be queried before migrations exist"
            raise AssertionError(msg)

    connection = FakeConnection()

    assert _read_alembic_revision(connection) is None
    assert connection.queries == ["select to_regclass('public.alembic_version')"]


def test_dashboard_dev_seed_records_are_synthetic_and_read_only() -> None:
    seed_records = build_dashboard_dev_seed_records()
    source_systems = {
        record.__dict__["source_system"]
        for record in seed_records.records
        if "source_system" in record.__dict__
    }
    event_fingerprints = {
        record.__dict__["event_fingerprint"]
        for record in seed_records.records
        if "event_fingerprint" in record.__dict__
    }

    assert seed_records.record_count == 18
    assert source_systems == {SEED_SOURCE_SYSTEM}
    assert "module27-dashboard-demo-dispatched" in event_fingerprints
    assert "module27-dashboard-demo-adapter-prepared" in event_fingerprints

    route_assignment = next(
        record
        for record in seed_records.records
        if getattr(record, "external_failure_snapshot", None)
    )
    assert route_assignment.external_failure_snapshot["provider_execution"] == "not_executed"
    assert route_assignment.retry_preparation_snapshot["retry_execution"] == "not_executed"


def test_dashboard_endpoint_verifier_uses_get_only(monkeypatch) -> None:
    captured_methods: list[str] = []

    class FakeResponse:
        status = 200

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def read(self) -> bytes:
            return b'{"status":"ok"}'

    def fake_urlopen(request, *, timeout):
        captured_methods.append(request.get_method())
        assert timeout == 2.0
        return FakeResponse()

    monkeypatch.setattr("scripts.verify_dashboard_endpoints.urlopen", fake_urlopen)

    result = verify_endpoint("http://127.0.0.1:8000", "/api/v1/health", timeout=2.0)

    assert result.ok
    assert result.status_code == 200
    assert result.response_keys == ("status",)
    assert captured_methods == ["GET"]
