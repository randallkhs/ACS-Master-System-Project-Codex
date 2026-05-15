from pathlib import Path


def test_initial_alembic_migration_exists() -> None:
    migration_files = list(Path("app/db/migrations/versions").glob("*.py"))

    assert migration_files, "Expected an initial Alembic migration for foundational tables"
