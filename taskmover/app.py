"""
Main application logic for the TaskMover application.

This module initializes the application, sets up the user interface, and
handles user interactions.
"""

import os
import tkinter as tk
import logging
from tkinter import Menu, filedialog, messagebox, simpledialog, colorchooser  # Import colorchooser for askcolor
import yaml  # Import yaml to fix NameError
import ttkbootstrap as ttkb
import tkinter.scrolledtext as scrolledtext

from .config import load_rules, create_default_rules, save_rules, load_settings, save_settings
from .file_operations import organize_files, move_file, start_organization  # Fixed relative import
from .logging_config import configure_logger
from .rule_operations import add_rule
from .utils import center_window
from .utils import ensure_directory_exists
from .config import load_or_initialize_rules
from .ui_helpers import update_rule_list, enable_all_rules, disable_all_rules
from .utils import reset_colors, show_license_info, browse_path
from .debug_config import draw_debug_lines, display_widget_names, enable_debug_lines, enable_widget_highlighter
from .ui_helpers import open_settings_window
from .ui_helpers import add_menubar_with_settings, update_rule_list, enable_all_rules, disable_all_rules

settings_path = os.path.expanduser("~/default_dir/config/settings.yml")

class TextHandler(logging.Handler):
    """Custom logging handler that writes log messages to a Tkinter Text widget."""
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget

    def emit(self, record):
        msg = self.format(record)
        self.text_widget.after(0, self._append, msg)

    def _append(self, msg):
        self.text_widget.insert('end', msg + '\n')
        self.text_widget.see('end')

def check_first_run(config_directory, base_directory_var, settings, save_settings, logger):
    """Check if this is the first run and prompt for base directory setup."""
    first_run_marker = os.path.join(config_directory, "first_run_marker.txt")
    if not os.path.exists(first_run_marker):
        logger.info("First run detected. Prompting user to select a base directory.")
        messagebox.showinfo("Welcome", "It seems this is your first time running the program. Please select a base directory. This will be used to save your settings.")
        selected_path = filedialog.askdirectory(title="Select Base Directory")
        base_directory_var.set(selected_path or os.path.expanduser("~/default_dir"))
        
        # Prompt for organization folder
        messagebox.showinfo("Select Folder to Organize", "Please select a folder that you want to organize. Default: Downloads")
        organisation_folder = filedialog.askdirectory(title="Select Folder to Organize") or os.path.expanduser("~/Downloads")
        settings["organisation_folder"] = organisation_folder  # Save to settings
        save_settings(settings_path, settings, logger)

        os.makedirs(base_directory_var.get(), exist_ok=True)
        with open(first_run_marker, 'w') as marker_file:
            marker_file.write("This file marks that the program has been run before.")
        logger.info(f"Base directory set to: {base_directory_var.get()}")
        logger.info(f"Organization folder set to: {organisation_folder}")

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

    check_first_run(config_directory, base_directory_var, settings, save_settings, logger)

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
    """Set up the user interface."""
    # Apply settings on startup
    from .config import apply_settings
    apply_settings(root, settings, logger)

    # Add Menubar
    add_menubar_with_settings(root, style, settings, save_settings, logger)

    # Rule List and Scrollbar
    rule_frame_container = ttkb.Frame(root, padding=0)
    rule_frame_container.pack(fill="both", expand=True, padx=10, pady=10)
    canvas = tk.Canvas(rule_frame_container, borderwidth=0, highlightthickness=0)
    scrollbar = ttkb.Scrollbar(rule_frame_container, orient="vertical", command=canvas.yview)
    rule_frame = ttkb.Frame(canvas, padding=10, bootstyle="secondary")
    canvas.create_window((0, 0), window=rule_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    def on_frame_configure(event):
        canvas.configure(scrollregion=canvas.bbox("all"))
    rule_frame.bind("<Configure>", on_frame_configure)

    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    canvas.bind_all("<MouseWheel>", _on_mousewheel)

    update_rule_list(rule_frame, rules, config_directory, logger)

    # Buttons for rule operations
    button_frame = ttkb.Frame(root, padding=10, bootstyle="secondary")
    button_frame.pack(fill="x", padx=10, pady=5, before=rule_frame_container)
    ttkb.Button(button_frame, text="Enable All Rules", bootstyle="light", command=lambda: enable_all_rules(rules, config_directory, rule_frame, logger)).pack(side="left", padx=5)
    ttkb.Button(button_frame, text="Disable All Rules", bootstyle="light", command=lambda: disable_all_rules(rules, config_directory, rule_frame, logger)).pack(side="left", padx=5)
    ttkb.Button(button_frame, text="Add Rule", bootstyle="light", command=lambda: add_rule(rules, config_directory, rule_frame, logger, root)).pack(side="left", padx=5)
    ttkb.Button(button_frame, text="Delete Multiple Rules", bootstyle="light", command=lambda: delete_multiple_rules(rules, config_directory, logger, rule_frame, root)).pack(side="left", padx=5)
    ttkb.Button(button_frame, text="Start Organization", bootstyle="success", command=lambda: start_organization(settings, rules, logger, show_progress=True)).pack(side="left", padx=5)

    # Show log display widget only in developer mode
    if settings.get("developer_mode", False):
        log_frame = ttkb.Frame(root, padding=5, bootstyle="secondary")
        log_frame.pack(fill="both", expand=False, padx=10, pady=(0,10), side="bottom")
        log_label = ttkb.Label(log_frame, text="Application Log:", font=("Helvetica", 10, "bold"))
        log_label.pack(anchor="w")
        log_widget = scrolledtext.ScrolledText(log_frame, height=8, state="normal", wrap="word")
        log_widget.pack(fill="both", expand=True)

        # Attach custom handler to logger
        text_handler = TextHandler(log_widget)
        formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s', datefmt='%H:%M:%S')
        text_handler.setFormatter(formatter)
        logger.addHandler(text_handler)

def browse_path(path_var, logger):
    """Browse and select a directory."""
    selected_path = filedialog.askdirectory()
    if selected_path:
        path_var.set(selected_path)
        logger.info(f"Base path updated to: {selected_path}")

def open_developer_settings(root, settings, logger):
    """Open the developer settings window."""
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
    ttkb.Button(dev_window, text="Create Dummy Files", bootstyle="info", command=lambda: create_dummy_files(os.path.expanduser(settings.get("organisation_folder", "")), logger)).pack(pady=10)

    def save_dev_settings():
        settings["developer_mode"] = dev_mode_var.get() == "Enabled"
        save_settings(settings_path, settings, logger)  # Ensure save_settings is called correctly
        logger.info(f"Developer mode set to {dev_mode_var.get()}.")
        dev_window.destroy()

    ttkb.Button(dev_window, text="Save", command=save_dev_settings).pack(pady=10)

def add_rule(rules, config_directory, rule_frame, logger, root):
    """Add a new rule to the rules dictionary."""
    rule_name = simpledialog.askstring("Add Rule", "Enter the name of the new rule:")
    if rule_name:
        if rule_name in rules:
            messagebox.showerror("Error", f"Rule '{rule_name}' already exists.")
            logger.warning(f"Attempted to add duplicate rule: {rule_name}")
        else:
            rules[rule_name] = {"patterns": [], "path": "", "unzip": False, "active": True}
            save_rules(config_directory, rules)
            update_rule_list(rule_frame, rules, config_directory, logger)
            logger.info(f"Added new rule: {rule_name}")

def remove_rule(rules, config_directory, rule_frame, logger):
    """Remove an existing rule from the rules dictionary."""
    rule_name = simpledialog.askstring("Remove Rule", "Enter the name of the rule to remove:")
    if rule_name:
        if rule_name in rules:
            del rules[rule_name]
            save_rules(config_directory, rules)
            update_rule_list(rule_frame, rules, config_directory, logger)
            logger.info(f"Removed rule: {rule_name}")
        else:
            messagebox.showerror("Error", f"Rule '{rule_name}' does not exist.")
            logger.warning(f"Attempted to remove non-existent rule: {rule_name}")

def delete_multiple_rules(rules, config_directory, logger, rule_frame, root):
    """Delete multiple rules from the rules dictionary."""
    delete_window = tk.Toplevel(root)
    delete_window.title("Delete Rules")
    delete_window.geometry("400x500")
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
            save_rules(rules, logger)
            update_rule_list(rule_frame, rules, config_directory, logger)
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

    dummy_files = [
        "test_document.pdf",
        "image_sample.jpg",
        "video_clip.mp4",
        "archive_file.zip",
        "random_file.txt"
    ]

    try:
        for file_name in dummy_files:
            file_path = os.path.join(base_directory, file_name)
            with open(file_path, "w") as f:
                f.write(f"This is a dummy file: {file_name}")
            logger.info(f"Created dummy file: {file_path}")

        # Only show messagebox if running in a GUI context
        try:
            from tkinter import messagebox
            messagebox.showinfo("Dummy Files Created", f"Dummy files have been created in '{base_directory}'.")
        except Exception:
            pass
    except Exception as e:
        logger.error(f"Error creating dummy files: {e}")
        try:
            from tkinter import messagebox
            messagebox.showerror("Error", f"An error occurred while creating dummy files: {e}")
        except Exception:
            pass

def add_menubar_with_settings(window, style, settings, save_settings, logger):
    """Add a menubar with settings to the main window."""
    menubar = Menu(window)
    window.config(menu=menubar)

    # File Menu
    file_menu = Menu(menubar, tearoff=0)
    file_menu.add_command(label='Exit', command=window.quit)
    menubar.add_cascade(label='File', menu=file_menu)

    # Settings Menu
    settings_menu = Menu(menubar, tearoff=0)
    settings_menu.add_command(label="Open Settings", command=lambda: open_settings_window(window, settings, save_settings, logger)) 
    menubar.add_cascade(label='Settings', menu=settings_menu)

    # Help Menu
    help_menu = Menu(menubar, tearoff=0)
    help_menu.add_command(label="License Information", command=show_license_info)
    menubar.add_cascade(label="Help", menu=help_menu)

def reset_colors(settings, save_settings, logger):
    """Reset all color settings to their default values."""
    default_colors = {"accent_color": None, "background_color": None, "text_color": None}
    settings.update(default_colors)
    save_settings(settings_path, settings, logger)
    logger.info("Colors reset to default values.")
    messagebox.showinfo("Reset Colors", "All colors have been reset to their default values.")

def choose_color(color_type, style, settings, save_settings, logger):
    """Allow the user to choose a color and update the settings."""
    color_code = colorchooser.askcolor(title=f"Choose {color_type} Color")[1]  # Use colorchooser.askcolor
    if color_code:
        settings[f"{color_type.lower()}_color"] = color_code
        save_settings(settings_path, settings, logger)
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

def edit_rule(rule_key, rules, config_directory, logger, rule_frame, root):
    """Edit an existing rule in the rules dictionary."""
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
        save_rules(config_directory, rules)
        logger.info(f"Rule '{rule_key}' updated.")
        update_rule_list(rule_frame, rules, config_directory, logger)
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

def run():
    """
    Main function to initialize and run the TaskMover application.
    """
    logger = configure_logger()
 
    # Define configuration paths
    config_directory = os.path.expanduser("~/default_dir/config")
    ensure_directory_exists(config_directory, logger)

    config_directory = os.path.join(config_directory, "rules.yml")
    fallback_path = os.path.join(config_directory, "fallback_conf.yml")
    settings_path = os.path.expanduser("~/default_dir/config/settings.yml")

    # Load or initialize rules
    rules = load_or_initialize_rules(config_directory, fallback_path, logger)

    # Load settings
    settings = load_settings(settings_path)

    # --- Custom UI Setup ---
    root = ttkb.Window(themename="flatly")
    root.title("TaskMover")
    root.geometry("900x700")

    base_path_var = ttkb.StringVar(value=os.path.expanduser("~/default_dir"))
    style = ttkb.Style()  # Initialize style before using it

    # Load theme dynamically from settings
    if not isinstance(settings, dict):
        logger.warning("Settings is not a valid dictionary. Using default theme.")
        settings = {}
    theme_name = settings.get("theme", "flatly")
    try:
        style.theme_use(theme_name)
        logger.info(f"Theme loaded dynamically from settings: {theme_name}")
    except Exception as e:
        logger.error(f"Failed to load theme '{theme_name}'. Falling back to default theme 'flatly'. Error: {e}")
        style.theme_use("flatly")
    base_directory_var = tk.StringVar(value=os.path.expanduser("~/default_dir"))
    check_first_run(os.path.expanduser("~/default_dir/config"), base_directory_var, settings, save_settings, logger)
    setup_ui(root, base_path_var, rules, config_directory, style, settings, logger)
    logger.info("Starting TaskMover application.")
    

    # Debugging utilities integration
    if enable_debug_lines:
        canvas = tk.Canvas(root)
        canvas.pack(fill=tk.BOTH, expand=True)
        draw_debug_lines(canvas, root, draw_to_center=True)

    if enable_widget_highlighter:
        widget_list = ["Widget1", "Widget2", "Widget3"]  # Example widget names
        display_widget_names(widget_list)

    root.mainloop()

def load_settings(settings_path):
    """Load settings from the settings file with strict validation and error handling."""
    import os
    if not os.path.exists(settings_path):
        return {
            "base_directory": "",
            "theme": "superhero",
            "developer_mode": True,
            "logging_level": "DEBUG",
            "accent_color": "#FFFFFF",
            "background_color": "#FFFFFF",
            "text_color": "#000000",
            "logging_components": {
                "UI": 1,
                "File Operations": 1,
                "Rules": 1,
                "Settings": 1
            }
        }
    try:
        with open(settings_path, "r") as file:
            import yaml
            settings = yaml.safe_load(file)
            # Strict validation: must be a dict and contain required keys
            required_keys = [
                "base_directory", "theme", "developer_mode", "logging_level",
                "accent_color", "background_color", "text_color", "logging_components"
            ]
            if not isinstance(settings, dict) or not all(k in settings for k in required_keys):
                raise ValueError("Settings file is not a valid TaskMover settings dictionary.")
            return settings
    except FileNotFoundError:
        raise FileNotFoundError(f"Settings file not found: {settings_path}")
    except yaml.YAMLError as e:
        raise ValueError(f"Error parsing YAML settings file: {e}")
    except Exception as e:
        raise RuntimeError(f"Failed to load settings: {e}")
