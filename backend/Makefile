PYTHON ?= ../.venv/bin/python
FASTAPI ?= ../.venv/bin/fastapi
ALEMBIC ?= ../.venv/bin/alembic
MIGRATION_MESSAGE ?= describe migration

.PHONY: install dev run lint format format-check test migrate migration history compileall db-check seed-dashboard dashboard-check verify

install:
	$(PYTHON) -m pip install -e ".[dev]"

dev:
	$(FASTAPI) dev app/main.py

run:
	$(FASTAPI) run app/main.py

lint:
	$(PYTHON) -m ruff check .

format:
	$(PYTHON) -m ruff format .

format-check:
	$(PYTHON) -m ruff format --check .

test:
	$(PYTHON) -m pytest -q

migrate:
	$(ALEMBIC) upgrade head

migration:
	$(ALEMBIC) revision --autogenerate -m "$(MIGRATION_MESSAGE)"

history:
	$(ALEMBIC) history

compileall:
	$(PYTHON) -m compileall app tests

db-check:
	$(PYTHON) -m scripts.check_local_database

seed-dashboard:
	$(PYTHON) -m scripts.seed_dashboard_dev_data --confirm-dev-seed

dashboard-check:
	$(PYTHON) -m scripts.verify_dashboard_endpoints

verify: lint format-check test history compileall
