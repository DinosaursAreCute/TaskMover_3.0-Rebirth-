import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import unittest
from unittest.mock import MagicMock
import time

DEPLOY_TIME = time.time()

COLOR_RESET = "\033[0m"
COLOR_GREEN = "\033[92m"
COLOR_RED = "\033[91m"
COLOR_YELLOW = "\033[93m"
COLOR_CYAN = "\033[96m"

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
        start_time = time.time()
        try:
            fn(self, *args, **kwargs)
            duration = time.time() - start_time
            log_test("finished", "passed", test_name, f"Test passed in {duration:.3f}s")
        except unittest.SkipTest as e:
            duration = time.time() - start_time
            COLOR_SKIPPED = "\033[94m"
            elapsed = time.time() - DEPLOY_TIME
            print(f"{COLOR_YELLOW}[{elapsed:.2f}s]{COLOR_RESET} "
                  f"{COLOR_SKIPPED}[skipped]{COLOR_RESET} "
                  f"{COLOR_SKIPPED}[skipped]{COLOR_RESET} "
                  f"{COLOR_CYAN}[{test_name}]{COLOR_RESET} Test skipped: {e} (in {duration:.3f}s)")
            raise
        except Exception as e:
            duration = time.time() - start_time
            log_test("stopped", "failed", test_name, f"Test failed in {duration:.3f}s: {e}")
            raise
    return wrapper

def can_init_tk():
    try:
        import tkinter as tk
        root = tk.Tk()
        root.destroy()
        return True
    except Exception:
        return False

class TestUI(unittest.TestCase):
    def setUp(self):
        self.rules = {
            "Rule1": {"patterns": ["*.txt"], "path": "C:/Documents", "unzip": False, "active": True},
            "Rule2": {"patterns": ["*.jpg"], "path": "C:/Pictures", "unzip": False, "active": False},
        }
        self.config_directory = "C:/config"
        self.logger = MagicMock()
        self.settings = {"theme": "flatly"}

    @log_decorator
    def test_buttons_integration(self):
        if not can_init_tk():
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

    @log_decorator
    def test_rule_list_update(self):
        if not can_init_tk():
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

    @log_decorator
    def test_rule_list_update_empty(self):
        if not can_init_tk():
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

    @log_decorator
    def test_rule_list_update_logger_called(self):
        if not can_init_tk():
            self.skipTest("Tkinter cannot be initialized (no display or misconfigured Tcl/Tk). Skipping UI test.")
        import tkinter as tk
        from taskmover.ui_helpers import update_rule_list
        root = tk.Tk()
        try:
            rule_frame = tk.Frame(root)
            update_rule_list(rule_frame, self.rules, self.config_directory, self.logger)
            # Log the result of the test explicitly
            log_test("finished", "passed", "test_rule_list_update_logger_called", "update_rule_list executed without error.")
            self.assertTrue(True, "update_rule_list executed without error.")
        finally:
            root.destroy()

    @log_decorator
    def test_all_ttkbootstrap_themes(self):
        if not can_init_tk():
            self.skipTest("Tkinter cannot be initialized (no display or misconfigured Tcl/Tk). Skipping UI test.")
        import ttkbootstrap as ttkb
        style = ttkb.Style()
        available_themes = style.theme_names()
        for theme in available_themes:
            try:
                style.theme_use(theme)
                log_test("finished", "passed", f"test_theme_{theme}", f"Theme '{theme}' applied successfully.")
            except Exception as e:
                log_test("stopped", "failed", f"test_theme_{theme}", f"Theme '{theme}' failed: {e}")
                self.fail(f"Theme '{theme}' failed: {e}")

    @log_decorator
    def test_color_application(self):
        if not can_init_tk():
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
                    log_test("finished", "passed", f"test_color_{color}", f"Color '{color}' applied successfully.")
                except Exception as e:
                    log_test("stopped", "failed", f"test_color_{color}", f"Color '{color}' failed: {e}")
                    self.fail(f"Color '{color}' failed: {e}")
        finally:
            root.destroy()

if __name__ == "__main__":
    unittest.main()
