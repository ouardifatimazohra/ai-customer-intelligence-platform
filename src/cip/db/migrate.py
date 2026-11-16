"""Exécuteur de migrations SQL versionnées.

Règles :
- Fichiers `database/migrations/NNNN_description.sql`, appliqués par ordre de numéro.
- Chaque migration est appliquée **une seule fois**, dans une transaction (tout ou rien),
  et enregistrée dans `app.schema_migration` avec son empreinte SHA-256.
- Une migration déjà appliquée ne doit plus être modifiée : si son contenu change,
  l'exécution s'arrête (on crée une nouvelle migration à la place).
- Un verrou consultatif PostgreSQL empêche deux exécutions simultanées.

Pourquoi pas Alembic ? Pour une dizaine de tables, des fichiers SQL lisibles et un
runner de ~100 lignes sont plus simples à expliquer et à auditer.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from pathlib import Path

from sqlalchemy import Connection, Engine, text

from cip.log import get_logger

log = get_logger(__name__)

MIGRATIONS_DIR = Path(__file__).resolve().parents[3] / "database" / "migrations"
_FILENAME = re.compile(r"^(?P<version>\d{4})_(?P<name>[a-z0-9_]+)\.sql$")
_LOCK_KEY = 4242_0001  # identifiant arbitraire du verrou consultatif

_BOOTSTRAP = """
CREATE SCHEMA IF NOT EXISTS app;
CREATE TABLE IF NOT EXISTS app.schema_migration (
    version     INTEGER PRIMARY KEY,
    filename    TEXT        NOT NULL,
    checksum    CHAR(64)    NOT NULL,
    applied_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
"""


class MigrationError(Exception):
    """Migration invalide, modifiée après application, ou en échec."""


@dataclass(frozen=True)
class Migration:
    version: int
    filename: str
    sql: str
    checksum: str


def discover(directory: Path = MIGRATIONS_DIR) -> list[Migration]:
    """Liste les migrations, triées, en refusant noms invalides et doublons de version."""
    migrations: dict[int, Migration] = {}
    for path in sorted(directory.glob("*.sql")):
        match = _FILENAME.match(path.name)
        if not match:
            raise MigrationError(f"Nom de migration invalide : {path.name} (attendu NNNN_nom.sql)")
        version = int(match["version"])
        if version in migrations:
            raise MigrationError(f"Version {version:04d} en double : {path.name}")
        content = path.read_bytes()
        migrations[version] = Migration(
            version=version,
            filename=path.name,
            sql=content.decode("utf-8"),
            checksum=hashlib.sha256(content).hexdigest(),
        )
    return [migrations[v] for v in sorted(migrations)]


def _applied(conn: Connection) -> dict[int, str]:
    rows = conn.execute(text("SELECT version, checksum FROM app.schema_migration"))
    return {row.version: row.checksum for row in rows}


def migrate(engine: Engine, directory: Path = MIGRATIONS_DIR) -> list[str]:
    """Applique les migrations en attente. Retourne la liste des fichiers appliqués."""
    pending = discover(directory)
    applied_now: list[str] = []

    with engine.connect() as conn:
        # SQLAlchemy 2 ouvre une transaction implicite (« autobegin ») à la première
        # requête : on la valide aussitôt pour que chaque étape ait sa propre transaction.
        conn.execute(text("SELECT pg_advisory_lock(:k)"), {"k": _LOCK_KEY})
        conn.commit()
        try:
            with conn.begin():
                conn.exec_driver_sql(_BOOTSTRAP)
            with conn.begin():
                done = _applied(conn)

            for m in pending:
                if m.version in done:
                    if done[m.version] != m.checksum:
                        raise MigrationError(
                            f"{m.filename} a été modifiée après son application "
                            "(créer une nouvelle migration au lieu de la modifier)."
                        )
                    continue
                log.info("Application de la migration %s", m.filename)
                try:
                    with conn.begin():
                        conn.exec_driver_sql(m.sql)
                        conn.execute(
                            text(
                                "INSERT INTO app.schema_migration (version, filename, checksum) "
                                "VALUES (:v, :f, :c)"
                            ),
                            {"v": m.version, "f": m.filename, "c": m.checksum},
                        )
                except Exception as exc:
                    raise MigrationError(f"Échec de {m.filename} : {exc}") from exc
                applied_now.append(m.filename)
        finally:
            if conn.in_transaction():
                conn.rollback()
            conn.execute(text("SELECT pg_advisory_unlock(:k)"), {"k": _LOCK_KEY})
            conn.commit()

    log.info("Migrations : %d appliquée(s), base à jour", len(applied_now))
    return applied_now


def status(engine: Engine, directory: Path = MIGRATIONS_DIR) -> list[tuple[str, str]]:
    """État de chaque migration : 'appliquée', 'en attente' ou 'modifiée'."""
    with engine.connect() as conn:
        exists = conn.execute(text("SELECT to_regclass('app.schema_migration')")).scalar()
        done = _applied(conn) if exists else {}
    result = []
    for m in discover(directory):
        if m.version not in done:
            state = "en attente"
        elif done[m.version] == m.checksum:
            state = "appliquée"
        else:
            state = "MODIFIÉE"
        result.append((m.filename, state))
    return result
