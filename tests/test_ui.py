import unittest
from unittest.mock import MagicMock
import tkinter as tk
from taskmover.app import setup_ui
from taskmover.ui_helpers import update_rule_list

class TestUI(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.root.geometry("900x700")
        self.rules = {
            "Rule1": {"patterns": ["*.txt"], "path": "C:/Documents", "unzip": False, "active": True},
            "Rule2": {"patterns": ["*.jpg"], "path": "C:/Pictures", "unzip": False, "active": False},
        }
        self.config_directory = "C:/config"
        self.logger = MagicMock()
        self.style = MagicMock()
        self.settings = {"theme": "flatly"}

    def tearDown(self):
        self.root.destroy()

    def test_buttons_integration(self):
        """Test if buttons for adding, removing, enabling, and disabling rules are integrated."""
        setup_ui(self.root, tk.StringVar(value="C:/"), self.rules, self.config_directory, self.style, self.settings, self.logger)

        # Check if buttons exist
        add_button = self.root.nametowidget("!frame.!button")
        remove_button = self.root.nametowidget("!frame.!button2")
        enable_all_button = self.root.nametowidget("!frame.!button3")
        disable_all_button = self.root.nametowidget("!frame.!button4")

        self.assertIsNotNone(add_button, "Add Rule button is missing")
        self.assertIsNotNone(remove_button, "Remove Rule button is missing")
        self.assertIsNotNone(enable_all_button, "Enable All button is missing")
        self.assertIsNotNone(disable_all_button, "Disable All button is missing")

    def test_rule_list_update(self):
        """Test if the rule list updates correctly."""
        rule_frame = tk.Frame(self.root)
        update_rule_list(rule_frame, self.rules, self.config_directory, self.logger)

        # Check if rules are displayed
        children = rule_frame.winfo_children()
        self.assertEqual(len(children), len(self.rules), "Rule list does not match the number of rules.")

if __name__ == "__main__":
    unittest.main()
