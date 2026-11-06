"""Tests du moteur de création et d'inspection des archives ZIP."""

import unittest
from io import BytesIO
from zipfile import ZipFile

from v2.core.config import Settings
from v2.exports.zip_builder import (
    ZipBuildError,
    build_zip,
    inspect_zip,
)


class TestZipBuilder(unittest.TestCase):

    def setUp(self):
        self.settings = Settings()

    def test_build_valid_zip(self):
        files = {
            "README.md": "# Mon projet",
            "src/main.py": "print('Hello')",
        }

        archive_data = build_zip(files, self.settings)

        self.assertIsInstance(archive_data, bytes)
        self.assertGreater(len(archive_data), 0)

    def test_inspect_valid_zip(self):
        files = {
            "README.md": "# Mon projet",
            "src/main.py": "print('Hello')",
        }

        archive_data = build_zip(files, self.settings)
        names = inspect_zip(archive_data)

        self.assertEqual(names, ["README.md", "src/main.py"])

    def test_build_binary_file(self):
        files = {
            "image.png": b"\x89PNG\r\n\x1a\n",
        }

        archive_data = build_zip(files, self.settings)
        self.assertIsInstance(archive_data, bytes)

    def test_empty_files_rejected(self):
        with self.assertRaises(ZipBuildError):
            build_zip({}, self.settings)

    def test_non_dictionary_rejected(self):
        with self.assertRaises(ZipBuildError):
            build_zip(["file.txt"], self.settings)

    def test_too_many_files_rejected(self):
        settings = Settings(max_files_per_project=2)
        files = {
            "a.txt": "A",
            "b.txt": "B",
            "c.txt": "C",
        }

        with self.assertRaises(ZipBuildError):
            build_zip(files, settings)

    def test_file_too_large_rejected(self):
        settings = Settings(max_file_bytes=5)
        files = {"large.txt": "A" * 6}

        with self.assertRaises(ZipBuildError):
            build_zip(files, settings)

    def test_parent_directory_path_rejected(self):
        files = {"../secret.txt": "secret"}

        with self.assertRaises(ZipBuildError):
            build_zip(files, self.settings)

    def test_absolute_path_rejected(self):
        files = {"/etc/passwd": "secret"}

        with self.assertRaises(ZipBuildError):
            build_zip(files, self.settings)

    def test_windows_path_rejected(self):
        files = {"C:\\Windows\\secret.txt": "secret"}

        with self.assertRaises(ZipBuildError):
            build_zip(files, self.settings)

    def test_env_file_rejected(self):
        files = {".env": "API_KEY=secret"}

        with self.assertRaises(ZipBuildError):
            build_zip(files, self.settings)

    def test_git_directory_rejected(self):
        files = {".git/config": "secret"}

        with self.assertRaises(ZipBuildError):
            build_zip(files, self.settings)

    def test_python_cache_rejected(self):
        files = {"__pycache__/module.pyc": b"cache"}

        with self.assertRaises(ZipBuildError):
            build_zip(files, self.settings)

    def test_invalid_content_rejected(self):
        files = {"data.txt": 123}

        with self.assertRaises(ZipBuildError):
            build_zip(files, self.settings)

    def test_archive_integrity(self):
        files = {
            "README.md": "Projet de test",
            "src/main.py": "print('OK')",
        }

        archive_data = build_zip(files, self.settings)

        with ZipFile(BytesIO(archive_data), "r") as archive:
            self.assertIsNone(archive.testzip())

    def test_corrupted_archive_rejected(self):
        with self.assertRaises(ZipBuildError):
            inspect_zip(b"ceci n'est pas une archive ZIP")

    def test_non_bytes_archive_rejected(self):
        with self.assertRaises(ZipBuildError):
            inspect_zip("archive invalide")


if __name__ == "__main__":
    unittest.main()
