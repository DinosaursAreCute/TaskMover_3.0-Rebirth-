import os
import tkinter as tk
import logging
from tkinter import Menu, filedialog, messagebox, simpledialog, colorchooser  # Import colorchooser for askcolor
import yaml  # Import yaml to fix NameError
import ttkbootstrap as ttkb
from .config import load_rules, create_default_rules, save_rules, load_settings, save_settings
from .file_operations import organize_files, move_file, start_organization  # Import move_file to fix NameError
from .ui_helpers import center_window, add_menubar_with_settings, trigger_developer_function, update_rule_list, enable_all_rules, disable_all_rules, delete_rule, delete_multiple_rules, edit_rule  # Ensure these are imported
from .logging_config import configure_logger

def check_first_run(config_directory, base_directory_var, logger):
    """Check if this is the first run and prompt for base directory setup."""
    first_run_marker = os.path.join(config_directory, "first_run_marker.txt")
    if not os.path.exists(first_run_marker):
        logger.info("First run detected. Prompting user to select a base directory.")
        messagebox.showinfo("Welcome", "It seems this is your first time running the program. Please select a base directory.")
        selected_path = filedialog.askdirectory(title="Select Base Directory")
        base_directory_var.set(selected_path or os.path.expanduser("~/default_dir"))
        os.makedirs(base_directory_var.get(), exist_ok=True)
        with open(first_run_marker, 'w') as marker_file:
            marker_file.write("This file marks that the program has been run before.")
        logger.info(f"Base directory set to: {base_directory_var.get()}")

def main(rules, logger):
    """Main entry point for the application."""
    settings = load_settings(logger)
    logger.debug(f"Loaded settings: {settings}")

    # Reconfigure logger based on developer mode
    developer_mode = settings.get("developer_mode", False)
    logger = configure_logger(developer_mode=developer_mode)

    root = tk.Tk()
    root.withdraw()

    base_directory_var = tk.StringVar(value=os.path.expanduser("~/default_dir"))
    config_directory = os.path.join(base_directory_var.get(), "config")
    os.makedirs(config_directory, exist_ok=True)

    check_first_run(config_directory, base_directory_var, logger)

    root.deiconify()
    root.title("File Organizer")
    root.geometry("900x700")
    center_window(root)

    style = ttkb.Style()
    style.theme_use(settings.get("theme", "flatly"))

    # UI Setup
    base_path_var = tk.StringVar(value=base_directory_var.get())
    setup_ui(root, base_path_var, rules, config_directory, style, settings, logger)

    root.mainloop()
    logger.info("Application exited successfully.")

def setup_ui(root, base_path_var, rules, config_directory, style, settings, logger):
    """Set up the main UI components."""
    # Base Path Frame
    base_path_frame = ttkb.Frame(root, padding=10, bootstyle="primary")
    base_path_frame.pack(fill="x", pady=10, padx=10)

    ttkb.Label(base_path_frame, text="Base Path:", font=("Helvetica", 12, "bold")).pack(side="left", padx=10)
    ttkb.Entry(base_path_frame, textvariable=base_path_var, width=50).pack(side="left", padx=10)
    ttkb.Button(base_path_frame, text="Browse", bootstyle="success", command=lambda: browse_path(base_path_var, logger)).pack(side="left", padx=10)

    # Rule List and Buttons
    rule_frame = ttkb.Frame(root, padding=10, bootstyle="secondary")
    rule_frame.pack(fill="both", expand=True, padx=10, pady=10)
    update_rule_list(rule_frame, rules, config_directory, logger)  # Removed extra 'root' argument

    # Menubar
    add_menubar_with_settings(root, style, settings, save_settings, logger,base_directory=base_path_var.get())

def browse_path(path_var, logger):
    """Browse and select a directory."""
    selected_path = filedialog.askdirectory()
    if selected_path:
        path_var.set(selected_path)
        logger.info(f"Base path updated to: {selected_path}")

def load_settings(logger):
    settings_path = os.path.expanduser("~/default_dir/config/settings.yml")
    if not os.path.exists(settings_path):
        # Create default settings if the file does not exist
        default_settings = {"theme": "flatly", "developer_mode": False, "accent_color": None, "background_color": None, "text_color": None}
        save_settings(default_settings, logger)  # Pass logger to save_settings
        return default_settings
    try:
        with open(settings_path, "r") as file:
            settings = yaml.safe_load(file)
            if not isinstance(settings, dict):  # Ensure the loaded settings are a dictionary
                raise ValueError("Invalid settings format")
            return settings
    except (yaml.YAMLError, ValueError):
        # If the file is invalid, recreate it with default settings
        default_settings = {"theme": "flatly", "developer_mode": False, "accent_color": None, "background_color": None, "text_color": None}
        save_settings(default_settings, logger)  # Pass logger to save_settings
        return default_settings

def save_settings(settings, logger):
    settings_path = os.path.expanduser("~/default_dir/config/settings.yml")
    os.makedirs(os.path.dirname(settings_path), exist_ok=True)  # Ensure the directory exists
    with open(settings_path, "w") as file:
        yaml.dump(settings, file)
    logger.info("Settings saved successfully.")

def open_developer_settings(root, settings, save_settings, logger):
    dev_window = tk.Toplevel(root)
    dev_window.title("Developer Settings")
    dev_window.geometry("400x300")
    center_window(dev_window)

    ttkb.Label(dev_window, text="Developer Settings", font=("Helvetica", 12, "bold")).pack(pady=10)

    # Developer Mode Dropdown
    dev_mode_var = tk.StringVar(value="Enabled" if settings.get("developer_mode", False) else "Disabled")
    ttkb.Label(dev_window, text="Developer Mode:").pack(anchor="w", padx=10)
    dev_mode_dropdown = ttkb.Combobox(dev_window, textvariable=dev_mode_var, values=["Enabled", "Disabled"], state="readonly")
    dev_mode_dropdown.pack(fill="x", padx=10, pady=5)

    # Create Dummy Files Button
    ttkb.Button(dev_window, text="Create Dummy Files", bootstyle="info", command=lambda: create_dummy_files(settings.get("base_directory", "~/default_dir"), logger)).pack(pady=10)

    def save_dev_settings():
        settings["developer_mode"] = dev_mode_var.get() == "Enabled"
        save_settings(settings,logger)  # Ensure save_settings is called correctly
        logger.info(f"Developer mode set to {dev_mode_var.get()}.")
        dev_window.destroy()

    ttkb.Button(dev_window, text="Save", command=save_dev_settings).pack(pady=10)

def add_rule(rules, config_path, rule_frame, logger, root):
    rule_name = simpledialog.askstring("Add Rule", "Enter the name of the new rule:")
    if rule_name:
        if rule_name in rules:
            messagebox.showerror("Error", f"Rule '{rule_name}' already exists.")
            logger.warning(f"Attempted to add duplicate rule: {rule_name}")
        else:
            rules[rule_name] = {"patterns": [], "path": "", "unzip": False, "active": True}
            save_rules(config_path, rules)
            update_rule_list(rule_frame, rules, config_path, logger, root)
            logger.info(f"Added new rule: {rule_name}")

def remove_rule(rules, config_path, rule_frame, logger):
    rule_name = simpledialog.askstring("Remove Rule", "Enter the name of the rule to remove:")
    if rule_name:
        if rule_name in rules:
            del rules[rule_name]
            save_rules(config_path, rules)
            update_rule_list(rule_frame, rules, config_path, logger)
            logger.info(f"Removed rule: {rule_name}")
        else:
            messagebox.showerror("Error", f"Rule '{rule_name}' does not exist.")
            logger.warning(f"Attempted to remove non-existent rule: {rule_name}")

def delete_multiple_rules(rules, config_path, logger, rule_frame, root):
    delete_window = tk.Toplevel(root)
    delete_window.title("Delete Rules")
    delete_window.geometry("400x300")
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
            save_rules(config_path, rules, logger)
            update_rule_list(rule_frame, rules, config_path, logger)
            delete_window.destroy()

    ttkb.Button(delete_window, text="Delete Selected", command=confirm_delete).pack(pady=10)
    ttkb.Button(delete_window, text="Cancel", command=delete_window.destroy).pack(pady=5)

def create_dummy_files(base_directory, logger):
    """Create dummy files of various types in the base directory for testing."""
    if not base_directory:
        base_directory = os.path.expanduser("~/default_dir")  # Use default_dir if base_directory is not provided
        logger.warning(f"Base directory not provided. Using default directory: {base_directory}")

    if not os.path.exists(base_directory):
        os.makedirs(base_directory, exist_ok=True)
        logger.info(f"Base directory '{base_directory}' created.")

    dummy_files = {
        "Documents": ["test1.pdf", "test2.docx", "test3.txt"],
        "Pictures": ["image1.jpg", "image2.png", "image3.gif"],
        "Videos": ["video1.mp4", "video2.mkv", "video3.avi"],
        "Archives": ["archive1.zip", "archive2.rar"],
        "Others": ["random1.exe", "random2.tmp", "random3.log"]
    }

    try:
        for category, files in dummy_files.items():
            for file_name in files:
                file_path = os.path.join(base_directory, file_name)
                with open(file_path, "w") as f:
                    f.write(f"This is a dummy {category} file: {file_name}")
                logger.info(f"Created dummy file: {file_path}")

        messagebox.showinfo("Dummy Files Created", f"Dummy files have been created in '{base_directory}'.")
    except Exception as e:
        logger.error(f"Error creating dummy files: {e}")
        messagebox.showerror("Error", f"An error occurred while creating dummy files: {e}")

def add_menubar_with_settings(window, style, settings, save_settings, logger, base_directory):
    def change_theme(style, settings, save_settings, theme_id):
        """Change the application's theme."""
        style.theme_use(theme_id)
        settings["theme"] = theme_id
        save_settings(settings, logger)
        logger.info(f"Theme changed to: {theme_id}")
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
            command=lambda theme_id=theme_id: change_theme(style, settings, save_settings, theme_id)  # Correctly pass theme_id
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

def reset_colors(settings, save_settings, logger):
    """Reset all color settings to their default values."""
    default_colors = {"accent_color": None, "background_color": None, "text_color": None}
    settings.update(default_colors)
    save_settings(settings, logger)
    logger.info("Colors reset to default values.")
    messagebox.showinfo("Reset Colors", "All colors have been reset to their default values.")

def choose_color(color_type, style, settings, save_settings, logger):
    """Allow the user to choose a color and update the settings."""
    color_code = colorchooser.askcolor(title=f"Choose {color_type} Color")[1]  # Use colorchooser.askcolor
    if color_code:
        settings[f"{color_type.lower()}_color"] = color_code
        save_settings(settings, logger)
        logger.info(f"{color_type} color updated to: {color_code}")

        # Apply the selected color to the UI
        if color_type == "Accent":
            style.configure("TButton", foreground=color_code)
            style.configure("TCheckbutton", foreground=color_code)
        elif color_type == "Background":
            style.configure("TFrame", background=color_code)
            style.configure("TLabel", background=color_code)
            style.configure("TButton", background=color_code)
        elif color_type == "Text":
            style.configure("TLabel", foreground=color_code)
            style.configure("TEntry", foreground=color_code)
            style.configure("TLabel", foreground=color_code)


        logger.info(f"{color_type} color applied to the UI.")

def edit_rule(rule_key, rules, config_path, logger, rule_frame, root):
    edit_window = tk.Toplevel(root)
    edit_window.title(f"Edit Rule: {rule_key}")
    edit_window.geometry("400x300")
    center_window(edit_window)

    ttkb.Label(edit_window, text=f"Edit Rule: {rule_key}", font=("Helvetica", 12, "bold")).pack(pady=10)

    # Directory
    ttkb.Label(edit_window, text="Directory:").pack(anchor="w", padx=10)
    dir_var = tk.StringVar(value=rules[rule_key]['path'])
    dir_frame = ttkb.Frame(edit_window)
    dir_frame.pack(fill="x", padx=10, pady=5)

    dir_entry = ttkb.Entry(dir_frame, textvariable=dir_var, width=40)
    dir_entry.pack(side="left", padx=5)

    def browse_directory():
        selected_path = filedialog.askdirectory(title="Select Directory")
        if selected_path:
            dir_var.set(selected_path)
            logger.info(f"Updated directory for rule '{rule_key}' to: {selected_path}")

    browse_button = ttkb.Button(dir_frame, text="Browse", bootstyle="success", command=browse_directory)
    browse_button.pack(side="left", padx=5)

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

def show_license_info():
    """Display the license information in a message box."""
    license_text = """
MIT License

Copyright (c) 2025 Noah

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
    messagebox.showinfo("License Information", license_text)