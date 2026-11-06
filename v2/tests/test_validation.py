import unittest

from v2.core.config import Settings
from v2.core.validation import (
    ValidationError,
    validate_request,
    validate_file_count,
    validate_file_size,
    validate_file_path,
)


class TestValidation(unittest.TestCase):

    def setUp(self):
        self.settings = Settings()

    def test_valid_request(self):
        validate_request("Créer une application", self.settings)

    def test_empty_request(self):
        with self.assertRaises(ValidationError):
            validate_request("   ", self.settings)

    def test_request_too_long(self):
        with self.assertRaises(ValidationError):
            validate_request("A" * 20001, self.settings)

    def test_valid_file_count(self):
        validate_file_count(5, self.settings)

    def test_zero_file_count(self):
        with self.assertRaises(ValidationError):
            validate_file_count(0, self.settings)

    def test_too_many_files(self):
        with self.assertRaises(ValidationError):
            validate_file_count(101, self.settings)

    def test_valid_file_size(self):
        validate_file_size(1000, self.settings)

    def test_negative_file_size(self):
        with self.assertRaises(ValidationError):
            validate_file_size(-1, self.settings)

    def test_file_too_large(self):
        with self.assertRaises(ValidationError):
            validate_file_size(2000001, self.settings)

    def test_valid_file_path(self):
        result = validate_file_path("src/main.py")
        self.assertEqual(result, "src/main.py")

    def test_absolute_path(self):
        with self.assertRaises(ValidationError):
            validate_file_path("/etc/passwd")

    def test_parent_directory_path(self):
        with self.assertRaises(ValidationError):
            validate_file_path("../secret.txt")

    def test_windows_path(self):
        with self.assertRaises(ValidationError):
            validate_file_path("C:\\Windows\\system32")

    def test_null_byte_path(self):
        with self.assertRaises(ValidationError):
            validate_file_path("src/\x00secret.py")


if __name__ == "__main__":
    unittest.main()
