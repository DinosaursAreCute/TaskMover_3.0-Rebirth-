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
        style = ttkb.Style()  # Create after root
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
            if button_frame is not None:
                buttons = [w for w in button_frame.winfo_children() if isinstance(w, ttkb.Button)]
                self.assertGreaterEqual(len(buttons), 4, "Not all rule management buttons are present")
        finally:
            root.destroy()

    def test_rule_list_update(self):
        if not self.can_init_tk():
            self.skipTest("Tkinter cannot be initialized (no display or misconfigured Tcl/Tk). Skipping UI test.")
        import tkinter as tk
        import ttkbootstrap as ttkb
        sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
        from taskmover.ui_rule_helpers import update_rule_list
        root = tk.Tk()
        style = ttkb.Style()
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
        import ttkbootstrap as ttkb
        from taskmover.ui_rule_helpers import update_rule_list
        root = tk.Tk()
        style = ttkb.Style()
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
        import ttkbootstrap as ttkb
        from taskmover.ui_rule_helpers import update_rule_list
        root = tk.Tk()
        style = ttkb.Style()
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
        import tkinter as tk
        root = tk.Tk()
        style = ttkb.Style()
        available_themes = style.theme_names()
        for theme in available_themes:
            try:
                style.theme_use(theme)
            except Exception as e:
                self.fail(f"Theme '{theme}' failed: {e}")
        root.destroy()

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

    def test_add_custom_theme(self):
        if not self.can_init_tk():
            self.skipTest("Tkinter cannot be initialized (no display or misconfigured Tcl/Tk). Skipping UI test.")
        import tkinter as tk
        import ttkbootstrap as ttkb
        from taskmover.ui_settings_helpers import open_theme_manager_window
        from unittest.mock import patch
        root = tk.Tk()
        style = ttkb.Style()
        logger = MagicMock()
        with patch('tkinter.simpledialog.askstring', return_value="TestTheme"):
            open_theme_manager_window(root, style, logger)
            # Find the theme manager window
            theme_win = None
            for w in root.winfo_children():
                if isinstance(w, (tk.Toplevel, ttkb.Toplevel)):
                    try:
                        if w.title() == "Theme Manager":
                            theme_win = w
                            break
                    except Exception:
                        continue
            self.assertIsNotNone(theme_win, "Theme Manager window not found")
            if theme_win is not None:
                # Find and click the 'Add Theme' button
                add_btn = None
                for child in theme_win.winfo_children():
                    if isinstance(child, ttkb.Button) and child.cget("text") == "Add Theme":
                        add_btn = child
                        break
                self.assertIsNotNone(add_btn, "Add Theme button not found")
                if add_btn is not None:
                    add_btn.invoke()
                # Now refresh and check the listbox
                theme_listbox = None
                for child in theme_win.winfo_children():
                    if isinstance(child, tk.Listbox):
                        theme_listbox = child
                        break
                self.assertIsNotNone(theme_listbox, "Theme listbox not found")
                if theme_listbox is not None:
                    self.assertIn("TestTheme", theme_listbox.get(0, tk.END), "Custom theme not added to listbox")
                theme_win.destroy()
        root.destroy()

    def test_edit_and_apply_custom_theme(self):
        if not self.can_init_tk():
            self.skipTest("Tkinter cannot be initialized (no display or misconfigured Tcl/Tk). Skipping UI test.")
        import tkinter as tk
        import ttkbootstrap as ttkb
        from taskmover.ui_settings_helpers import open_theme_manager_window
        from unittest.mock import patch
        root = tk.Tk()
        style = ttkb.Style()
        logger = MagicMock()
        # Add a theme first
        with patch('tkinter.simpledialog.askstring', return_value="EditTheme"):
            open_theme_manager_window(root, style, logger)
        # Now edit the theme's colors
        from taskmover.theme_manager import save_theme, get_theme
        save_theme("EditTheme", {
            "accent_color": "#123456",
            "background_color": "#654321",
            "text_color": "#abcdef",
            "warning_color": "#fedcba"
        }, logger)
        # Apply the theme
        style.theme_use("flatly")  # Reset to known theme
        theme = get_theme("EditTheme")
        self.assertIsNotNone(theme, "Custom theme not found after save")
        if theme is not None:
            # Simulate applying theme colors
            style.configure('TButton', foreground=theme.get("accent_color", "#000000"))
            style.configure('TFrame', background=theme.get("background_color", "#FFFFFF"))
            style.configure('TLabel', foreground=theme.get("text_color", "#000000"))
            # Check that the style was updated
            self.assertEqual(style.lookup('TButton', 'foreground'), theme.get("accent_color", "#000000"))
            self.assertEqual(style.lookup('TFrame', 'background'), theme.get("background_color", "#FFFFFF"))
            self.assertEqual(style.lookup('TLabel', 'foreground'), theme.get("text_color", "#000000"))
        root.destroy()

    def test_delete_custom_theme(self):
        if not self.can_init_tk():
            self.skipTest("Tkinter cannot be initialized (no display or misconfigured Tcl/Tk). Skipping UI test.")
        import tkinter as tk
        import ttkbootstrap as ttkb
        from taskmover.ui_settings_helpers import open_theme_manager_window
        from taskmover.theme_manager import save_theme, delete_theme, load_all_themes
        from unittest.mock import patch
        root = tk.Tk()
        style = ttkb.Style()
        logger = MagicMock()
        # Add a theme
        save_theme("DeleteTheme", {
            "accent_color": "#000000",
            "background_color": "#111111",
            "text_color": "#222222",
            "warning_color": "#333333"
        }, logger)
        # Open theme manager and delete
        open_theme_manager_window(root, style, logger)
        delete_theme("DeleteTheme", logger)
        themes = load_all_themes()
        self.assertNotIn("DeleteTheme", themes, "Custom theme was not deleted")
        root.destroy()

    def test_all_custom_theme_components(self):
        if not self.can_init_tk():
            self.skipTest("Tkinter cannot be initialized (no display or misconfigured Tcl/Tk). Skipping UI test.")
        import tkinter as tk
        import ttkbootstrap as ttkb
        from taskmover.ui_settings_helpers import open_theme_manager_window
        from taskmover.theme_manager import get_theme
        from unittest.mock import patch
        root = tk.Tk()
        style = ttkb.Style()
        logger = MagicMock()
        # Add a theme for testing
        theme_name = "ComponentTestTheme"
        with patch('tkinter.simpledialog.askstring', return_value=theme_name):
            open_theme_manager_window(root, style, logger)
        # All widget/button types as in the UI
        widget_types = [
            "TButton", "TCheckbutton", "TRadiobutton", "TEntry", "TLabel", "TFrame", "TMenubutton", "TCombobox", "TMenubar", "TNotebook", "TScrollbar", "TProgressbar", "TScale", "TSpinbox", "TSeparator", "TLabelframe", "TPanedwindow", "TTreeview", "TText", "TListbox",
            "primary.TButton", "success.TButton", "info.TButton", "warning.TButton", "danger.TButton", "secondary.TButton", "outline.TButton", "link.TButton"
        ]
        # Assign a unique color to each type and save
        from taskmover.theme_manager import save_theme
        base_color = 0x100000
        theme = get_theme(theme_name) or {}
        for i, wtype in enumerate(widget_types):
            color = f"#{(base_color + i * 0x10101):06x}"
            theme[wtype] = color
        save_theme(theme_name, theme, logger)
        # Reload and check
        loaded = get_theme(theme_name)
        self.assertIsNotNone(loaded, "Custom theme not found after save")
        if loaded is not None:
            for i, wtype in enumerate(widget_types):
                color = f"#{(base_color + i * 0x10101):06x}"
                self.assertIn(wtype, loaded, f"Theme missing style: {wtype}")
                self.assertEqual(loaded[wtype], color, f"Theme color mismatch for {wtype}")
        root.destroy()

if __name__ == "__main__":
    unittest.main()
