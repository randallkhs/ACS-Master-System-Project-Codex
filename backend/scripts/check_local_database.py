from __future__ import annotations

import json
from dataclasses import asdict, dataclass

from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url

from app.core.config import LOCAL_DATABASE_HOSTS, PLACEHOLDER_DATABASE_PASSWORDS, Settings


@dataclass(frozen=True)
class LocalDatabaseCheckResult:
    connected: bool
    migrated: bool
    database_url: str
    alembic_revision: str | None
    error: str | None = None


def check_local_database(settings: Settings) -> LocalDatabaseCheckResult:
    validate_local_database_settings(settings)

    engine = create_engine(
        settings.database_url,
        echo=False,
        pool_pre_ping=settings.database_pool_pre_ping,
    )
    with engine.connect() as connection:
        connection.execute(text("select 1"))
        alembic_revision = connection.execute(
            text("select version_num from alembic_version limit 1"),
        ).scalar_one_or_none()

    return LocalDatabaseCheckResult(
        connected=True,
        migrated=bool(alembic_revision),
        database_url=make_url(settings.database_url).render_as_string(hide_password=True),
        alembic_revision=alembic_revision,
    )


def validate_local_database_settings(settings: Settings) -> None:
    database_url = make_url(settings.database_url)
    host = (database_url.host or "").lower()
    password = database_url.password or ""

    if settings.is_production:
        raise RuntimeError("local database check refuses to run in production")
    if host not in LOCAL_DATABASE_HOSTS or host == "0.0.0.0":
        raise RuntimeError("local database check requires a local PostgreSQL host")
    if ".example." in host or host.startswith("db.example"):
        raise RuntimeError("local database check refuses placeholder example hosts")
    if password in PLACEHOLDER_DATABASE_PASSWORDS:
        raise RuntimeError("local database check refuses placeholder database credentials")


def main() -> int:
    settings = Settings()
    try:
        result = check_local_database(settings)
        exit_code = 0
    except Exception as exc:
        redacted_database_url = make_url(settings.database_url).render_as_string(
            hide_password=True,
        )
        result = LocalDatabaseCheckResult(
            connected=False,
            migrated=False,
            database_url=redacted_database_url,
            alembic_revision=None,
            error=str(exc).replace(settings.database_url, redacted_database_url),
        )
        exit_code = 1
    print(json.dumps(asdict(result), indent=2, sort_keys=True))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
