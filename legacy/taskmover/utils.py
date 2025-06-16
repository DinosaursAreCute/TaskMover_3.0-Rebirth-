import os
import logging
import tkinter.filedialog
import tkinter
from tkinter import messagebox
from pathlib import Path

# Define loggers at the top for consistency
file_ops_logger = logging.getLogger("File Operations")

# Modularized UI helpers are now imported from their respective files.
from .ui_menu_helpers import add_menubar
from .ui_rule_helpers import (
    update_rule_list, toggle_rule_active, toggle_unzip, enable_all_rules, disable_all_rules,
    add_rule_button, delete_rule, delete_multiple_rules, edit_rule
)
from .ui_settings_helpers import (
    open_settings_window, change_theme, choose_color, apply_custom_style
)
from .ui_developer_helpers import (
    trigger_developer_function, execute_button
)
from .ui_color_helpers import (
    choose_color_and_update, browse_path_and_update
)
from .ui_button_helpers import (
    add_buttons_to_ui, activate_all_button, deactivate_all_button
)
from .ui_license_helpers import show_license_info
from .center_window import center_window

# Utility functions (non-UI)
def ensure_directory_exists(directory: str | Path, logger: 'logging.Logger | None' = None) -> None:
    import logging
    try:
        Path(directory).mkdir(parents=True, exist_ok=True)
        if logger is not None:
            logger.debug(f"Ensured directory exists: {directory}")
        file_ops_logger.debug(f"Ensured directory exists: {directory}")
    except Exception as e:
        if logger is not None:
            logger.error(f"Failed to create directory '{directory}': {e}")
        file_ops_logger.error(f"Failed to create directory '{directory}': {e}")
        raise

settings_path = os.path.expanduser("~/default_dir/config/settings.yml")

def reset_colors(settings: dict, save_settings, logger: logging.Logger) -> None:
    """
    Reset all color settings to their default values.
    Args:
        settings (dict): Current application settings.
        save_settings (function): Function to save updated settings.
        logger (logging.Logger): Logger for logging updates.
    """
    default_colors = {"accent_color": None, "background_color": None, "text_color": None}
    settings.update(default_colors)
    try:
        save_settings(settings_path, settings, logger)
        logger.info("Colors reset to default values.")
        messagebox.showinfo("Reset Colors", "All colors have been reset to their default values.")
    except Exception as e:
        logger.error(f"Failed to reset colors: {e}")
        messagebox.showerror("Error", f"Failed to reset colors: {e}")

def show_license_info() -> None:
    """
    Display the license information in a message box.
    """
    license_text = """
MIT License

Copyright (c) 2025 Noah

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the \"Software\"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED \"AS IS\", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
    try:
        messagebox.showinfo("License Information", license_text)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to display license info: {e}")

def browse_path(path_var: tkinter.StringVar, logger: logging.Logger) -> None:
    """
    Open a directory selection dialog and update the given path variable.
    Args:
        path_var (tk.StringVar): Variable to store the selected directory.
        logger (logging.Logger): Logger for logging updates.
    """
    try:
        selected_path = tkinter.filedialog.askdirectory()
        if selected_path:
            path_var.set(selected_path)
            logger.info(f"Base path updated to: {selected_path}")
    except Exception as e:
        logger.error(f"Failed to browse path: {e}")
        messagebox.showerror("Error", f"Failed to select directory: {e}")
