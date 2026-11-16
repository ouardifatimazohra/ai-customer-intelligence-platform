"""Configuration centralisée de la plateforme.

Toutes les valeurs proviennent des variables d'environnement (ou du fichier `.env`
en local), jamais du code. Les secrets sont typés `SecretStr` : ils ne s'affichent
pas dans les logs, les `repr()` ni les messages d'erreur.

Usage :
    from cip.config import get_settings
    settings = get_settings()
    settings.database_url  # URL SQLAlchemy construite à partir des variables POSTGRES_*
"""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Paramètres de l'application, validés au démarrage."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",  # une variable inconnue dans .env ne fait pas planter l'application
        case_sensitive=False,
    )

    # --- Application ---
    app_env: Literal["local", "test", "ci"] = "local"
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"

    # --- PostgreSQL : compte applicatif ---
    postgres_host: str = "localhost"
    postgres_port: int = Field(default=5432, ge=1, le=65535)
    postgres_db: str = "cip"
    postgres_user: str = "cip_app"
    postgres_password: SecretStr = SecretStr("change-me-local-only")

    # --- PostgreSQL : compte en lecture seule de l'assistant (sprint 6) ---
    assistant_db_user: str = "cip_assistant"
    assistant_db_password: SecretStr = SecretStr("change-me-readonly")

    # --- LLM (sprint 6) ---
    llm_provider: Literal["mock", "groq"] = "mock"
    groq_api_key: SecretStr | None = None
    groq_model: str | None = None

    # --- MLflow (sprint 4) ---
    mlflow_tracking_uri: str = "http://localhost:5000"

    @model_validator(mode="after")
    def _groq_requires_key(self) -> Settings:
        """Échoue tôt et clairement si Groq est choisi sans clé."""
        if self.llm_provider == "groq" and not (
            self.groq_api_key and self.groq_api_key.get_secret_value().strip()
        ):
            raise ValueError(
                "LLM_PROVIDER=groq nécessite GROQ_API_KEY dans .env "
                "(ou utiliser LLM_PROVIDER=mock pour fonctionner sans clé)."
            )
        return self

    def _url(self, user: str, password: SecretStr) -> str:
        return (
            f"postgresql+psycopg://{user}:{password.get_secret_value()}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def database_url(self) -> str:
        """URL SQLAlchemy du compte applicatif. Contient un secret : ne jamais la logger."""
        return self._url(self.postgres_user, self.postgres_password)

    @property
    def assistant_database_url(self) -> str:
        """URL SQLAlchemy du compte lecture seule. Contient un secret : ne jamais la logger."""
        return self._url(self.assistant_db_user, self.assistant_db_password)

    def secret_values(self) -> list[str]:
        """Valeurs secrètes non vides, utilisées pour masquer les logs."""
        secrets = [self.postgres_password, self.assistant_db_password, self.groq_api_key]
        return [s.get_secret_value() for s in secrets if s and s.get_secret_value()]


@lru_cache
def get_settings() -> Settings:
    """Instance unique (mise en cache) des paramètres."""
    return Settings()
