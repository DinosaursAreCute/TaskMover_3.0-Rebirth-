import unittest
import os
import sys
from unittest.mock import MagicMock

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
        for root, dirs, files in os.walk(self.test_base_directory):
            for file in files:
                os.remove(os.path.join(root, file))
            for dir in dirs:
                os.rmdir(os.path.join(root, dir))

    def test_load_settings_creates_defaults(self):
        settings = load_settings(self.test_settings_path)
        self.assertIn("theme", settings)
        self.assertIn("developer_mode", settings)

    def test_save_settings(self):
        settings = {"theme": "darkly", "developer_mode": True}
        save_settings(self.test_settings_path, settings, self.logger)
        self.assertTrue(os.path.exists(self.test_settings_path))

    def test_create_dummy_files(self):
        create_dummy_files(self.test_base_directory, self.logger)
        self.assertTrue(os.path.exists(self.test_base_directory))
        self.assertGreater(len(os.listdir(self.test_base_directory)), 0)
        self.logger.info.assert_any_call(f"Base directory '{self.test_base_directory}' created.")
        dummy_files = [
            "test_document.pdf",
            "image_sample.jpg",
            "video_clip.mp4",
            "archive_file.zip",
            "random_file.txt"
        ]
        for file_name in dummy_files:
            expected_path = os.path.normpath(os.path.join(self.test_base_directory, file_name))
            found = any(
                call_args[0][0].replace("/", os.sep).replace("\\", os.sep) == f"Created dummy file: {expected_path}"
                for call_args in self.logger.info.call_args_list
            )
            self.assertTrue(found, f"Log for {expected_path} not found")
        # Do not call tearDown here; unittest will handle cleanup
        self.assertTrue(os.path.exists(self.test_base_directory))

    def test_save_settings_invalid_path(self):
        # Should raise an error if path is a directory
        with self.assertRaises(Exception):
            save_settings("/", {"theme": "darkly"}, self.logger)

    def test_create_dummy_files_empty_dir(self):
        # Should still create files if directory exists
        os.makedirs(self.test_base_directory, exist_ok=True)
        create_dummy_files(self.test_base_directory, self.logger)
        self.assertTrue(os.path.exists(self.test_base_directory))
        self.assertGreater(len(os.listdir(self.test_base_directory)), 0)

    def test_load_settings_invalid_file(self):
        """Test loading an invalid settings file."""
        invalid_settings_path = "invalid_settings.yml"
        with open(invalid_settings_path, "w") as file:
            file.write("invalid: [this, is, not, a, dict]")
        # Test loading the invalid settings file
        with self.assertRaises(RuntimeError):
            load_settings(invalid_settings_path)
        # Clean up
        os.remove(invalid_settings_path)

if __name__ == "__main__":
    unittest.main()
