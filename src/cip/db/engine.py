"""Création du moteur SQLAlchemy à partir de la configuration centralisée."""

from __future__ import annotations

from sqlalchemy import Engine, create_engine

from cip.config import get_settings


def get_engine(url: str | None = None) -> Engine:
    """Moteur du compte applicatif. `pool_pre_ping` évite les connexions mortes."""
    return create_engine(url or get_settings().database_url, pool_pre_ping=True, future=True)
