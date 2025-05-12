import unittest
import os
import sys
import time
from unittest.mock import MagicMock

DEPLOY_TIME = time.time()

# ANSI color codes
COLOR_RESET = "\033[0m"
COLOR_GREEN = "\033[92m"
COLOR_RED = "\033[91m"
COLOR_YELLOW = "\033[93m"
COLOR_CYAN = "\033[96m"

# Only log on finish or fatal error, with color
# Format: [time since deploy] [finished|stopped] [passed|failed] [test] [message]
def log_test(state, result, test, message):
    elapsed = time.time() - DEPLOY_TIME
    color = COLOR_GREEN if result == "passed" else COLOR_RED
    state_color = COLOR_CYAN if state == "finished" else COLOR_YELLOW
    print(f"{COLOR_YELLOW}[{elapsed:.2f}s]{COLOR_RESET} "
          f"{state_color}[{state}]{COLOR_RESET} "
          f"{color}[{result}]{COLOR_RESET} "
          f"{COLOR_CYAN}[{test}]{COLOR_RESET} {message}")

def log_decorator(fn):
    def wrapper(self, *args, **kwargs):
        test_name = fn.__name__
        try:
            fn(self, *args, **kwargs)
            log_test("finished", "passed", test_name, "Test passed")
        except Exception as e:
            log_test("stopped", "failed", test_name, f"Test failed: {e}")
            raise
    return wrapper

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
        for root, dirs, files in os.walk(self.test_base_directory):
            for file in files:
                os.remove(os.path.join(root, file))
            for dir in dirs:
                os.rmdir(os.path.join(root, dir))

    @log_decorator
    def test_load_settings_creates_defaults(self):
        settings = load_settings(self.test_settings_path)
        self.assertIn("theme", settings)
        self.assertIn("developer_mode", settings)

    @log_decorator
    def test_save_settings(self):
        settings = {"theme": "darkly", "developer_mode": True}
        save_settings(self.test_settings_path, settings, self.logger)
        self.assertTrue(os.path.exists(self.test_settings_path))

    @log_decorator
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
        self.tearDown()
        self.assertFalse(os.path.exists(self.test_base_directory))

    @log_decorator
    def test_save_settings_invalid_path(self):
        # Should raise an error if path is a directory
        with self.assertRaises(Exception):
            save_settings("/", {"theme": "darkly"}, self.logger)

    @log_decorator
    def test_create_dummy_files_empty_dir(self):
        # Should still create files if directory exists
        os.makedirs(self.test_base_directory, exist_ok=True)
        create_dummy_files(self.test_base_directory, self.logger)
        self.assertTrue(os.path.exists(self.test_base_directory))
        self.assertGreater(len(os.listdir(self.test_base_directory)), 0)

    @log_decorator
    def test_load_settings_invalid_file(self):
        # Write invalid yaml
        with open(self.test_settings_path, "w") as f:
            f.write(":invalid_yaml:")
        with self.assertRaises(Exception):
            load_settings(self.test_settings_path)

if __name__ == "__main__":
    unittest.main()
