"""
UI color and dialog helpers for TaskMover.
"""

import tkinter as tk
from tkinter import colorchooser
from tkinter import filedialog

# Color and dialog helpers

def choose_color_and_update(setting, color_var):
    color_code = colorchooser.askcolor(title=f"Choose {setting} Color")[1]
    if color_code:
        color_var.set(color_code)

def browse_path_and_update(base_dir_var, logger):
    selected_path = filedialog.askdirectory()
    if selected_path:
        base_dir_var.set(selected_path)
        logger.info(f"Base directory updated to: {selected_path}")
