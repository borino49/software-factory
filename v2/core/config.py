"""Configuration centralisée de Software Factory V2."""

import os
from dataclasses import dataclass
from pathlib import Path


def _env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)

    if value is None:
        return default

    normalized = value.strip().lower()

    if normalized in {"1", "true", "yes", "on"}:
        return True

    if normalized in {"0", "false", "no", "off"}:
        return False

    raise ValueError(f"Valeur booléenne invalide pour {name}.")


def _env_int(name: str, default: int) -> int:
    value = os.getenv(name)

    if value is None:
        return default

    try:
        return int(value)
    except ValueError as exc:
        raise ValueError(f"Valeur entière invalide pour {name}.") from exc


@dataclass(frozen=True, slots=True)
class Settings:
    """Paramètres globaux de l'application."""

    app_name: str = "Software Factory"
    environment: str = "development"
    data_dir: Path = Path("data")

    max_request_chars: int = 20_000
    max_files_per_project: int = 100
    max_file_bytes: int = 2_000_000

    provider_timeout_seconds: int = 60
    execution_timeout_seconds: int = 30
    max_correction_attempts: int = 2

    allow_execution_network: bool = False
    debug: bool = False

    def __post_init__(self) -> None:
        if self.environment not in {"development", "test", "production"}:
            raise ValueError("Environnement non reconnu.")

        if self.max_request_chars < 100:
            raise ValueError("La limite de caractères est trop faible.")

        if self.max_files_per_project < 1:
            raise ValueError("Le nombre maximal de fichiers doit être positif.")

        if self.max_file_bytes < 1:
            raise ValueError("La taille maximale des fichiers doit être positive.")

        if self.provider_timeout_seconds < 1:
            raise ValueError("Le délai fournisseur doit être positif.")

        if self.execution_timeout_seconds < 1:
            raise ValueError("Le délai d'exécution doit être positif.")

        if self.max_correction_attempts < 0:
            raise ValueError("Le nombre de corrections ne peut pas être négatif.")


def get_settings() -> Settings:
    """Construit la configuration à partir des variables d'environnement."""

    return Settings(
        environment=os.getenv("SF_ENVIRONMENT", "development").strip().lower(),
        data_dir=Path(os.getenv("SF_DATA_DIR", "data")),
        max_request_chars=_env_int("SF_MAX_REQUEST_CHARS", 20_000),
        max_files_per_project=_env_int("SF_MAX_FILES", 100),
        max_file_bytes=_env_int("SF_MAX_FILE_BYTES", 2_000_000),
        provider_timeout_seconds=_env_int("SF_PROVIDER_TIMEOUT", 60),
        execution_timeout_seconds=_env_int("SF_EXECUTION_TIMEOUT", 30),
        max_correction_attempts=_env_int("SF_MAX_CORRECTIONS", 2),
        allow_execution_network=_env_bool("SF_ALLOW_EXECUTION_NETWORK", False),
        debug=_env_bool("SF_DEBUG", False),
    )
