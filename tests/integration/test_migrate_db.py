"""Tests d'intégration des migrations contre un vrai PostgreSQL (DB-001)."""

import shutil

import pytest
from sqlalchemy import text

from cip.db.migrate import MIGRATIONS_DIR, MigrationError, migrate, status

pytestmark = pytest.mark.integration

EXPECTED_SCHEMAS = {"raw", "staging", "analytics", "app"}


def _schemas(engine) -> set[str]:
    with engine.connect() as conn:
        rows = conn.execute(text("SELECT schema_name FROM information_schema.schemata"))
        return {r[0] for r in rows}


def _snapshot(engine):
    with engine.connect() as conn:
        return conn.execute(
            text("SELECT version, filename, checksum FROM app.schema_migration ORDER BY version")
        ).all()


def test_migrate_creates_the_four_layers(pg_engine):
    applied = migrate(pg_engine)
    assert "0001_create_schemas.sql" in applied
    assert _schemas(pg_engine) >= EXPECTED_SCHEMAS


def test_migrate_twice_gives_same_state(pg_engine):
    migrate(pg_engine)
    first = (_schemas(pg_engine), _snapshot(pg_engine))
    assert migrate(pg_engine) == []  # rien à rejouer
    assert (_schemas(pg_engine), _snapshot(pg_engine)) == first


def test_status_reports_pending_then_applied(pg_engine):
    assert all(state == "en attente" for _, state in status(pg_engine))
    migrate(pg_engine)
    assert all(state == "appliquée" for _, state in status(pg_engine))


def test_modified_migration_is_detected(pg_engine, tmp_path):
    for f in MIGRATIONS_DIR.glob("*.sql"):
        shutil.copy(f, tmp_path / f.name)
    migrate(pg_engine, tmp_path)
    target = tmp_path / "0001_create_schemas.sql"
    target.write_text(target.read_text() + "\n-- modification interdite\n")
    with pytest.raises(MigrationError, match="modifiée après son application"):
        migrate(pg_engine, tmp_path)


def test_failing_migration_is_rolled_back(pg_engine, tmp_path):
    (tmp_path / "0001_ok.sql").write_text("CREATE SCHEMA demo_ok;")
    (tmp_path / "0002_broken.sql").write_text(
        "CREATE SCHEMA demo_partial; SELECT * FROM table_inexistante;"
    )
    with pytest.raises(MigrationError, match="0002_broken.sql"):
        migrate(pg_engine, tmp_path)
    schemas = _schemas(pg_engine)
    assert "demo_ok" in schemas  # 0001 validée
    assert "demo_partial" not in schemas  # 0002 annulée entièrement
    assert [row.version for row in _snapshot(pg_engine)] == [1]
