
"""Création sécurisée des archives ZIP des projets."""

from io import BytesIO
from zipfile import ZIP_DEFLATED, BadZipFile, ZipFile

from v2.core.config import Settings
from v2.core.validation import (
    ValidationError,
    validate_file_count,
    validate_file_path,
    validate_file_size,
)


class ZipBuildError(ValueError):
    """Erreur lors de la création ou de l'inspection d'une archive ZIP."""


EXCLUDED_NAMES = {
    ".git",
    "__pycache__",
    ".ds_store",
    "thumbs.db",
}

EXCLUDED_SUFFIXES = (
    ".pyc",
    ".pyo",
    ".pyd",
)


def _is_excluded(path: str) -> bool:
    """Détermine si un chemin contient un élément interdit."""
    parts = path.split("/")

    for part in parts:
        normalized = part.casefold()

        if normalized in EXCLUDED_NAMES:
            return True

        if normalized.endswith(EXCLUDED_SUFFIXES):
            return True

        if normalized.startswith(".env") and normalized != ".env.example":
            return True

    return False


def _validate_archive_path(path: str) -> str:
    """Valide et normalise un chemin destiné à une archive ZIP."""
    safe_path = validate_file_path(path)

    if safe_path != path:
        raise ZipBuildError(
            f"Le chemin '{path}' n'est pas au format canonique."
        )

    if ":" in safe_path:
        raise ZipBuildError(
            f"Le chemin '{safe_path}' contient un caractère interdit."
        )

    if _is_excluded(safe_path):
        raise ZipBuildError(
            f"Le fichier '{safe_path}' est interdit dans l'export."
        )

    return safe_path


def _check_path_collisions(paths: list[str]) -> None:
    """Refuse les doublons et les conflits entre fichiers et répertoires."""
    known_paths = set()
    known_casefolded = set()

    for path in paths:
        normalized = path.casefold()

        if normalized in known_casefolded:
            raise ZipBuildError(
                f"Chemin de fichier dupliqué : '{path}'."
            )

        parts = path.split("/")

        for index in range(1, len(parts)):
            parent = "/".join(parts[:index]).casefold()

            if parent in known_casefolded:
                raise ZipBuildError(
                    f"Conflit entre fichier et répertoire : '{path}'."
                )

        prefix = normalized + "/"

        if any(existing.startswith(prefix) for existing in known_casefolded):
            raise ZipBuildError(
                f"Conflit entre fichier et répertoire : '{path}'."
            )

        known_paths.add(path)
        known_casefolded.add(normalized)


def build_zip(
    files: dict[str, str | bytes],
    settings: Settings,
) -> bytes:
    """Construit une archive ZIP sécurisée en mémoire."""

    if not isinstance(files, dict):
        raise ZipBuildError(
            "Les fichiers doivent être fournis sous forme de dictionnaire."
        )

    if not files:
        raise ZipBuildError("Impossible de créer une archive vide.")

    try:
        validate_file_count(len(files), settings)

        validated_files = {}

        for file_path, content in files.items():
            if not isinstance(file_path, str):
                raise ZipBuildError("Un chemin de fichier est invalide.")

            safe_path = _validate_archive_path(file_path)

            if not isinstance(content, (str, bytes)):
                raise ZipBuildError(
                    f"Le contenu de '{safe_path}' doit être du texte ou des octets."
                )

            if isinstance(content, str):
                content = content.encode("utf-8")

            validate_file_size(len(content), settings)

            validated_files[safe_path] = content

        _check_path_collisions(list(validated_files))

    except ValidationError as exc:
        raise ZipBuildError(str(exc)) from exc

    archive_buffer = BytesIO()

    try:
        with ZipFile(
            archive_buffer,
            mode="w",
            compression=ZIP_DEFLATED,
        ) as archive:
            for file_path, content in validated_files.items():
                archive.writestr(file_path, content)

        archive_data = archive_buffer.getvalue()

        inspect_zip(archive_data, settings)
        return archive_data

    except ZipBuildError:
        raise
    except Exception as exc:
        raise ZipBuildError(
            "Échec de la création de l'archive ZIP."
        ) from exc


def inspect_zip(
    archive_data: bytes,
    settings: Settings | None = None,
) -> bytes | list[str]:
    """Vérifie une archive ZIP et retourne la liste de ses fichiers."""

    if not isinstance(archive_data, bytes):
        raise ZipBuildError(
            "L'archive doit être fournie sous forme d'octets."
        )

    if settings is None:
        settings = Settings()

    try:
        with ZipFile(BytesIO(archive_data), mode="r") as archive:
            entries = archive.infolist()

            validate_file_count(len(entries), settings)

            names = []
            total_size = 0

            for entry in entries:
                if entry.is_dir():
                    raise ZipBuildError(
                        "Les entrées de répertoire explicites sont interdites."
                    )

                safe_path = _validate_archive_path(entry.filename)

                validate_file_size(entry.file_size, settings)

                total_size += entry.file_size

                maximum_total_size = (
                    settings.max_file_bytes
                    * settings.max_files_per_project
                )

                if total_size > maximum_total_size:
                    raise ZipBuildError(
                        "La taille totale de l'archive dépasse la limite autorisée."
                    )

                names.append(safe_path)

            _check_path_collisions(names)

            for entry in entries:
                content = archive.read(entry)

                if len(content) != entry.file_size:
                    raise ZipBuildError(
                        f"Taille incohérente pour '{entry.filename}'."
                    )

            return names

    except ZipBuildError:
        raise
    except ValidationError as exc:
        raise ZipBuildError(str(exc)) from exc
    except (BadZipFile, OSError, RuntimeError, ValueError) as exc:
        raise ZipBuildError(
            "Archive ZIP invalide ou illisible."
        ) from exc
    except Exception as exc:
        raise ZipBuildError(
            "Échec de l'inspection de l'archive ZIP."
        ) from exc
