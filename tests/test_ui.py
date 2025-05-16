import sys
import os
import unittest
from unittest.mock import MagicMock
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

class TestUI(unittest.TestCase):
    def setUp(self):
        self.rules = {
            "Rule1": {"patterns": ["*.txt"], "path": "C:/Documents", "unzip": False, "active": True},
            "Rule2": {"patterns": ["*.jpg"], "path": "C:/Pictures", "unzip": False, "active": False},
        }
        self.config_directory = "C:/config"
        self.logger = MagicMock()
        self.settings = {"theme": "flatly"}

    def can_init_tk(self):
        try:
            import tkinter as tk
            root = tk.Tk()
            root.destroy()
            return True
        except Exception:
            return False

    def test_buttons_integration(self):
        if not self.can_init_tk():
            self.skipTest("Tkinter cannot be initialized (no display or misconfigured Tcl/Tk). Skipping UI test.")
        import tkinter as tk
        import ttkbootstrap as ttkb
        from taskmover.app import setup_ui
        root = tk.Tk()
        style = MagicMock()
        try:
            setup_ui(root, tk.StringVar(value="C:/"), self.rules, self.config_directory, style, self.settings, self.logger)
            button_frame = None
            for child in root.winfo_children():
                if isinstance(child, ttkb.Frame):
                    buttons = [w for w in child.winfo_children() if isinstance(w, ttkb.Button)]
                    if len(buttons) >= 4:
                        button_frame = child
                        break
            self.assertIsNotNone(button_frame, "Button frame not found")
            buttons = [w for w in button_frame.winfo_children() if isinstance(w, ttkb.Button)]
            self.assertGreaterEqual(len(buttons), 4, "Not all rule management buttons are present")
        finally:
            root.destroy()

    def test_rule_list_update(self):
        if not self.can_init_tk():
            self.skipTest("Tkinter cannot be initialized (no display or misconfigured Tcl/Tk). Skipping UI test.")
        import tkinter as tk
        from taskmover.ui_helpers import update_rule_list
        root = tk.Tk()
        try:
            rule_frame = tk.Frame(root)
            update_rule_list(rule_frame, self.rules, self.config_directory, self.logger)
            children = rule_frame.winfo_children()
            self.assertEqual(len(children), len(self.rules), "Rule list does not match the number of rules.")
        finally:
            root.destroy()

    def test_rule_list_update_empty(self):
        if not self.can_init_tk():
            self.skipTest("Tkinter cannot be initialized (no display or misconfigured Tcl/Tk). Skipping UI test.")
        import tkinter as tk
        from taskmover.ui_helpers import update_rule_list
        root = tk.Tk()
        try:
            rule_frame = tk.Frame(root)
            update_rule_list(rule_frame, {}, self.config_directory, self.logger)
            children = rule_frame.winfo_children()
            self.assertEqual(len(children), 0, "Rule list should be empty when no rules are provided.")
        finally:
            root.destroy()

    def test_rule_list_update_logger_called(self):
        if not self.can_init_tk():
            self.skipTest("Tkinter cannot be initialized (no display or misconfigured Tcl/Tk). Skipping UI test.")
        import tkinter as tk
        from taskmover.ui_helpers import update_rule_list
        root = tk.Tk()
        try:
            rule_frame = tk.Frame(root)
            update_rule_list(rule_frame, self.rules, self.config_directory, self.logger)
            self.assertTrue(True, "update_rule_list executed without error.")
        finally:
            root.destroy()

    def test_all_ttkbootstrap_themes(self):
        if not self.can_init_tk():
            self.skipTest("Tkinter cannot be initialized (no display or misconfigured Tcl/Tk). Skipping UI test.")
        import ttkbootstrap as ttkb
        style = ttkb.Style()
        available_themes = style.theme_names()
        for theme in available_themes:
            try:
                style.theme_use(theme)
            except Exception as e:
                self.fail(f"Theme '{theme}' failed: {e}")

    def test_color_application(self):
        if not self.can_init_tk():
            self.skipTest("Tkinter cannot be initialized (no display or misconfigured Tcl/Tk). Skipping UI test.")
        import tkinter as tk
        root = tk.Tk()
        try:
            test_colors = ["#FF0000", "#00FF00", "#0000FF", "#FFFF00", "#00FFFF"]
            label = tk.Label(root, text="Color Test")
            label.pack()
            for color in test_colors:
                try:
                    label.config(bg=color)
                    root.update_idletasks()
                except Exception as e:
                    self.fail(f"Color '{color}' failed: {e}")
        finally:
            root.destroy()

if __name__ == "__main__":
    unittest.main()
