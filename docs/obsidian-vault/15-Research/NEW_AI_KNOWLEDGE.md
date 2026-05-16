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
  - https://tailwindcss.com/docs/installation/using-postcss
- Summary:
  - Next.js App Router Server Components can read server-only environment variables and use server-side `fetch` for backend data access.
  - Dashboard API base URLs should remain environment-driven instead of hardcoded, especially for future Apache reverse-proxy and VPS deployment.
  - Tailwind CSS v4 uses the `tailwindcss` package with the `@tailwindcss/postcss` PostCSS plugin and `@import "tailwindcss"` in the global CSS entrypoint.
  - For ACS dashboard screens, the frontend should consume backend read models and avoid duplicating workflow, blocker, Manual Review, integration, or AI authority in components.
- Applicable projects:
  - ACS-FSM
- Confidence:
  - High
- Notes:
  - Recheck before production deployment or major Next/Tailwind upgrades because framework setup details can shift between releases.
