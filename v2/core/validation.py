"""Validation et sécurisation des données des projets."""

from pathlib import PurePosixPath

from v2.core.config import Settings


class ValidationError(ValueError):
    """Erreur déclenchée lorsqu'une donnée ne respecte pas les règles."""


def validate_request(request: str, settings: Settings) -> None:
    """Vérifie la taille d'une demande utilisateur."""
    if not isinstance(request, str):
        raise ValidationError("La demande doit être du texte.")

    if not request.strip():
        raise ValidationError("La demande ne peut pas être vide.")

    if len(request) > settings.max_request_chars:
        raise ValidationError("La demande dépasse la taille maximale autorisée.")


def validate_file_count(file_count: int, settings: Settings) -> None:
    """Vérifie le nombre de fichiers d'un projet."""
    if not isinstance(file_count, int) or isinstance(file_count, bool):
        raise ValidationError("Le nombre de fichiers doit être un entier.")

    if file_count < 1:
        raise ValidationError("Un projet doit contenir au moins un fichier.")

    if file_count > settings.max_files_per_project:
        raise ValidationError("Le projet contient trop de fichiers.")


def validate_file_size(file_size: int, settings: Settings) -> None:
    """Vérifie la taille d'un fichier en octets."""
    if not isinstance(file_size, int) or isinstance(file_size, bool):
        raise ValidationError("La taille du fichier doit être un entier.")

    if file_size < 0:
        raise ValidationError("La taille du fichier ne peut pas être négative.")

    if file_size > settings.max_file_bytes:
        raise ValidationError("Le fichier dépasse la taille maximale autorisée.")


def validate_file_path(file_path: str) -> str:
    """Refuse les chemins absolus et les chemins permettant une sortie du projet."""
    if not isinstance(file_path, str) or not file_path.strip():
        raise ValidationError("Le chemin du fichier est invalide.")

    if "\x00" in file_path or "\\" in file_path:
        raise ValidationError("Le chemin du fichier contient des caractères interdits.")

    path = PurePosixPath(file_path)

    if path.is_absolute():
        raise ValidationError("Les chemins absolus sont interdits.")

    if any(part in {".", ".."} for part in file_path.split("/")):
        raise ValidationError("Le chemin tente de sortir du dossier du projet.")

    if not path.parts:
        raise ValidationError("Le chemin du fichier est invalide.")

    return path.as_posix()
