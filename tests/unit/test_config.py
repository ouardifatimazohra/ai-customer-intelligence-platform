"""Tests de la configuration centralisée (DO-003)."""

import pytest
from pydantic import ValidationError

from cip.config import Settings


@pytest.fixture(autouse=True)
def isolated_env(monkeypatch, tmp_path):
    """Chaque test démarre sans .env ni variables du poste de développement."""
    monkeypatch.chdir(tmp_path)
    for var in [
        "APP_ENV",
        "LOG_LEVEL",
        "POSTGRES_HOST",
        "POSTGRES_PORT",
        "POSTGRES_DB",
        "POSTGRES_USER",
        "POSTGRES_PASSWORD",
        "LLM_PROVIDER",
        "GROQ_API_KEY",
        "GROQ_MODEL",
    ]:
        monkeypatch.delenv(var, raising=False)


def test_defaults_work_without_any_configuration():
    s = Settings()
    assert s.app_env == "local"
    assert s.llm_provider == "mock"
    assert s.database_url == "postgresql+psycopg://cip_app:change-me-local-only@localhost:5432/cip"


def test_environment_variables_override_defaults(monkeypatch):
    monkeypatch.setenv("POSTGRES_HOST", "db.internal")
    monkeypatch.setenv("POSTGRES_PORT", "6543")
    s = Settings()
    assert "@db.internal:6543/" in s.database_url


def test_dotenv_file_is_read(tmp_path):
    (tmp_path / ".env").write_text("POSTGRES_DB=cip_test\nLOG_LEVEL=DEBUG\n", encoding="utf-8")
    s = Settings()
    assert s.postgres_db == "cip_test"
    assert s.log_level == "DEBUG"


@pytest.mark.parametrize(
    ("var", "value"),
    [("LLM_PROVIDER", "openai"), ("POSTGRES_PORT", "99999"), ("LOG_LEVEL", "VERBOSE")],
)
def test_invalid_values_fail_with_clear_error(monkeypatch, var, value):
    monkeypatch.setenv(var, value)
    with pytest.raises(ValidationError) as exc:
        Settings()
    assert var.lower() in str(exc.value)


def test_groq_without_key_is_rejected(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "groq")
    with pytest.raises(ValidationError, match="GROQ_API_KEY"):
        Settings()


def test_groq_with_key_is_accepted(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "groq")
    monkeypatch.setenv("GROQ_API_KEY", "gsk_test_not_a_real_key")
    assert Settings().llm_provider == "groq"


def test_secrets_never_appear_in_repr(monkeypatch):
    monkeypatch.setenv("POSTGRES_PASSWORD", "super-secret-pw")
    monkeypatch.setenv("GROQ_API_KEY", "gsk_secret_value")
    s = Settings()
    text = repr(s) + str(s) + s.model_dump_json()
    assert "super-secret-pw" not in text
    assert "gsk_secret_value" not in text
    assert set(s.secret_values()) >= {"super-secret-pw", "gsk_secret_value"}
