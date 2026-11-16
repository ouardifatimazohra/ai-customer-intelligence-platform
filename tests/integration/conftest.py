"""Fixtures d'intégration : une base PostgreSQL vierge et jetable par test.

Nécessite un serveur PostgreSQL joignable avec les paramètres POSTGRES_* (.env ou
variables d'environnement) — en local : `docker compose up -d postgres`.
"""

import uuid

import pytest
from sqlalchemy import create_engine, make_url, text

from cip.config import Settings


@pytest.fixture
def pg_engine():
    admin_url = make_url(Settings().database_url)
    db_name = f"cip_test_{uuid.uuid4().hex[:8]}"
    admin = create_engine(admin_url.set(database="postgres"), isolation_level="AUTOCOMMIT")
    with admin.connect() as conn:
        conn.execute(text(f'CREATE DATABASE "{db_name}"'))
    engine = create_engine(admin_url.set(database=db_name))
    try:
        yield engine
    finally:
        engine.dispose()
        with admin.connect() as conn:
            conn.execute(text(f'DROP DATABASE IF EXISTS "{db_name}" WITH (FORCE)'))
        admin.dispose()
