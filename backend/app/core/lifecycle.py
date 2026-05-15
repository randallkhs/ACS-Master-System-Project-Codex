from __future__ import annotations

import logging
from collections.abc import AsyncIterator, Callable
from contextlib import asynccontextmanager
from dataclasses import dataclass
from datetime import UTC, datetime

from fastapi import FastAPI

from app.core.config import Settings

logger = logging.getLogger("app.lifecycle")


@dataclass
class HealthState:
    ready: bool = False
    started_at: datetime | None = None
    shutdown_at: datetime | None = None

    def mark_ready(self) -> None:
        self.ready = True
        self.started_at = datetime.now(UTC)
        self.shutdown_at = None

    def mark_shutdown(self) -> None:
        self.ready = False
        self.shutdown_at = datetime.now(UTC)

    def as_payload(self, settings: Settings) -> dict[str, str | bool | None]:
        return {
            "status": "ok" if self.ready else "starting",
            "service": settings.service_name,
            "environment": settings.environment,
            "version": settings.app_version,
            "ready": self.ready,
            "started_at": self.started_at.isoformat() if self.started_at else None,
        }


def create_lifespan(settings: Settings) -> Callable[[FastAPI], AsyncIterator[None]]:
    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        app.state.health.mark_ready()
        logger.info(
            "app.startup",
            extra={
                "event": "app.startup",
                "environment": settings.environment,
            },
        )
        try:
            yield
        finally:
            app.state.health.mark_shutdown()
            logger.info(
                "app.shutdown",
                extra={
                    "event": "app.shutdown",
                    "environment": settings.environment,
                },
            )

    return lifespan
