"""Tests unitaires de la découverte des migrations (sans base de données)."""

import pytest

from cip.db.migrate import MIGRATIONS_DIR, MigrationError, discover


def test_project_migrations_are_valid_and_ordered():
    migrations = discover(MIGRATIONS_DIR)
    assert migrations, "aucune migration trouvée"
    versions = [m.version for m in migrations]
    assert versions == sorted(versions)
    assert migrations[0].filename == "0001_create_schemas.sql"
    assert all(len(m.checksum) == 64 for m in migrations)


def test_invalid_filename_is_rejected(tmp_path):
    (tmp_path / "create_tables.sql").write_text("SELECT 1;")
    with pytest.raises(MigrationError, match="Nom de migration invalide"):
        discover(tmp_path)


def test_duplicate_version_is_rejected(tmp_path):
    (tmp_path / "0001_a.sql").write_text("SELECT 1;")
    (tmp_path / "0001_b.sql").write_text("SELECT 2;")
    with pytest.raises(MigrationError, match="en double"):
        discover(tmp_path)


def test_checksum_changes_with_content(tmp_path):
    f = tmp_path / "0001_a.sql"
    f.write_text("SELECT 1;")
    before = discover(tmp_path)[0].checksum
    f.write_text("SELECT 2;")
    assert discover(tmp_path)[0].checksum != before


def test_cli_reports_unreachable_database_cleanly(monkeypatch):
    from typer.testing import CliRunner

    from cip.cli import app
    from cip.config import get_settings

    monkeypatch.setenv("POSTGRES_HOST", "127.0.0.1")
    monkeypatch.setenv("POSTGRES_PORT", "1")  # aucun serveur n'écoute ici
    get_settings.cache_clear()
    try:
        result = CliRunner().invoke(app, ["db", "status"])
    finally:
        get_settings.cache_clear()
    assert result.exit_code == 3
    assert "PostgreSQL injoignable" in result.output
    assert "Traceback" not in result.output
