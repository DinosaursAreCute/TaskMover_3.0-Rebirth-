"""
UI menu-related helper functions for TaskMover.
"""

import tkinter as tk
from tkinter import Menu
import logging
from .ui_license_helpers import show_license_info

def add_menubar(window, style=None, settings=None, save_settings=None, logger=None):
    """Add a basic menubar with a File menu to the given window. Accepts extra parameters for compatibility."""
    menubar = Menu(window)
    window.config(menu=menubar)

    file_menu = Menu(menubar, tearoff=0)
    file_menu.add_command(label='Exit', command=window.quit)
    menubar.add_cascade(label='File', menu=file_menu)

    # Add Settings menu
    if style and settings and save_settings and logger:
        settings_menu = Menu(menubar, tearoff=0)
        settings_menu.add_command(label='Settings', command=lambda: __import__('taskmover.ui_settings_helpers').ui_settings_helpers.open_settings_window(window, settings, save_settings, logger))
        menubar.add_cascade(label='Settings', menu=settings_menu)
    # Add Help menu with License
    help_menu = Menu(menubar, tearoff=0)
    help_menu.add_command(label='License', command=show_license_info)
    menubar.add_cascade(label='Help', menu=help_menu)

# Additional menu-related helpers can be added here.
