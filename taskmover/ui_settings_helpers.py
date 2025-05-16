"""
Settings and theme UI helpers for TaskMover.
"""

import tkinter as tk
import ttkbootstrap as ttkb
from tkinter import messagebox, colorchooser
from taskmover.config import save_rules
from .ui_color_helpers import choose_color_and_update, browse_path_and_update
from .ui_developer_helpers import trigger_developer_function

# Settings window and theme helpers

def open_settings_window(root, settings, save_settings, logger):
    settings_window = tk.Toplevel(root)
    settings_window.attributes('-topmost', True)
    settings_window.title("Settings")
    settings_window.geometry("400x600")
    canvas = tk.Canvas(settings_window)
    scrollbar = ttkb.Scrollbar(settings_window, orient="vertical", command=canvas.yview)
    scrollable_frame = ttkb.Frame(canvas)
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    ttkb.Label(scrollable_frame, text="Settings", font=("Helvetica", 14, "bold")).pack(pady=10)
    ttkb.Label(scrollable_frame, text="Organisation Folder:").pack(anchor="w", padx=10, pady=5)
    organisation_folder_var = tk.StringVar(value=settings.get("organisation_folder", ""))
    organisation_folder_frame = ttkb.Frame(scrollable_frame)
    organisation_folder_frame.pack(fill="x", padx=10, pady=5)
    ttkb.Entry(organisation_folder_frame, textvariable=organisation_folder_var, width=40).pack(side="left", padx=5)
    ttkb.Button(organisation_folder_frame, text="Browse", command=lambda: browse_path_and_update(organisation_folder_var, logger)).pack(side="left", padx=5)
    ttkb.Label(scrollable_frame, text="Theme:").pack(anchor="w", padx=10, pady=5)
    theme_var = tk.StringVar(value=settings.get("theme", "flatly"))
    valid_themes = ttkb.Style().theme_names()
    def preview_theme(event):
        try:
            root.style.theme_use(theme_var.get())
        except tk.TclError:
            messagebox.showerror("Invalid Theme", f"'{theme_var.get()}' is not a valid theme. Please select a valid theme.")
    theme_combobox = ttkb.Combobox(scrollable_frame, textvariable=theme_var, values=valid_themes, state="readonly")
    theme_combobox.pack(fill="x", padx=10, pady=5)
    theme_combobox.bind("<<ComboboxSelected>>", preview_theme)
    ttkb.Label(scrollable_frame, text="Developer Mode:").pack(anchor="w", padx=10, pady=5)
    developer_mode_var = tk.BooleanVar(value=settings.get("developer_mode", False))
    ttkb.Checkbutton(scrollable_frame, text="Enable Developer Mode", variable=developer_mode_var).pack(anchor="w", padx=10, pady=5)
    ttkb.Label(scrollable_frame, text="Logging Level:").pack(anchor="w", padx=10, pady=5)
    logging_level_var = tk.StringVar(value=settings.get("logging_level", "INFO"))
    ttkb.Combobox(scrollable_frame, textvariable=logging_level_var, values=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], state="readonly").pack(fill="x", padx=10, pady=5)
    ttkb.Label(scrollable_frame, text="Logging Components:", font=("Helvetica", 10, "bold")).pack(anchor="w", padx=10, pady=5)
    components_frame = ttkb.Frame(scrollable_frame)
    components_frame.pack(fill="x", padx=10, pady=5)
    components = ["UI", "File Operations", "Rules", "Settings"]
    component_vars = {component: tk.IntVar(value=settings.get("logging_components", {}).get(component, 0)) for component in components}
    for component, var in component_vars.items():
        ttkb.Checkbutton(components_frame, text=component, variable=var).pack(anchor="w")
    ttkb.Button(scrollable_frame, text="Create Dummy Files", command=lambda: trigger_developer_function(organisation_folder_var.get(), logger)).pack(anchor="w", padx=10, pady=10)
    ttkb.Label(scrollable_frame, text="Custom Theme:", font=("Helvetica", 12, "bold")).pack(anchor="w", padx=10, pady=10)
    accent_color_var = tk.StringVar(value=settings.get("accent_color", "#FFFFFF"))
    ttkb.Label(scrollable_frame, text="Accent Color:").pack(anchor="w", padx=10, pady=5)
    ttkb.Button(scrollable_frame, text="Choose", command=lambda: choose_color_and_update("accent_color", accent_color_var)).pack(anchor="w", padx=10, pady=5)
    background_color_var = tk.StringVar(value=settings.get("background_color", "#FFFFFF"))
    ttkb.Label(scrollable_frame, text="Background Color:").pack(anchor="w", padx=10, pady=5)
    ttkb.Button(scrollable_frame, text="Choose", command=lambda: choose_color_and_update("background_color", background_color_var)).pack(anchor="w", padx=10, pady=5)
    text_color_var = tk.StringVar(value=settings.get("text_color", "#000000"))
    ttkb.Label(scrollable_frame, text="Text Color:").pack(anchor="w", padx=10, pady=5)
    ttkb.Button(scrollable_frame, text="Choose", command=lambda: choose_color_and_update("text_color", text_color_var)).pack(anchor="w", padx=10, pady=5)
    def reset_colors_command():
        from .utils import reset_colors
        reset_colors(settings, save_settings, logger)
    ttkb.Button(scrollable_frame, text="Reset Colors", command=reset_colors_command).pack(anchor="w", padx=10, pady=5)
    def save_changes():
        settings["organisation_folder"] = organisation_folder_var.get()
        settings["theme"] = theme_var.get()
        settings["developer_mode"] = developer_mode_var.get()
        settings["logging_level"] = logging_level_var.get()
        settings["accent_color"] = accent_color_var.get()
        settings["background_color"] = background_color_var.get()
        settings["text_color"] = text_color_var.get()
        settings["logging_components"] = {component: var.get() for component, var in component_vars.items()}
        try:
            root.style.theme_use(settings["theme"])
        except Exception:
            pass
        # Use the correct signature for save_settings
        from taskmover.config import save_settings as save_settings_func
        import os
        settings_path = os.path.expanduser("~/default_dir/config/settings.yml")
        save_settings_func(settings_path, settings, logger)
        logger.info("Settings saved successfully.")
        settings_window.destroy()
    def close_window():
        settings_window.destroy()
    button_frame = ttkb.Frame(scrollable_frame)
    button_frame.pack(fill="x", pady=10)
    ttkb.Button(button_frame, text="Save", command=save_changes).pack(side="right", padx=10)
    ttkb.Button(button_frame, text="Cancel", command=close_window).pack(side="right", padx=10)

def change_theme(style, settings, save_settings, theme_name, logger):
    style.theme_use(theme_name)
    settings["theme"] = theme_name
    try:
        bg = style.lookup("TFrame", "background") or style.lookup("TLabel", "background")
        fg = style.lookup("TLabel", "foreground")
        accent = style.lookup("TButton", "foreground")
        if bg:
            settings["background_color"] = bg
        if fg:
            settings["text_color"] = fg
        if accent:
            settings["accent_color"] = accent
        logger.info(f"Theme colors saved as custom colors: bg={bg}, fg={fg}, accent={accent}")
    except Exception as e:
        logger.warning(f"Could not extract theme colors: {e}")
    save_settings(settings)
    logger.info(f"Theme changed to {theme_name}.")

def choose_color(setting, style, settings, save_settings, logger):
    color_code = colorchooser.askcolor(title=f"Choose {setting} Color")[1]
    if color_code:
        if setting == "Accent":
            style.configure('TButton', foreground=color_code)
            style.configure('TLabel', foreground=color_code)
            style.configure('TCheckbutton', foreground=color_code)
        elif setting == "Background":
            style.configure('TFrame', background=color_code)
        elif setting == "Text":
            style.configure('TLabel', foreground=color_code)
        settings[f"{setting.lower()}_color"] = color_code
        save_settings(settings)
        logger.info(f"{setting} color changed to {color_code}.")

def apply_custom_style(style, settings, save_settings, custom_style, logger):
    style.configure('TFrame', background=custom_style["background"])
    style.configure('TLabel', foreground=custom_style["foreground"])
    settings["custom_style"] = custom_style
    save_settings(settings)
    logger.info(f"Applied custom style: {custom_style}")
