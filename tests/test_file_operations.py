import unittest
from unittest.mock import patch, MagicMock
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from taskmover import file_operations

class TestFileOperationsProgressBar(unittest.TestCase):
    def setUp(self):
        self.settings = {"organisation_folder": os.path.dirname(__file__)}
        self.rules = {}
        self.logger = MagicMock()

    @patch("taskmover.file_operations.ttk.Progressbar")
    @patch("taskmover.file_operations.ttk.Label")
    @patch("taskmover.file_operations.Toplevel")
    def test_progress_bar_called_in_organize_files(self, mock_toplevel, mock_label, mock_progressbar):
        # Patch os.listdir and os.path.isfile to simulate files
        with patch("os.listdir", return_value=["file1.txt", "file2.txt"]), \
             patch("os.path.isfile", return_value=True), \
             patch("os.path.exists", return_value=True), \
             patch("taskmover.file_operations.move_file"):
            file_operations.organize_files(self.settings, self.rules, self.logger)
            self.assertTrue(mock_progressbar.called, "Progressbar should be instantiated when organizing files.")

if __name__ == "__main__":
    unittest.main()
