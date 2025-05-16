"""
Theme management logic for TaskMover.
Provides functions to create, edit, save, load, and apply custom themes.
"""

import os
import ttkbootstrap as ttkb
import tkinter as tk
from tkinter import colorchooser, messagebox, simpledialog

THEMES_PATH = os.path.expanduser("~/default_dir/config/themes.yml")

def save_theme(theme_name, theme_data, logger=None):
    """Save a custom theme to the themes.yml file."""
    import yaml
    themes = load_all_themes()
    themes[theme_name] = theme_data
    os.makedirs(os.path.dirname(THEMES_PATH), exist_ok=True)
    with open(THEMES_PATH, "w") as f:
        yaml.dump(themes, f)
    if logger:
        logger.info(f"Theme '{theme_name}' saved.")

def load_all_themes():
    """Load all custom themes from the themes.yml file."""
    import yaml
    if not os.path.exists(THEMES_PATH):
        return {}
    with open(THEMES_PATH, "r") as f:
        return yaml.safe_load(f) or {}

def apply_theme(style, theme_data):
    """Apply a theme to the ttkbootstrap style object, including special button and menubar colors."""
    style.configure("TButton", foreground=theme_data.get("accent_color", "#007bff"))
    style.configure("TFrame", background=theme_data.get("background_color", "#FFFFFF"))
    style.configure("TLabel", foreground=theme_data.get("text_color", "#000000"))
    style.configure("Warning.TButton", foreground="#000", background=theme_data.get("warning_color", "#ffc107"))
    # Menubar: handled in UI by setting bg/fg on Menu widgets

def delete_theme(theme_name, logger=None):
    """Delete a custom theme from the themes.yml file."""
    import yaml
    themes = load_all_themes()
    if theme_name in themes:
        del themes[theme_name]
        with open(THEMES_PATH, "w") as f:
            yaml.dump(themes, f)
        if logger:
            logger.info(f"Theme '{theme_name}' deleted.")

def get_theme(theme_name):
    """Get a theme's data by name."""
    return load_all_themes().get(theme_name, None)
