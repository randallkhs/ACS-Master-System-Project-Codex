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

## Topic: Next.js App Router And Tailwind Frontend Foundation Patterns

- Date learned: 2026-05-16
- Category: frontend
- Recheck after: 2026-07-15
- Source links:
  - https://nextjs.org/docs/app/guides/environment-variables
  - https://nextjs.org/docs/app/getting-started/fetching-data
  - https://fastapi.tiangolo.com/tutorial/cors/
  - https://tailwindcss.com/docs/installation/using-postcss
- Summary:
  - Next.js App Router Server Components can read server-only environment variables and use server-side `fetch` for backend data access.
  - Dashboard API base URLs should remain environment-driven instead of hardcoded, especially for future Apache reverse-proxy and VPS deployment.
  - Server-side dashboard reads do not require exposing the backend URL through `NEXT_PUBLIC_`; browser-side API calls would need explicit backend CORS configuration later.
  - Tailwind CSS v4 uses the `tailwindcss` package with the `@tailwindcss/postcss` PostCSS plugin and `@import "tailwindcss"` in the global CSS entrypoint.
  - For ACS dashboard screens, the frontend should consume backend read models and avoid duplicating workflow, blocker, Manual Review, integration, or AI authority in components.
- Applicable projects:
  - ACS-FSM
- Confidence:
  - High
- Notes:
  - Recheck before production deployment or major Next/Tailwind upgrades because framework setup details can shift between releases.

## Topic: Local PostgreSQL Migration And Dashboard Verification Workflow

- Date learned: 2026-05-16
- Category: backend/database
- Recheck after: 2026-07-15
- Source links:
  - https://alembic.sqlalchemy.org/en/latest/tutorial.html
  - https://docs.sqlalchemy.org/en/20/core/engines.html
  - https://docs.sqlalchemy.org/en/20/dialects/postgresql.html
  - https://nextjs.org/docs/app/guides/environment-variables
- Summary:
  - Alembic migration environments can set `sqlalchemy.url` from application settings, and `alembic upgrade head` applies revisions to the configured database.
  - SQLAlchemy 2 PostgreSQL URLs with psycopg use the `postgresql+psycopg://user:password@host:port/dbname` shape.
  - ACS local dashboard verification should keep the database URL and frontend backend URL environment-driven, with local defaults documented only for development.
  - Next.js server-side dashboard fetches can keep backend origins in server-only environment variables; browser-side fetching remains a separate CORS/public-runtime decision.
- Applicable projects:
  - ACS-FSM
- Confidence:
  - High
- Notes:
  - Recheck before introducing production migration automation, integration-test database orchestration, or browser-side dashboard fetching.
