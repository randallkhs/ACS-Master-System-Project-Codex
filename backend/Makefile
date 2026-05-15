PYTHON ?= ../.venv/bin/python
FASTAPI ?= ../.venv/bin/fastapi
ALEMBIC ?= ../.venv/bin/alembic
MIGRATION_MESSAGE ?= describe migration

.PHONY: install dev run lint format format-check test migrate migration history compileall verify

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

verify: lint format-check test history compileall
