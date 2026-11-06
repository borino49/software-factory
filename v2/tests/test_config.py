import os
import unittest
from pathlib import Path
from unittest.mock import patch

from v2.core.config import Settings, get_settings


class TestSettings(unittest.TestCase):

    def test_default_settings(self):
        settings = Settings()

        self.assertEqual(settings.app_name, "Software Factory")
        self.assertEqual(settings.environment, "development")
        self.assertFalse(settings.allow_execution_network)
        self.assertEqual(settings.max_correction_attempts, 2)

    def test_invalid_environment(self):
        with self.assertRaises(ValueError):
            Settings(environment="unknown")

    def test_negative_execution_timeout(self):
        with self.assertRaises(ValueError):
            Settings(execution_timeout_seconds=0)

    def test_negative_correction_attempts(self):
        with self.assertRaises(ValueError):
            Settings(max_correction_attempts=-1)

    def test_environment_variables(self):
        variables = {
            "SF_ENVIRONMENT": "test",
            "SF_DATA_DIR": "test_data",
            "SF_MAX_FILES": "50",
            "SF_ALLOW_EXECUTION_NETWORK": "false",
        }

        with patch.dict(os.environ, variables, clear=False):
            settings = get_settings()

        self.assertEqual(settings.environment, "test")
        self.assertEqual(settings.data_dir, Path("test_data"))
        self.assertEqual(settings.max_files_per_project, 50)
        self.assertFalse(settings.allow_execution_network)


if __name__ == "__main__":
    unittest.main()
