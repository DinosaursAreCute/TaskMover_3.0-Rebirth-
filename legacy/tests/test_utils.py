import unittest
from unittest.mock import MagicMock, patch
import tkinter as tk
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from taskmover.utils import reset_colors, show_license_info, browse_path, center_window, ensure_directory_exists

class TestUtils(unittest.TestCase):
    def setUp(self):
        try:
            self.root = tk.Tk()
            self.has_display = True
        except Exception:
            self.has_display = False
        self.settings = {"accent_color": "#123456", "background_color": "#654321", "text_color": "#abcdef"}
        self.saved_settings = None
        self.logger = MagicMock()
        def fake_save(path, settings, logger):
            self.saved_settings = dict(settings)
        self.fake_save = fake_save

    def tearDown(self):
        if hasattr(self, 'root') and self.has_display:
            self.root.destroy()

    def test_reset_colors(self):
        # Patch messagebox to avoid GUI popups
        import taskmover.utils as utils
        utils.messagebox.showinfo = MagicMock()
        reset_colors(self.settings, self.fake_save, self.logger)
        self.assertEqual(self.saved_settings["accent_color"], None)
        self.assertEqual(self.saved_settings["background_color"], None)
        self.assertEqual(self.saved_settings["text_color"], None)
        self.logger.info.assert_called_with("Colors reset to default values.")
        utils.messagebox.showinfo.assert_called()

    def test_show_license_info(self):
        import taskmover.utils as utils
        utils.messagebox.showinfo = MagicMock()
        show_license_info()
        utils.messagebox.showinfo.assert_called()
        args, kwargs = utils.messagebox.showinfo.call_args
        self.assertIn("MIT License", args[1])

    def test_browse_path(self):
        import taskmover.utils as utils
        utils.tkinter.filedialog.askdirectory = MagicMock(return_value="/tmp/testdir")
        # Use a real StringVar (no mock master) so .get() works as expected
        var = tk.StringVar()
        browse_path(var, self.logger)
        self.assertEqual(var.get(), "/tmp/testdir")
        self.logger.info.assert_called_with("Base path updated to: /tmp/testdir")

    def test_center_window(self):
        # Simulate a UI root window for all environments
        mock_root = MagicMock()
        mock_root.geometry = MagicMock(return_value="200x100")
        mock_root.update_idletasks = MagicMock()
        center_window(mock_root)
        mock_root.geometry.assert_called()

    def test_ensure_directory_exists(self):
        test_dir = os.path.join(os.path.dirname(__file__), "test_utils_tmp")
        if os.path.exists(test_dir):
            os.rmdir(test_dir)
        ensure_directory_exists(test_dir, self.logger)
        self.assertTrue(os.path.exists(test_dir))
        self.logger.debug.assert_called_with(f"Ensured directory exists: {test_dir}")
        os.rmdir(test_dir)

if __name__ == "__main__":
    unittest.main()
