"""Tests de la journalisation (DO-003)."""

import logging
import re

import pytest

from cip.log import configure_logging, get_logger, ingestion_context


@pytest.fixture
def logs(capsys):
    def _read() -> str:
        return capsys.readouterr().err

    yield _read
    logging.getLogger().handlers.clear()


def test_log_line_is_timestamped_and_has_level(logs):
    configure_logging(level="INFO", secrets=[])
    get_logger("cip.test").info("bonjour")
    line = logs().strip()
    assert re.match(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[+-]\d{4} INFO\s+cip\.test ", line)
    assert line.endswith("bonjour")


def test_ingestion_id_is_attached_inside_context_only(logs):
    configure_logging(level="INFO", secrets=[])
    log = get_logger("cip.test")
    with ingestion_context("batch-42"):
        log.info("dans le lot")
    log.info("hors lot")
    inside, outside = logs().strip().splitlines()
    assert "[ingestion_id=batch-42]" in inside
    assert "[ingestion_id=-]" in outside


def test_secrets_are_masked_even_when_logged_by_mistake(logs):
    configure_logging(level="INFO", secrets=["gsk_secret_value"])
    get_logger("cip.test").error("connexion refusée avec la clé %s", "gsk_secret_value")
    output = logs()
    assert "gsk_secret_value" not in output
    assert "clé ***" in output


def test_level_filters_lower_messages(logs):
    configure_logging(level="WARNING", secrets=[])
    log = get_logger("cip.test")
    log.info("ignoré")
    log.warning("affiché")
    output = logs()
    assert "ignoré" not in output
    assert "affiché" in output


def test_configure_is_idempotent(logs):
    configure_logging(level="INFO", secrets=[])
    configure_logging(level="INFO", secrets=[])
    get_logger("cip.test").info("une seule fois")
    assert logs().count("une seule fois") == 1
