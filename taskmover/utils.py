import os
import logging
import tkinter.filedialog
from tkinter import messagebox

def center_window(window):
    """Zentriert ein Fenster auf dem Bildschirm."""
    window.update_idletasks()
    width = window.winfo_width()
    height = window.winfo_height()
    x = (window.winfo_screenwidth() // 2) - (width // 2)
    y = (window.winfo_screenheight() // 2) - (height // 2)
    window.geometry(f"{width}x{height}+{x}+{y}")

def ensure_directory_exists(directory, logger=None):
    """Ensure a directory exists, creating it if necessary."""
    try:
        os.makedirs(directory, exist_ok=True)
        if logger:
            logger.debug(f"Ensured directory exists: {directory}")
    except Exception as e:
        if logger:
            logger.error(f"Failed to create directory '{directory}': {e}")
        raise

settings_path = os.path.expanduser("~/default_dir/config/settings.yml")

def reset_colors(settings, save_settings, logger):
    """
    Reset all color settings to their default values.
    Args:
        settings (dict): Current application settings.
        save_settings (function): Function to save updated settings.
        logger (logging.Logger): Logger for logging updates.
    """
    default_colors = {"accent_color": None, "background_color": None, "text_color": None}
    settings.update(default_colors)
    save_settings(settings_path, settings, logger)
    logger.info("Colors reset to default values.")
    messagebox.showinfo("Reset Colors", "All colors have been reset to their default values.")

def show_license_info():
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
    messagebox.showinfo("License Information", license_text)

def browse_path(path_var, logger):
    """
    Open a directory selection dialog and update the given path variable.
    Args:
        path_var (tk.StringVar): Variable to store the selected directory.
        logger (logging.Logger): Logger for logging updates.
    """
    selected_path = tkinter.filedialog.askdirectory()
    if selected_path:
        path_var.set(selected_path)
        logger.info(f"Base path updated to: {selected_path}")
