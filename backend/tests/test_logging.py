import json
import logging

from app.core.config import Settings
from app.core.logging import JsonFormatter, redact_url_credentials


def test_json_formatter_emits_request_safe_structured_fields() -> None:
    settings = Settings(
        environment="testing",
        database_url="postgresql+psycopg://acs_user:acs_pass@db.internal:5432/acs_fsm_test",
    )
    formatter = JsonFormatter(settings)
    record = logging.LogRecord(
        name="app.test",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="request.completed",
        args=(),
        exc_info=None,
    )
    record.request_id = "req-123"
    record.method = "GET"
    record.path = "/api/v1/health"
    record.status_code = 200

    payload = json.loads(formatter.format(record))

    assert payload["message"] == "request.completed"
    assert payload["level"] == "INFO"
    assert payload["service"] == "acs-fsm-backend"
    assert payload["environment"] == "testing"
    assert payload["request_id"] == "req-123"
    assert payload["method"] == "GET"
    assert payload["path"] == "/api/v1/health"
    assert "query" not in payload


def test_database_url_redaction_removes_credentials() -> None:
    redacted = redact_url_credentials(
        "postgresql+psycopg://acs_user:secret-pass@db.internal:5432/acs_fsm",
    )

    assert "secret-pass" not in redacted
    assert redacted == "postgresql+psycopg://acs_user:***@db.internal:5432/acs_fsm"
