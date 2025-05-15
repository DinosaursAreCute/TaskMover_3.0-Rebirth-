"""
Helper functions for managing the user interface of the TaskMover application.

This module provides utilities for creating and managing UI components such as
menus, rule lists, and settings windows.
"""

import logging
import tkinter as tk
from tkinter import Menu, simpledialog, colorchooser, messagebox, filedialog, ttk, Scrollbar  # Import correct modules for askstring, askcolor, and askdirectory
import ttkbootstrap as ttkb
from ttkbootstrap.constants import *
import os
import winsound  # Import winsound for playing error sounds

from .utils import reset_colors, show_license_info, browse_path

from .config import load_settings, save_rules
import colorlog  # Import colorlog for colored console logging
from .file_operations import organize_files
from .rule_operations import add_rule
from .utils import center_window

logger = logging.getLogger("TaskMover")

settings_path = os.path.expanduser("~/default_dir/config/settings.yml")

def add_menubar(window):
    """Add a basic menubar with a File menu to the given window."""
    menubar = Menu(window)
    window.config(menu=menubar)

    file_menu = Menu(menubar, tearoff=0)
    file_menu.add_command(label='Exit', command=window.quit)
    menubar.add_cascade(label='File', menu=file_menu)

def update_rule_list(rule_frame, rules, config_path, logger):
    """
    Update the rule list UI.

    Args:
        rule_frame (tk.Frame): The frame containing the rule list.
        rules (dict): Dictionary of rules to display.
        config_path (str): Path to the configuration file.
        logger (logging.Logger): Logger for logging updates.
    """
    for widget in rule_frame.winfo_children():
        widget.destroy()

    for rule_key, rule in rules.items():
        frame = ttkb.Frame(rule_frame, padding=10, bootstyle="secondary")
        frame.pack(fill="x", pady=5, padx=10)

        ttkb.Label(frame, text=f"{rule_key}", font=("Helvetica", 12, "bold")).pack(anchor="w", pady=5)
        ttkb.Label(frame, text=f"Patterns: {', '.join(rule['patterns'])}", font=("Helvetica", 10)).pack(anchor="w", padx=10)
        ttkb.Label(frame, text=f"Path: {rule['path']}", font=("Helvetica", 10)).pack(anchor="w", padx=10)

        # Rule Details with Switches
        details_frame = ttkb.Frame(frame)
        details_frame.pack(fill="x", pady=5)

        active_var = tk.IntVar(value=1 if rule['active'] else 0)
        active_switch = ttkb.Checkbutton(
            details_frame,
            text="Active",
            variable=active_var,
            bootstyle="success-switch",  # Use switch style
            command=lambda rk=rule_key, av=active_var: toggle_rule_active(rk, rules, config_path, av.get(), logger)
        )
        active_switch.pack(side="left", padx=10)

        unzip_var = tk.IntVar(value=1 if rule.get('unzip', False) else 0)
        unzip_switch = ttkb.Checkbutton(
            details_frame,
            text="Unzip",
            variable=unzip_var,
            bootstyle="info-switch",  # Use switch style
            command=lambda rk=rule_key, uv=unzip_var: toggle_unzip(rk, rules, config_path, uv.get(), logger)
        )
        unzip_switch.pack(side="left", padx=10)

        # Edit and Delete Buttons
        actions_frame = ttkb.Frame(frame)
        actions_frame.pack(fill="x", pady=5)

        edit_button = ttkb.Button(actions_frame, text="Edit", bootstyle="warning-outline", command=lambda rk=rule_key: edit_rule(rk, rules, config_path, logger, rule_frame))
        edit_button.pack(side="left", padx=10)

        delete_button = ttkb.Button(actions_frame, text="Delete", bootstyle="danger-outline", command=lambda rk=rule_key: delete_rule(rk, rules, config_path, logger, rule_frame))
        delete_button.pack(side="left", padx=10)

def cancel_rule_changes():
    """Display a message indicating that rule changes have been canceled."""
    messagebox.showinfo("Info", "Changes canceled.")

def toggle_rule_active(rule_key, rules, config_path, active, logger):
    """
    Toggle the active state of a rule.

    Args:
        rule_key (str): The key of the rule to toggle.
        rules (dict): Dictionary of rules.
        config_path (str): Path to the configuration file.
        active (bool): New active state.
        logger (logging.Logger): Logger for logging updates.
    """
    rules[rule_key]['active'] = bool(active)
    save_rules(config_path, rules)
    logger.info(f"Rule '{rule_key}' active state set to {bool(active)}.")

def toggle_unzip(rule_key, rules, config_path, unzip, logger):
    rules[rule_key]['unzip'] = bool(unzip)
    save_rules(config_path, rules)
    logger.info(f"Rule '{rule_key}' unzip state set to {bool(unzip)}.")

def enable_all_rules(rules, config_path, rule_frame, logger):
    for rule_key, rule in rules.items():
        rule['active'] = True
        logger.info(f"Rule '{rule_key}' enabled.")
    save_rules(config_path, rules)
    update_rule_list(rule_frame, rules, config_path, logger)  # Update the UI checkboxes dynamically

def disable_all_rules(rules, config_path, rule_frame, logger):
    for rule_key, rule in rules.items():
        rule['active'] = False
        logger.info(f"Rule '{rule_key}' disabled.")
    save_rules(config_path, rules)
    update_rule_list(rule_frame, rules, config_path, logger)  # Update the UI checkboxes dynamically

def add_menubar_with_settings(window, style, settings, save_settings, logger):
    """Add a menubar with settings and other options."""
    menubar = Menu(window)
    window.config(menu=menubar)

    # File Menu
    file_menu = Menu(menubar, tearoff=0)
    file_menu.add_command(label='Exit', command=window.quit)
    menubar.add_cascade(label='File', menu=file_menu)

    # Settings Menu
    settings_menu = Menu(menubar, tearoff=0)
    settings_menu.add_command(label='Open Settings', command=lambda: open_settings_window(window, settings, save_settings, logger))
    menubar.add_cascade(label='Settings', menu=settings_menu)

    # Theme Selector
    theme_menu = Menu(menubar, tearoff=0)
    for theme in style.theme_names():
        theme_menu.add_command(label=theme, command=lambda t=theme: change_theme(style, settings, save_settings, t, logger))
    menubar.add_cascade(label='Themes', menu=theme_menu)

    # Color Selector
    color_menu = Menu(menubar, tearoff=0)
    color_menu.add_command(label='Accent Color', command=lambda: choose_color("accent_color", style, settings, save_settings))
    color_menu.add_command(label='Background Color', command=lambda: choose_color("background_color", style, settings, save_settings))
    color_menu.add_command(label='Text Color', command=lambda: choose_color("text_color", style, settings, save_settings))
    menubar.add_cascade(label='Colors', menu=color_menu)

    # Help Menu
    help_menu = Menu(menubar, tearoff=0)
    help_menu.add_command(label='License Information', command=show_license_info)
    menubar.add_cascade(label='Help', menu=help_menu)

    logger.info("Menubar with settings added.")

def open_settings_window(root, settings, save_settings, logger):
    """
    Open the settings window for modifying application settings.

    Args:
        root (tk.Tk): The root window.
        settings (dict): Current application settings.
        save_settings (function): Function to save updated settings.
        logger (logging.Logger): Logger for logging updates.
    """
    settings_window = tk.Toplevel(root)
    settings_window.attributes('-topmost', True)
    settings_window.title("Settings")
    settings_window.geometry("400x600")

    # Prevent the user from closing or moving focus without saving or discarding
    def on_closing():
        winsound.MessageBeep(winsound.MB_ICONHAND)  # Play error sound
        messagebox.showerror("Error", "You must save or discard changes before closing the settings window.")

    settings_window.protocol("WM_DELETE_WINDOW", on_closing)
    settings_window.transient(root)  # Keep the window on top of the root window

    # Add a scrollbar to the settings window
    canvas = tk.Canvas(settings_window)
    scrollbar = ttk.Scrollbar(settings_window, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    ttkb.Label(scrollable_frame, text="Settings", font=("Helvetica", 14, "bold")).pack(pady=10)

    # Organisation Folder
    ttkb.Label(scrollable_frame, text="Organisation Folder:").pack(anchor="w", padx=10, pady=5)
    organisation_folder_var = tk.StringVar(value=settings.get("organisation_folder", ""))
    organisation_folder_frame = ttkb.Frame(scrollable_frame)
    organisation_folder_frame.pack(fill="x", padx=10, pady=5)
    ttkb.Entry(organisation_folder_frame, textvariable=organisation_folder_var, width=40).pack(side="left", padx=5)
    ttkb.Button(organisation_folder_frame, text="Browse", command=lambda: browse_path_and_update(organisation_folder_var, logger)).pack(side="left", padx=5)

    # Theme Selection
    ttkb.Label(scrollable_frame, text="Theme:").pack(anchor="w", padx=10, pady=5)
    theme_var = tk.StringVar(value=settings.get("theme", "flatly"))

    # Dynamically fetch valid themes
    valid_themes = ttkb.Style().theme_names()
    
    def preview_theme(event):
        try:
            root.style.theme_use(theme_var.get())
        except tk.TclError:
            messagebox.showerror("Invalid Theme", f"'{theme_var.get()}' is not a valid theme. Please select a valid theme.")

    theme_combobox = ttkb.Combobox(scrollable_frame, textvariable=theme_var, values=valid_themes, state="readonly")
    theme_combobox.pack(fill="x", padx=10, pady=5)
    theme_combobox.bind("<<ComboboxSelected>>", preview_theme)

    # Developer Mode
    ttkb.Label(scrollable_frame, text="Developer Mode:").pack(anchor="w", padx=10, pady=5)
    developer_mode_var = tk.BooleanVar(value=settings.get("developer_mode", False))
    ttkb.Checkbutton(scrollable_frame, text="Enable Developer Mode", variable=developer_mode_var, bootstyle="success-switch").pack(anchor="w", padx=10, pady=5)

    # Logging Level
    ttkb.Label(scrollable_frame, text="Logging Level:").pack(anchor="w", padx=10, pady=5)
    logging_level_var = tk.StringVar(value=settings.get("logging_level", "INFO"))
    ttkb.Combobox(scrollable_frame, textvariable=logging_level_var, values=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], state="readonly").pack(fill="x", padx=10, pady=5)
    # Add logging level for different components
    ttkb.Label(scrollable_frame, text="Logging Components:", font=("Helvetica", 10, "bold")).pack(anchor="w", padx=10, pady=5)
    components_frame = ttkb.Frame(scrollable_frame)
    components_frame.pack(fill="x", padx=10, pady=5)

    components = ["UI", "File Operations", "Rules", "Settings"]
    component_vars = {component: tk.IntVar(value=settings.get("logging_components", {}).get(component, 0)) for component in components}

    for component, var in component_vars.items():
        ttkb.Checkbutton(components_frame, text=component, variable=var, bootstyle="info-switch").pack(anchor="w")

    # Add button for developer function
    ttkb.Button(scrollable_frame, text="Create Dummy Files", bootstyle="primary", command=lambda: trigger_developer_function(organisation_folder_var.get(), logger)).pack(anchor="w", padx=10, pady=10)
    # Custom Theme Section
    ttkb.Label(scrollable_frame, text="Custom Theme:", font=("Helvetica", 12, "bold")).pack(anchor="w", padx=10, pady=10)

    accent_color_var = tk.StringVar(value=settings.get("accent_color", "#FFFFFF"))
    ttkb.Label(scrollable_frame, text="Accent Color:").pack(anchor="w", padx=10, pady=5)
    ttkb.Button(scrollable_frame, text="Choose", command=lambda: choose_color_and_preview("accent_color", accent_color_var)).pack(anchor="w", padx=10, pady=5)

    background_color_var = tk.StringVar(value=settings.get("background_color", "#FFFFFF"))
    ttkb.Label(scrollable_frame, text="Background Color:").pack(anchor="w", padx=10, pady=5)
    ttkb.Button(scrollable_frame, text="Choose", command=lambda: choose_color_and_preview("background_color", background_color_var)).pack(anchor="w", padx=10, pady=5)

    text_color_var = tk.StringVar(value=settings.get("text_color", "#000000"))
    ttkb.Label(scrollable_frame, text="Text Color:").pack(anchor="w", padx=10, pady=5)
    ttkb.Button(scrollable_frame, text="Choose", command=lambda: choose_color_and_preview("text_color", text_color_var)).pack(anchor="w", padx=10, pady=5)

    # Reset Colors Button
    ttkb.Button(scrollable_frame, text="Reset Colors", bootstyle="warning", command=lambda: reset_colors(settings, save_settings, logger)).pack(anchor="w", padx=10, pady=5)

    def choose_color_and_preview(setting, color_var):
        color_code = colorchooser.askcolor(title=f"Choose {setting} Color")[1]
        if color_code:
            color_var.set(color_code)
            if setting == "accent_color":
                root.configure(accent_color=color_code)
            elif setting == "background_color":
                root.configure(bg=color_code)
            elif setting == "text_color":
                root.configure(fg=color_code)

    # Save and Cancel Buttons
    def save_changes():
        settings["organisation_folder"] = organisation_folder_var.get()
        settings["theme"] = theme_var.get()
        settings["developer_mode"] = developer_mode_var.get()
        settings["logging_level"] = logging_level_var.get()
        settings["accent_color"] = accent_color_var.get()
        settings["background_color"] = background_color_var.get()
        settings["text_color"] = text_color_var.get()
        settings["logging_components"] = {component: var.get() for component, var in component_vars.items()}

        # Corrected save_settings call to include required arguments
        try:
            root.style.theme_use(settings["theme"])
        except tk.TclError:
            messagebox.showerror("Invalid Theme", f"'{settings['theme']}' is not a valid theme. Please select a valid theme.")
            return

        save_settings(settings_path, settings, logger)
        logger.info("Settings saved successfully.")

        # Apply new settings immediately
        root.style.theme_use(settings["theme"])
    
        logger.setLevel(settings["logging_level"])

        settings_window.destroy()
    def close_window():
        root.style.theme_use(settings["theme"])
        root.configure(bg=settings["background_color"])
        logger.setLevel(settings["logging_level"])
        settings_window.destroy()
    button_frame = ttkb.Frame(scrollable_frame)
    button_frame.pack(fill="x", pady=10)
    ttkb.Button(button_frame, text="Save", bootstyle="success", command=save_changes).pack(side="right", padx=10)
    ttkb.Button(button_frame, text="Cancel", bootstyle="danger", command=close_window).pack(side="right", padx=10)

# Helper functions to prevent premature closing or saving

def browse_path_and_update(base_dir_var, logger):
    """
    Open a directory selection dialog and update the base directory variable.

    Args:
        base_dir_var (tk.StringVar): Variable to store the selected directory.
        logger (logging.Logger): Logger for logging updates.
    """
    selected_path = filedialog.askdirectory()
    if selected_path:
        base_dir_var.set(selected_path)
        logger.info(f"Base directory updated to: {selected_path}")

def choose_color_and_update(setting, color_var):
    color_code = colorchooser.askcolor(title=f"Choose {setting} Color")[1]
    if color_code:
        color_var.set(color_code)

def trigger_developer_function(base_directory, logger):
    logger.info("Developer function triggered.")

    if not base_directory:
        logger.warning("Base directory is not set. Developer function aborted.")
        messagebox.showwarning("Warning", "Base directory is not set. Developer function aborted.")
        return

    # Create dummy files inside the base directory
    try:
        dummy_files = [
            "test_document.pdf",
            "image_sample.jpg",
            "video_clip.mp4",
            "archive_file.zip",
            "random_file.txt"
        ]

        for file_name in dummy_files:
            file_path = os.path.join(base_directory, file_name)
            with open(file_path, "w") as dummy_file:
                dummy_file.write(f"Dummy content for {file_name}")
            logger.info(f"Created dummy file: {file_path}")

        messagebox.showinfo("Developer Function", f"Dummy files created in {base_directory}.")
    except Exception as e:
        logger.error(f"Error creating dummy files: {e}")
        messagebox.showerror("Error", f"An error occurred while creating dummy files: {e}")

def apply_custom_style(style, settings, save_settings, custom_style):
    style.configure('TFrame', background=custom_style["background"])
    style.configure('TLabel', foreground=custom_style["foreground"])
    settings["custom_style"] = custom_style
    save_settings(settings_path, settings,logger)
    logger.info(f"Applied custom style: {custom_style}")

def open_developer_settings(window, settings, save_settings, logger):
    dev_window = tk.Toplevel()
    dev_window.title("Developer Settings")
    dev_window.geometry("400x400")
    center_window(dev_window)

    ttkb.Label(dev_window, text="Developer Settings", font=("Helvetica", 12, "bold")).pack(pady=10)

    # Developer Mode Dropdown
    dev_mode_var = tk.StringVar(value="Enabled" if settings.get("developer_mode", False) else "Disabled")
    ttkb.Label(dev_window, text="Developer Mode:").pack(anchor="w", padx=10)
    dev_mode_dropdown = ttkb.Combobox(dev_window, textvariable=dev_mode_var, values=["Enabled", "Disabled"], state="readonly")
    dev_mode_dropdown.pack(fill="x", padx=10, pady=5)
 
    # Logging Level Dropdown
    logging_level_var = tk.StringVar(value=logging.getLevelName(logger.level))
    ttkb.Label(dev_window, text="Logging Level:").pack(anchor="w", padx=10)
    logging_level_dropdown = ttkb.Combobox(dev_window, textvariable=logging_level_var, values=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], state="readonly")
    logging_level_dropdown.pack(fill="x", padx=10, pady=5)

    # Logging Components Toggles
    ttkb.Label(dev_window, text="Logging Components:", font=("Helvetica", 10, "bold")).pack(anchor="w", padx=10)
    components_frame = ttkb.Frame(dev_window)
    components_frame.pack(fill="x", padx=10, pady=5)

    components = ["UI", "File Operations", "Rules", "Settings"]
    component_vars = {component: tk.IntVar(value=1) for component in components}

    for component, var in component_vars.items():
        ttkb.Checkbutton(components_frame, text=component, variable=var, bootstyle="info-switch").pack(anchor="w")

    def save_dev_settings():
        settings["developer_mode"] = dev_mode_var.get() == "Enabled"
        save_settings(settings_path, settings,logger)
        logger.setLevel(logging_level_var.get())
        logger.info(f"Developer mode set to {dev_mode_var.get()}. Logging level set to {logging_level_var.get()}.")
        for component, var in component_vars.items():
            logger.info(f"Logging for {component}: {'Enabled' if var.get() else 'Disabled'}")
        dev_window.destroy()

    ttkb.Button(dev_window, text="Save", command=save_dev_settings).pack(pady=10)

def change_theme(style, settings, save_settings, theme_name, logger):
    style.theme_use(theme_name)
    settings["theme"] = theme_name
    save_settings(settings_path, settings,logger)
    logger.info(f"Theme changed to {theme_name}.")

def choose_color(setting, style, settings, save_settings):
    color_code = colorchooser.askcolor(title=f"Choose {setting} Color")[1]
    if (color_code):
        if setting == "Accent":
            style.configure('TButton', foreground=color_code)
            style.configure('TLabel', foreground=color_code)
            style.configure('TCheckbutton', foreground=color_code)
        elif setting == "Background":
            style.configure('TFrame', background=color_code)
        elif setting == "Text":
            style.configure('TLabel', foreground=color_code)
        settings[f"{setting.lower()}_color"] = color_code
        save_settings(settings_path, settings,logger)
        logger.info(f"{setting} color changed to {color_code}.")

def delete_rule(rule_key, rules, config_path, logger, rule_frame):
    if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete the rule '{rule_key}'?"):
        del rules[rule_key]
        save_rules(config_path, rules)
        logger.info(f"Rule '{rule_key}' deleted.")
        update_rule_list(rule_frame, rules, config_path, logger)

def delete_multiple_rules(rules, config_path, logger, rule_frame):
    delete_window = tk.Toplevel()
    delete_window.title("Delete Rules")
    delete_window.geometry("600x600")
    center_window(delete_window)

    ttkb.Label(delete_window, text="Select Rules to Delete", font=("Helvetica", 12, "bold")).pack(pady=10)

    listbox = tk.Listbox(delete_window, selectmode=tk.MULTIPLE, width=50, height=15)
    listbox.pack(pady=10, padx=10)

    for rule_key in rules.keys():
        listbox.insert(tk.END, rule_key)

    def confirm_delete():
        selected_indices = listbox.curselection()
        selected_rules = [listbox.get(i) for i in selected_indices]
        if selected_rules and messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete the selected rules?"):
            for rule_key in selected_rules:
                del rules[rule_key]
                logger.info(f"Rule '{rule_key}' deleted.")
            save_rules(config_path, rules)
            update_rule_list(rule_frame, rules, config_path, logger)
            delete_window.destroy()

    ttkb.Button(delete_window, text="Delete Selected", command=confirm_delete).pack(pady=10)
    ttkb.Button(delete_window, text="Cancel", command=delete_window.destroy).pack(pady=5)

def edit_rule(rule_key, rules, config_path, logger, rule_frame):
    edit_window = tk.Toplevel()
    edit_window.title(f"Edit Rule: {rule_key}")
    edit_window.geometry("400x300")
    center_window(edit_window)
    edit_window.attributes('-topmost', True)
    ttkb.Label(edit_window, text=f"Edit Rule: {rule_key}", font=("Helvetica", 12, "bold")).pack(pady=10)

    # Directory
    ttkb.Label(edit_window, text="Directory:").pack(anchor="w", padx=10)
    dir_var = tk.StringVar(value=rules[rule_key]['path'])
    dir_entry = ttkb.Entry(edit_window, textvariable=dir_var, width=50)
    dir_entry.pack(pady=5, padx=10)
    ttkb.Button(edit_window, text="Browse", command=lambda: dir_var.set(filedialog.askdirectory(title="Select Directory"))).pack(pady=5)
    # Patterns
    ttkb.Label(edit_window, text="Patterns (comma-separated):").pack(anchor="w", padx=10)
    patterns_var = tk.StringVar(value=", ".join(rules[rule_key]['patterns']))
    patterns_entry = ttkb.Entry(edit_window, textvariable=patterns_var, width=50)
    patterns_entry.pack(pady=5, padx=10)

    def save_changes():
        rules[rule_key]['path'] = dir_var.get()
        rules[rule_key]['patterns'] = [pattern.strip() for pattern in patterns_var.get().split(",")]
        save_rules(config_path, rules)
        logger.info(f"Rule '{rule_key}' updated.")
        update_rule_list(rule_frame, rules, config_path, logger)
        edit_window.destroy()

    ttkb.Button(edit_window, text="Save", command=save_changes).pack(pady=10)
    ttkb.Button(edit_window, text="Cancel", command=edit_window.destroy).pack(pady=5)

def add_rule_button(rules, config_path, rule_frame, logger, root):
    """Add a new rule to the rules dictionary and update the UI."""
    rule_name = simpledialog.askstring("Add Rule", "Enter the name of the new rule:", parent=root)
    if rule_name:
        if rule_name in rules:
            messagebox.showerror("Error", f"Rule '{rule_name}' already exists.", parent=root)
            logger.warning(f"Attempted to add duplicate rule: {rule_name}")
        else:
            rules[rule_name] = {"patterns": [], "path": "", "unzip": False, "active": True}
            save_rules(config_path, rules)
            update_rule_list(rule_frame, rules, config_path, logger)
            logger.info(f"Added new rule: {rule_name}")

def activate_all_button(rules, config_path, rule_frame, logger):
    """Activate all rules."""
    enable_all_rules(rules, config_path, rule_frame, logger)

def deactivate_all_button(rules, config_path, rule_frame, logger):
    """Deactivate all rules."""
    disable_all_rules(rules, config_path, rule_frame, logger)

def execute_button(base_directory, rules, logger):
    """Execute the file organization process."""
    if not base_directory or not os.path.exists(base_directory):
        logger.error("Invalid or non-existent base directory.")
        messagebox.showerror("Error", "Invalid or non-existent base directory.")
        return

    logger.info("Starting file organization process...")
    try:
        organize_files(base_directory, rules, logger)
        messagebox.showinfo("Success", "File organization completed successfully.")
        logger.info("File organization completed successfully.")
    except Exception as e:
        logger.error(f"Error during file organization: {e}")
        messagebox.showerror("Error", f"An error occurred during file organization: {e}")

def add_buttons_to_ui(root, rules, config_path, rule_frame, logger):
    """Add buttons for adding, removing, enabling, and disabling all rules to the existing UI."""
    button_frame = ttkb.Frame(root, style="warning.TFrame")
    button_frame.pack(fill="x", pady=10)

    ttkb.Button(button_frame, text="Add Rule", command=lambda: add_rule(rules, config_path, rule_frame, logger, root)).pack(side="left", padx=5)
    ttkb.Button(button_frame, text="Remove Rule", command=lambda: delete_multiple_rules(rules, config_path, logger, rule_frame)).pack(side="left", padx=5)
    ttkb.Button(button_frame, text="Enable All", command=lambda: enable_all_rules(rules, config_path, rule_frame, logger)).pack(side="left", padx=5)
    ttkb.Button(button_frame, text="Disable All", command=lambda: disable_all_rules(rules, config_path, rule_frame, logger)).pack(side="left", padx=5)



# License Information
def show_license_info():
    license_window = ttkb.Toplevel()
    license_window.title("License Information")
    license_window.geometry("500x400")

    text_area = ttkb.Text(license_window, wrap=WORD)
    text_area.insert(END, """MIT License\n\nCopyright (c) 2025 Noah\n\nPermission is hereby granted...""")
    text_area.pack(fill=BOTH, expand=True, padx=10, pady=10)
    text_area.config(state=DISABLED)

    ttkb.Button(license_window, text="Close", command=license_window.destroy).pack(pady=10)

