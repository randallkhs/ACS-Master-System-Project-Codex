# New AI Knowledge

This file stores reusable technical knowledge learned from internet research, Context7, official docs, SDK docs, API docs, and other current sources.

Each entry must include:
- Date learned
- Category
- Recheck after date
- Source links
- Summary
- Confidence level

Do not store long documentation copies here.
Store concise implementation-relevant knowledge only.

---

## Entries

## Topic: Phase 0 Backend Library Scaffold Patterns

- Date learned: 2026-05-15
- Category: backend
- Recheck after: 2026-07-14
- Source links:
  - https://github.com/fastapi/fastapi/blob/master/docs/en/docs/advanced/behind-a-proxy.md
  - https://github.com/pydantic/pydantic-settings/blob/main/docs/index.md
  - https://docs.sqlalchemy.org/en/20/orm/declarative_tables.html
  - https://alembic.sqlalchemy.org/en/latest/tutorial.html
- Summary:
  - FastAPI supports reverse-proxy deployments with `root_path` and proxy-header handling at the ASGI server layer.
  - Pydantic Settings v2 uses `SettingsConfigDict` for env files, env prefixes, nested delimiters, and env parsing behavior.
  - SQLAlchemy 2 recommends typed declarative models with `DeclarativeBase`, `Mapped`, and `mapped_column`.
  - Alembic migration environments should load application model metadata as `target_metadata` and can receive the database URL through application settings.
- Applicable projects:
  - ACS-FSM
- Confidence:
  - High
- Notes:
  - Keep deployment-specific proxy/header handling out of application business logic; configure it through environment and server startup.
