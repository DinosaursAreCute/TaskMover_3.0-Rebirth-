import unittest
import os
import sys
from unittest.mock import MagicMock

# Add the project directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from taskmover.app import load_settings, save_settings, create_dummy_files

class TestApp(unittest.TestCase):
    def setUp(self):
        self.logger = MagicMock()
        self.test_settings_path = os.path.expanduser("~/default_dir/config/settings.yml")
        self.test_base_directory = os.path.expanduser("~/default_dir/test_dummy_files")

    def tearDown(self):
        # Cleanup test files and directories
        if os.path.exists(self.test_settings_path):
            os.remove(self.test_settings_path)
        if os.path.exists(self.test_base_directory):
            for file in os.listdir(self.test_base_directory):
                os.remove(os.path.join(self.test_base_directory, file))
            os.rmdir(self.test_base_directory)

        # Check for moved files and delete them
        for root, dirs, files in os.walk(self.test_base_directory):
            for file in files:
                os.remove(os.path.join(root, file))
            for dir in dirs:
                os.rmdir(os.path.join(root, dir))

    def test_load_settings_creates_defaults(self):
        settings = load_settings(self.logger)
        self.assertIn("theme", settings)
        self.assertIn("developer_mode", settings)
        self.logger.info.assert_called_with("Settings saved successfully.")

    def test_save_settings(self):
        settings = {"theme": "darkly", "developer_mode": True}
        save_settings(settings, self.logger)
        self.assertTrue(os.path.exists(self.test_settings_path))
        self.logger.info.assert_called_with("Settings saved successfully.")

    def test_create_dummy_files(self):
        create_dummy_files(self.test_base_directory, self.logger)
        self.assertTrue(os.path.exists(self.test_base_directory))
        self.assertGreater(len(os.listdir(self.test_base_directory)), 0)
        self.logger.info.assert_any_call(f"Base directory '{self.test_base_directory}' created.")

        # Check for specific log messages for each dummy file
        dummy_files = [
            "test1.pdf",
            "image_sample.jpg",
            "video_clip.mp4",
            "archive_file.zip",
            "random_file.txt"
        ]
        for file_name in dummy_files:
            self.logger.info.assert_any_call(f"Created dummy file: {os.path.join(self.test_base_directory, file_name)}")

        # Ensure cleanup after test
        self.tearDown()
        self.assertFalse(os.path.exists(self.test_base_directory))

if __name__ == "__main__":
    unittest.main()
