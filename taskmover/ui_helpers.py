import logging
import tkinter as tk
from tkinter import Menu, simpledialog, colorchooser, messagebox, filedialog  # Import correct modules for askstring, askcolor, and askdirectory
import ttkbootstrap as ttkb
import os

from taskmover.app import reset_colors, show_license_info

from taskmover.config import save_rules
import colorlog  # Import colorlog for colored console logging
from taskmover.file_operations import organize_files
from taskmover.rule_operations import add_rule
from taskmover.utils import center_window

logger = logging.getLogger("TaskMover")

def add_menubar(window):
    menubar = Menu(window)
    window.config(menu=menubar)

    file_menu = Menu(menubar, tearoff=0)
    file_menu.add_command(label='Exit', command=window.quit)
    menubar.add_cascade(label='File', menu=file_menu)

def update_rule_list(rule_frame, rules, config_path, logger):
    """Update the rule list UI."""
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

        unzip_var = tk.IntVar(value=1 if rule['unzip'] else 0)
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

def save_rule(rule_key, rules, config_path):
    save_rules(config_path, rules)

def cancel_rule_changes():
    messagebox.showinfo("Info", "Changes canceled.")

def toggle_rule_active(rule_key, rules, config_path, active, logger):
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
    menubar = Menu(window)
    window.config(menu=menubar)

    # File Menu
    file_menu = Menu(menubar, tearoff=0)
    file_menu.add_command(label='Exit', command=window.quit)
    menubar.add_cascade(label='File', menu=file_menu)

    # Settings Menu
    settings_menu = Menu(menubar, tearoff=0)

    # Theme Submenu
    theme_menu = Menu(settings_menu, tearoff=0)
    themes = [
        ("Flatly", "flatly", "●●●"),
        ("Darkly", "darkly", "●●●"),
        ("Cyborg", "cyborg", "●●●"),
        ("Solar", "solar", "●●●"),
        ("Minty", "minty", "●●●"),
        ("Pulse", "pulse", "●●●"),
        ("Journal", "journal", "●●●"),
        ("Sketchy", "sketchy", "●●●"),
        ("Superhero", "superhero", "●●●"),
        ("United", "united", "●●●"),
        ("Morph", "morph", "●●●"),
    ]

    for theme_name, theme_id, dots in themes:
        theme_menu.add_command(
            label=f"{theme_name}  {dots}",
            command=lambda theme_id=theme_id: change_theme(style, settings, save_settings, theme_id, logger)
        )

    settings_menu.add_cascade(label="Themes", menu=theme_menu)

    # Color Settings
    color_menu = Menu(settings_menu, tearoff=0)
    color_menu.add_command(label='Choose Accent Color', command=lambda: choose_color("Accent", style, settings, save_settings, logger))
    color_menu.add_command(label='Choose Background Color', command=lambda: choose_color("Background", style, settings, save_settings, logger))
    color_menu.add_command(label='Choose Text Color', command=lambda: choose_color("Text", style, settings, save_settings, logger))
    color_menu.add_command(label='Reset Colors', command=lambda: reset_colors(settings, save_settings, logger))
    settings_menu.add_cascade(label='Colors', menu=color_menu)

    # Developer Settings
    dev_menu = Menu(settings_menu, tearoff=0)
    dev_menu.add_command(label="Developer Settings", command=lambda: open_developer_settings(window, settings, save_settings, logger))
    settings_menu.add_cascade(label='Developer', menu=dev_menu)

    menubar.add_cascade(label="Settings", menu=settings_menu)

    # Help Menu
    help_menu = Menu(menubar, tearoff=0)
    help_menu.add_command(label="License Information", command=show_license_info)  # Add License Information button
    menubar.add_cascade(label="Help", menu=help_menu)

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
    save_settings(settings,logger)
    logger.info(f"Applied custom style: {custom_style}")

def open_developer_settings(settings, save_settings, logger):
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
        save_settings(settings,logger)
        logger.setLevel(logging_level_var.get())
        logger.info(f"Developer mode set to {dev_mode_var.get()}. Logging level set to {logging_level_var.get()}.")
        for component, var in component_vars.items():
            logger.info(f"Logging for {component}: {'Enabled' if var.get() else 'Disabled'}")
        dev_window.destroy()

    ttkb.Button(dev_window, text="Save", command=save_dev_settings).pack(pady=10)

def change_theme(style, settings, save_settings, theme_name, logger):
    style.theme_use(theme_name)
    settings["theme"] = theme_name
    save_settings(settings,logger)
    logger.info(f"Theme changed to {theme_name}.")

def choose_color(setting, style, settings, save_settings):
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
        save_settings(settings,logger)
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
    delete_window.geometry("400x600")
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

    ttkb.Label(edit_window, text=f"Edit Rule: {rule_key}", font=("Helvetica", 12, "bold")).pack(pady=10)

    # Directory
    ttkb.Label(edit_window, text="Directory:").pack(anchor="w", padx=10)
    dir_var = tk.StringVar(value=rules[rule_key]['path'])
    dir_entry = ttkb.Entry(edit_window, textvariable=dir_var, width=50)
    dir_entry.pack(pady=5, padx=10)

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

def add_rule_button(root, rules, config_path, rule_frame, logger):
    """Add a button to add new rules."""
    ttkb.Button(root, text="Add Rule", command=lambda: add_rule(rules, config_path, rule_frame, logger, root)).pack(pady=5)

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
    button_frame = ttkb.Frame(root)
    button_frame.pack(fill="x", pady=10)

    ttkb.Button(button_frame, text="Add Rule", command=lambda: add_rule(rules, config_path, rule_frame, logger, root)).pack(side="left", padx=5)
    ttkb.Button(button_frame, text="Remove Rule", command=lambda: delete_multiple_rules(rules, config_path, logger, rule_frame)).pack(side="left", padx=5)
    ttkb.Button(button_frame, text="Enable All", command=lambda: enable_all_rules(rules, config_path, rule_frame, logger)).pack(side="left", padx=5)
    ttkb.Button(button_frame, text="Disable All", command=lambda: disable_all_rules(rules, config_path, rule_frame, logger)).pack(side="left", padx=5)
