# ACS FSM Backend

FastAPI backend foundation for the Apple Cleaning Systems FSM platform.

This module is Phase 0 scaffolding only. It does not implement Calendar, Sheets, FastField, Verizon Connect, AI, routing, or dispatch business workflows yet.

## Architecture

- FastAPI application package in `app/`
- API routes under `app/api/v1/`
- Pydantic Settings configuration in `app/core/config.py`
- SQLAlchemy 2 models in `app/models/`
- PostgreSQL session foundation in `app/db/session.py`
- Alembic migration environment in `app/db/migrations/`
- External integrations isolated under `app/adapters/`
- Business service placeholders under `app/services/`

## Local Setup

From the repository root:

```bash
python3 -m venv .venv
cd backend
../.venv/bin/python -m pip install -r requirements-dev.txt
```

Copy `backend/.env.example` to `backend/.env` for local development, then set a real PostgreSQL URL.

Do not commit `.env` files or production secrets.

## Run API

From `backend/`:

```bash
../.venv/bin/fastapi dev app/main.py
```

Health check:

```text
GET /api/v1/health
```

For Apache or another reverse proxy, configure the deployment process to pass proxy headers at the ASGI server layer and set `ACS_FSM_PROXY_ROOT_PATH` only if the backend is mounted under a path prefix.

## Migrations

From `backend/`:

```bash
../.venv/bin/alembic revision --autogenerate -m "create foundational tables"
../.venv/bin/alembic upgrade head
```

Alembic reads `ACS_FSM_DATABASE_URL` through the backend settings system.

## Verification

From `backend/`:

```bash
../.venv/bin/ruff check app tests
../.venv/bin/python -m pytest -q
```

## Safety Rules

- Database is the source of truth.
- Manual Review is a core safety system.
- AI is advisory only.
- External systems are adapters only.
- Uncertain jobs must never auto-dispatch.
