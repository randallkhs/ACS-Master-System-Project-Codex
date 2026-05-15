from __future__ import annotations

import json
import logging
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy.engine import make_url
from sqlalchemy.exc import ArgumentError

if TYPE_CHECKING:
    from app.core.config import Settings

REQUEST_SAFE_LOG_FIELDS = (
    "event",
    "request_id",
    "correlation_id",
    "method",
    "path",
    "status_code",
    "duration_ms",
)


class JsonFormatter(logging.Formatter):
    def __init__(self, settings: Settings) -> None:
        super().__init__()
        self.service_name = settings.service_name
        self.environment = settings.environment

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created, UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "service": self.service_name,
            "environment": self.environment,
        }

        for field_name in REQUEST_SAFE_LOG_FIELDS:
            value = getattr(record, field_name, None)
            if value is not None:
                payload[field_name] = value

        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)

        return json.dumps(payload, default=str, separators=(",", ":"))


def configure_logging(settings: Settings | str) -> None:
    if isinstance(settings, str):
        level_name = settings
        formatter: logging.Formatter = logging.Formatter(
            "%(asctime)s %(levelname)s [%(name)s] %(message)s",
        )
    else:
        level_name = settings.log_level
        if settings.log_format == "json":
            formatter = JsonFormatter(settings)
        else:
            formatter = logging.Formatter(
                "%(asctime)s %(levelname)s [%(name)s] %(message)s",
            )

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logging.basicConfig(
        level=getattr(logging, level_name.upper(), logging.INFO),
        handlers=[handler],
        force=True,
    )


def redact_url_credentials(url: str) -> str:
    try:
        parsed_url = make_url(url)
    except ArgumentError:
        return "<invalid-url>"
    return parsed_url.render_as_string(hide_password=True)
