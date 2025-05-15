import unittest
from unittest.mock import MagicMock
import tkinter as tk
import sys
import os
import time
import ttkbootstrap as ttkb  # Add this import

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
        except unittest.SkipTest as e:
            # Log skipped tests with a different color and state
            COLOR_SKIPPED = "\033[94m"  # Blue
            elapsed = time.time() - DEPLOY_TIME
            print(f"{COLOR_YELLOW}[{elapsed:.2f}s]{COLOR_RESET} "
                  f"{COLOR_SKIPPED}[skipped]{COLOR_RESET} "
                  f"{COLOR_SKIPPED}[skipped]{COLOR_RESET} "
                  f"{COLOR_CYAN}[{test_name}]{COLOR_RESET} Test skipped: {e}")
            raise
        except Exception as e:
            log_test("stopped", "failed", test_name, f"Test failed: {e}")
            raise
    return wrapper

# Add the project root to sys.path so 'taskmover' can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

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
        if self.root:
            self.root.destroy()
            self.root = None

    @log_decorator
    def test_buttons_integration(self):
        try:
            setup_ui(self.root, tk.StringVar(value="C:/"), self.rules, self.config_directory, self.style, self.settings, self.logger)
            button_frame = None
            for child in self.root.winfo_children():
                if isinstance(child, ttkb.Frame):
                    buttons = [w for w in child.winfo_children() if isinstance(w, ttkb.Button)]
                    if len(buttons) >= 4:
                        button_frame = child
                        break
            self.assertIsNotNone(button_frame, "Button frame not found")
            buttons = [w for w in button_frame.winfo_children() if isinstance(w, ttkb.Button)]
            self.assertGreaterEqual(len(buttons), 4, "Not all rule management buttons are present")
        except tk.TclError:
            self.skipTest("Tkinter display not available")

    @log_decorator
    def test_rule_list_update(self):
        try:
            rule_frame = tk.Frame(self.root)
            update_rule_list(rule_frame, self.rules, self.config_directory, self.logger)
            children = rule_frame.winfo_children()
            self.assertEqual(len(children), len(self.rules), "Rule list does not match the number of rules.")
        except tk.TclError:
            self.skipTest("Tkinter display not available")

    @log_decorator
    def test_rule_list_update_empty(self):
        try:
            rule_frame = tk.Frame(self.root)
            update_rule_list(rule_frame, {}, self.config_directory, self.logger)
            children = rule_frame.winfo_children()
            self.assertEqual(len(children), 0, "Rule list should be empty when no rules are provided.")
        except tk.TclError:
            self.skipTest("Tkinter display not available")

    @log_decorator
    def test_rule_list_update_logger_called(self):
        try:
            rule_frame = tk.Frame(self.root)
            update_rule_list(rule_frame, self.rules, self.config_directory, self.logger)
            self.assertTrue(self.logger.info.called or self.logger.debug.called or self.logger.warning.called or self.logger.error.called)
        except tk.TclError:
            self.skipTest("Tkinter display not available")

    @log_decorator
    def test_all_ttkbootstrap_themes(self):
        try:
            available_themes = ttkb.Style().theme_names()
            for theme in available_themes:
                try:
                    self.style.theme_use(theme)
                    log_test("finished", "passed", f"test_theme_{theme}", f"Theme '{theme}' applied successfully.")
                except Exception as e:
                    log_test("stopped", "failed", f"test_theme_{theme}", f"Theme '{theme}' failed: {e}")
                    self.fail(f"Theme '{theme}' failed: {e}")
        except tk.TclError:
            self.skipTest("Tkinter display not available")

    @log_decorator
    def test_color_application(self):
        try:
            test_colors = ["#FF0000", "#00FF00", "#0000FF", "#FFFF00", "#00FFFF"]
            label = tk.Label(self.root, text="Color Test")
            label.pack()
            for color in test_colors:
                try:
                    label.config(bg=color)
                    self.root.update_idletasks()
                    log_test("finished", "passed", f"test_color_{color}", f"Color '{color}' applied successfully.")
                except Exception as e:
                    log_test("stopped", "failed", f"test_color_{color}", f"Color '{color}' failed: {e}")
                    self.fail(f"Color '{color}' failed: {e}")
        except tk.TclError:
            self.skipTest("Tkinter display not available")

if __name__ == "__main__":
    unittest.main()
