import os
import sys
import tkinter
import ttkbootstrap as ttkb
from tkinter import messagebox

# Add the parent directory to the system path to ensure the package is recognized
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from taskmover.ui_helpers import add_rule_button, activate_all_button, deactivate_all_button, execute_button, update_rule_list
from taskmover.logging_config import configure_logger
from taskmover.app import main, setup_ui, save_settings, open_developer_settings, add_menubar_with_settings
from taskmover.config import load_rules, create_default_rules
from taskmover.file_operations import organize_files, unzip_file
def ensure_directory_exists(directory, logger):
    """Ensure a directory exists, creating it if necessary."""
    try:
        os.makedirs(directory, exist_ok=True)
        logger.debug(f"Ensured directory exists: {directory}")
    except Exception as e:
        logger.error(f"Failed to create directory '{directory}': {e}")
        raise

def load_or_initialize_rules(config_path, fallback_path, logger):
    """Load rules from a configuration file or initialize default rules."""
    try:
        if not os.path.exists(config_path):
            logger.warning("Configuration file not found. Creating default rules.")
            return create_default_rules(config_path)
        logger.info("Loading rules from configuration file.")
        return load_rules(config_path, fallback_path)
    except Exception as e:
        logger.error(f"Error loading or initializing rules: {e}")
        raise

def browse_path(base_path_var, logger):
    """Browse for a directory and update the base path variable."""
    directory = tkinter.filedialog.askdirectory()
    if directory:
        base_path_var.set(directory)
        logger.info(f"Base path updated to: {directory}")

def run():
    logger = configure_logger()

    # Check if a display is available
    if not os.environ.get("DISPLAY"):
        logger.error("No display found. Ensure you are running this application in an environment with GUI support.")
        sys.exit("Error: No display found. This application requires a graphical environment.")

    # Define configuration paths
    config_directory = os.path.expanduser("~/default_dir/config")
    ensure_directory_exists(config_directory, logger)

    config_path = os.path.join(config_directory, "rules.yml")
    fallback_path = os.path.join(config_directory, "fallback_conf.yml")

    # Load or initialize rules
    rules = load_or_initialize_rules(config_path, fallback_path, logger)

    # --- Custom UI Setup (buttons above rules, rules with scrollbar, start organize button) ---
    root = ttkb.Window(themename="flatly")
    root.title("TaskMover")
    root.geometry("900x700")

    # Menubar
    from taskmover.ui_helpers import add_menubar_with_settings
    from taskmover.app import save_settings, open_developer_settings, show_license_info
    settings = {}
    style = root.style if hasattr(root, "style") else ttkb.Style()
    add_menubar_with_settings(root, style, settings, save_settings, logger)
    # Add About section to menubar if not present
    import tkinter as tk
    menubar = root.nametowidget(root.winfo_children()[0])
    help_menu = tk.Menu(menubar, tearoff=0)
    help_menu.add_command(label="About", command=show_license_info)
    menubar.add_cascade(label="Help", menu=help_menu)

    # Base Path Frame
    base_path_var = ttkb.StringVar(value=os.path.expanduser("~/default_dir"))
    base_path_frame = ttkb.Frame(root, padding=10, bootstyle="primary")
    base_path_frame.pack(fill="x", pady=10, padx=10)
    ttkb.Label(base_path_frame, text="Base Path:", font=("Helvetica", 12, "bold")).pack(side="left", padx=10)
    ttkb.Entry(base_path_frame, textvariable=base_path_var, width=50).pack(side="left", padx=10)
    ttkb.Button(base_path_frame, text="Browse", bootstyle="success", command=lambda: browse_path(base_path_var, logger)).pack(side="left", padx=10)

    # Button Frame (above rules)
    button_frame = ttkb.Frame(root, padding=10)
    button_frame.pack(fill="x", padx=10, pady=5)
    ttkb.Button(
        button_frame,
        text="Add Rule",
        bootstyle="success",
        command=lambda: add_rule_button(rules, config_path, rule_frame, logger, root)
    ).pack(side="left", padx=5)
    ttkb.Button(
        button_frame,
        text="Activate All",
        bootstyle="primary",
        command=lambda: activate_all_button(rules, config_path, rule_frame, logger)
    ).pack(side="left", padx=5)
    ttkb.Button(
        button_frame,
        text="Deactivate All",
        bootstyle="warning",
        command=lambda: deactivate_all_button(rules, config_path, rule_frame, logger)
    ).pack(side="left", padx=5)
    ttkb.Button(
        button_frame,
        text="Start Organize",
        bootstyle="danger",
        command=lambda: execute_button(base_path_var.get(), rules, logger)
    ).pack(side="left", padx=5)

    # Rule Frame with Scrollbar
    rule_frame_container = ttkb.Frame(root, padding=0)
    rule_frame_container.pack(fill="both", expand=True, padx=10, pady=10)
    canvas = tk.Canvas(rule_frame_container, borderwidth=0, highlightthickness=0)
    scrollbar = ttkb.Scrollbar(rule_frame_container, orient="vertical", command=canvas.yview)
    rule_frame = ttkb.Frame(canvas, padding=10, bootstyle="secondary")
    rule_frame_id = canvas.create_window((0, 0), window=rule_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    def on_frame_configure(event):
        canvas.configure(scrollregion=canvas.bbox("all"))
    rule_frame.bind("<Configure>", on_frame_configure)

    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    canvas.bind_all("<MouseWheel>", _on_mousewheel)

    update_rule_list(rule_frame, rules, config_path, logger)

    logger.info("Starting TaskMover application.")
    root.mainloop()

if __name__ == "__main__":
    run()
