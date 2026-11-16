"""Journalisation structurée et traçable.

- Format horodaté ISO 8601 avec niveau, module et identifiant de lot (`ingestion_id`).
- L'identifiant de lot est porté par une variable de contexte : toutes les lignes
  émises pendant le traitement d'un lot le contiennent, sans le passer à chaque appel.
- Un filtre masque toute valeur secrète connue qui apparaîtrait par erreur dans un message.

Usage :
    from cip.log import configure_logging, get_logger, ingestion_context
    configure_logging()
    log = get_logger(__name__)
    with ingestion_context("3f2a..."):
        log.info("Chargement RAW terminé : %d lignes", 7043)
"""

from __future__ import annotations

import contextvars
import logging
import sys
from collections.abc import Iterable, Iterator
from contextlib import contextmanager

from cip.config import get_settings

_ingestion_id: contextvars.ContextVar[str] = contextvars.ContextVar("ingestion_id", default="-")

LOG_FORMAT = "%(asctime)s %(levelname)-8s %(name)s [ingestion_id=%(ingestion_id)s] %(message)s"
DATE_FORMAT = "%Y-%m-%dT%H:%M:%S%z"
MASK = "***"


class ContextFilter(logging.Filter):
    """Ajoute l'identifiant de lot courant à chaque enregistrement."""

    def filter(self, record: logging.LogRecord) -> bool:
        record.ingestion_id = _ingestion_id.get()
        return True


class RedactSecretsFilter(logging.Filter):
    """Remplace les valeurs secrètes par `***` dans le message final."""

    def __init__(self, secrets: Iterable[str]) -> None:
        super().__init__()
        # Les secrets trop courts sont ignorés pour ne pas masquer des mots ordinaires.
        self._secrets = sorted({s for s in secrets if len(s) >= 4}, key=len, reverse=True)

    def filter(self, record: logging.LogRecord) -> bool:
        if not self._secrets:
            return True
        message = record.getMessage()
        redacted = message
        for secret in self._secrets:
            redacted = redacted.replace(secret, MASK)
        if redacted != message:
            record.msg, record.args = redacted, None
        return True


def configure_logging(level: str | None = None, secrets: Iterable[str] | None = None) -> None:
    """Configure le logger racine (idempotent : peut être appelé plusieurs fois)."""
    settings = get_settings()
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(logging.Formatter(LOG_FORMAT, DATE_FORMAT))
    handler.addFilter(ContextFilter())
    handler.addFilter(
        RedactSecretsFilter(secrets if secrets is not None else settings.secret_values())
    )

    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(level or settings.log_level)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


@contextmanager
def ingestion_context(ingestion_id: str) -> Iterator[None]:
    """Associe un identifiant de lot à tous les logs émis dans le bloc `with`."""
    token = _ingestion_id.set(ingestion_id)
    try:
        yield
    finally:
        _ingestion_id.reset(token)
