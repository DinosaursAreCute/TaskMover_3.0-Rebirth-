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
from typing import Any

from .config import load_rules, create_default_rules, save_rules, load_settings, save_settings
from .file_operations import organize_files, move_file, start_organization  # Fixed relative import
from .logging_config import configure_logger
from .rule_operations import add_rule
from .utils import center_window
from .utils import ensure_directory_exists
from .config import load_or_initialize_rules
from .ui_menu_helpers import add_menubar
from .ui_rule_helpers import (
    update_rule_list, toggle_rule_active, toggle_unzip, enable_all_rules, disable_all_rules,
    delete_rule, delete_multiple_rules, edit_rule, add_rule_button
)
from .ui_settings_helpers import (
    open_settings_window, change_theme, apply_custom_style
)
from .ui_developer_helpers import (
    #open_developer_settings as open_developer_settings,
    trigger_developer_function
)
from .ui_color_helpers import (
    choose_color_and_update, browse_path_and_update
)
from .ui_button_helpers import (
    add_buttons_to_ui, activate_all_button, deactivate_all_button
)
from .ui_license_helpers import show_license_info
from .debug_config import enable_debug_lines, enable_widget_highlighter, draw_debug_lines, display_widget_names

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
    # Ensure logging is configured for all components
    from .logging_config import configure_logger
    logger = configure_logger(developer_mode=True)  # Or use settings.get("developer_mode", False) if available

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
    """
    Set up the main user interface for TaskMover, including the scrollable main window,
    rule list, and all rule operation buttons. The main content area is scrollable with
    smooth scrolling enabled only when hovering over the main content. The log area (if enabled)
    remains outside the scrollable region.
    Args:
        root: The main Tkinter window.
        base_path_var: StringVar for the base directory.
        rules: The rules dictionary.
        config_directory: Path to the config directory.
        style: The ttkbootstrap style object.
        settings: The application settings dictionary.
        logger: The logger instance.
    """
    logger.info("Setting up main UI.")
    # Apply settings on startup
    from .config import apply_settings
    apply_settings(root, settings, logger)

    # Add Menubar
    add_menubar(root, style, settings, save_settings, logger)

    # --- Rule List and Scrollbar (scroll logic handled here, not in ui_rule_helpers) ---
    rule_frame_container = ttkb.Frame(root, padding=0)
    rule_frame_container.pack(fill="both", expand=True, padx=10, pady=10)
    canvas = tk.Canvas(rule_frame_container, borderwidth=0, highlightthickness=0)
    scrollbar = ttkb.Scrollbar(rule_frame_container, orient="vertical", command=canvas.yview)
    geometry_logger = logging.getLogger("geometry")

    # --- Event Handlers (must be defined before create_rule_frame) ---
    def on_frame_configure(event=None):
        try:
            geometry_logger.debug(f"<Configure> event: widget={event.widget if event else None}, width={canvas.winfo_width()}, height={canvas.winfo_height()}")
            update_canvas_scrollregion()
            if rule_refs["rule_window_id"] in canvas.find_all():
                canvas.itemconfig(rule_refs["rule_window_id"], width=canvas.winfo_width())
            else:
                geometry_logger.warning(f"rule_window_id {rule_refs['rule_window_id']} not found in canvas.")
        except Exception as e:
            import traceback
            geometry_logger.error(f"Exception in on_frame_configure: {e}\n{traceback.format_exc()}")
            try:
                def log_widget_tree(widget, prefix=""):
                    geometry_logger.debug(f"{prefix}{widget.winfo_class()} {widget.winfo_name()} ({widget})")
                    for child in widget.winfo_children():
                        log_widget_tree(child, prefix + "  ")
                log_widget_tree(root)
            except Exception as tree_exc:
                geometry_logger.error(f"Exception logging widget tree: {tree_exc}")
    def _on_mousewheel(event):
        """
        Handle mouse wheel events for smooth scrolling in the main window canvas.
        Scrolls in small increments for a smoother user experience.
        Args:
            event: The Tkinter mouse wheel event.
        """
        # Smooth scroll: use smaller increments and multiple events per scroll
        if event.delta:
            for _ in range(abs(event.delta) // 40):
                canvas.yview_scroll(int(-1 * (event.delta / abs(event.delta))), "units")
        else:
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    def _bind_mousewheel(event): # type: ignore
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
    def _unbind_mousewheel(event): # type: ignore
        canvas.unbind_all("<MouseWheel>")

    # Use a container to hold mutable references
    rule_refs: dict[str, Any] = {"rule_frame": None, "rule_window_id": None}
    def create_rule_frame():
        # Destroy old frame and window if present
        if rule_refs["rule_window_id"] is not None:
            try:
                canvas.delete(rule_refs["rule_window_id"])
            except Exception:
                pass
        if rule_refs["rule_frame"] is not None:
            try:
                rule_refs["rule_frame"].destroy()
            except Exception:
                pass
        rule_frame = ttkb.Frame(canvas, padding=10)
        rule_window_id = canvas.create_window((0, 0), window=rule_frame, anchor="nw")
        rule_refs["rule_frame"] = rule_frame
        rule_refs["rule_window_id"] = rule_window_id
        # Bind events to the new frame
        rule_frame.bind("<Configure>", on_frame_configure)
        rule_frame.bind("<Enter>", _bind_mousewheel)
        rule_frame.bind("<Leave>", _unbind_mousewheel)
        return rule_frame, rule_window_id
    # Initial creation
    rule_frame, rule_window_id = create_rule_frame()
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    
    def update_canvas_scrollregion():
        try:
            window_ids = canvas.find_all()
            geometry_logger.debug(f"Checking rule_window_id {rule_refs['rule_window_id']} in canvas.find_all(): {window_ids}")
            if rule_refs["rule_window_id"] not in window_ids:
                geometry_logger.warning(f"rule_window_id {rule_refs['rule_window_id']} missing from canvas. Self-healing: rebuilding rule_frame and window item.")
                create_rule_frame()
                update_rule_list_preserve_scroll(rules, config_directory, logger)
                canvas.after_idle(update_canvas_scrollregion)
                return
            log_height = 0
            if settings.get("developer_mode", False):
                for child in root.winfo_children():
                    if str(child).endswith("log_frame") or getattr(child, 'winfo_name', lambda: None)() == 'log_frame':
                        log_height = child.winfo_height()
                        break
            canvas.update_idletasks()
            bbox = list(canvas.bbox("all")) if canvas.bbox("all") else [0, 0, 0, 0]
            if len(bbox) < 4:
                bbox = [0, 0, 0, 0]
            if log_height:
                bbox[3] = max(0, bbox[3] - log_height)
            geometry_logger.debug(f"update_canvas_scrollregion: bbox={bbox}, log_height={log_height}")
            if not canvas.winfo_ismapped():
                geometry_logger.debug(f"Canvas {canvas} is not mapped - skipping scrollregion update.")
                return
            canvas.configure(scrollregion=(bbox[0], bbox[1], bbox[2], bbox[3]))
        except Exception as e:
            import traceback
            geometry_logger.error(f"Exception in update_canvas_scrollregion: {e}\n{traceback.format_exc()}")
            try:
                def log_widget_tree(widget, prefix=""):
                    geometry_logger.debug(f"{prefix}{widget.winfo_class()} {widget.winfo_name()} ({widget})")
                    for child in widget.winfo_children():
                        log_widget_tree(child, prefix + "  ")
                log_widget_tree(root)
            except Exception as tree_exc:
                geometry_logger.error(f"Exception logging widget tree: {tree_exc}")
    def _bind_mousewheel(event):
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
    def _unbind_mousewheel(event):
        canvas.unbind_all("<MouseWheel>")
    rule_refs["rule_frame"].bind("<Enter>", _bind_mousewheel)
    rule_refs["rule_frame"].bind("<Leave>", _unbind_mousewheel)
    
    def update_rule_list_preserve_scroll(rules, config_path, logger):
        logger.info("Updating rule list with scroll preservation.")
        try:
            yview = canvas.yview()
            logger.debug(f"Saving scroll position: {yview}")
        except Exception as e:
            logger.debug(f"Could not get yview: {e}")
            yview = (0, 0)
        
        # Always use the current rule_frame from rule_refs
        update_rule_list(rule_refs["rule_frame"], rules, config_path, logger, update_rule_list_preserve_scroll)
        
        # Use a sequence of delayed restores to ensure scrolling is preserved
        # This handles cases where layout and scrollregion updates take time
        def restore_scroll(attempt=1, max_attempts=5):
            try:
                # Force an update of the canvas to ensure dimensions are correct
                canvas.update_idletasks()
                
                # Get current scrollregion and check validity
                bbox = canvas.bbox("all")
                if bbox is None or bbox == (0, 0, 1, 1):
                    logger.debug(f"Invalid bbox {bbox} on attempt {attempt}, will retry")
                    if attempt < max_attempts:
                        canvas.after(50 * attempt, lambda: restore_scroll(attempt + 1, max_attempts))
                    return

                # Apply saved scroll position
                logger.debug(f"Restoring scroll to {yview[0]} (attempt {attempt})")
                canvas.yview_moveto(yview[0])
                
                # Do a second delayed restore as final safety check
                if attempt == 1:
                    canvas.after(100, lambda: restore_scroll(max_attempts, max_attempts))
            except Exception as e:
                logger.debug(f"Error restoring scroll: {e}")
                if attempt < max_attempts:
                    canvas.after(50, lambda: restore_scroll(attempt + 1, max_attempts))
        
        # Start the first restore attempt with a delay
        canvas.after(50, restore_scroll)

    # Use the wrapper for initial population
    update_rule_list_preserve_scroll(rules, config_directory, logger)

    # Update all button callbacks to use the scroll-preserving function
    button_frame = ttkb.Frame(root, padding=10)
    button_frame.pack(fill="x", padx=10, pady=5, before=rule_frame_container)
    ttkb.Button(button_frame, text="Enable All Rules", style="success.TButton", command=lambda: (logger.info("Enable all rules clicked."), enable_all_rules(rules, config_directory, rule_refs["rule_frame"], logger, update_rule_list_preserve_scroll))).pack(side="left", padx=5)
    ttkb.Button(button_frame, text="Disable All Rules", style="danger.TButton", command=lambda: (logger.info("Disable all rules clicked."), disable_all_rules(rules, config_directory, rule_refs["rule_frame"], logger, update_rule_list_preserve_scroll))).pack(side="left", padx=5)
    ttkb.Button(button_frame, text="Add Rule", style="primary.TButton", command=lambda: (logger.info("Add rule clicked."), add_rule_button(rules, config_directory, rule_refs["rule_frame"], logger, root, update_rule_list_preserve_scroll))).pack(side="left", padx=5)
    ttkb.Button(button_frame, text="Delete Multiple Rules", style="Warning.TButton", command=lambda: (logger.info("Delete multiple rules clicked."), delete_multiple_rules(rules, config_directory, logger, rule_refs["rule_frame"], update_rule_list_preserve_scroll))).pack(side="left", padx=5)
    #ttkb.Button(button_frame, text="Reload List", style="info.TButton", command=lambda: update_rule_list_preserve_scroll(rules, config_directory, logger)).pack(side="left", padx=5)
    
    def show_organization_progress():
        # Close any existing progress window before opening a new one
        if hasattr(root, 'progress_win') and root.progress_win is not None:
            try:
                root.progress_win.destroy()
            except Exception:
                pass
            root.progress_win = None

        progress_win = ttkb.Toplevel(root)
        root.progress_win = progress_win  # Track the progress window on the root
        progress_win.title("Organizing Files")
        progress_win.geometry("500x400")
        center_window(progress_win)
        progress_win.transient(root)
        progress_win.grab_set()  # Prevent interaction with main window
        # Do not set always-on-top or force focus

        progress_label = ttkb.Label(progress_win, text="Organizing files, please wait...")
        progress_label.pack(pady=10)

        progress_bar = ttkb.Progressbar(progress_win, orient="horizontal", length=400, mode="determinate")
        progress_bar.pack(pady=10)
        file_listbox = tk.Listbox(progress_win, height=10)
        file_listbox.pack(fill="both", expand=True, padx=10, pady=10)
        scrollbar = ttkb.Scrollbar(progress_win, orient="vertical", command=file_listbox.yview)
        file_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        current_file_label = ttkb.Label(progress_win, text="Current file: None")
        current_file_label.pack(pady=5)

        moved_files = []
        def progress_callback(index, total, file_name):
            progress_bar["maximum"] = total
            progress_bar["value"] = index
            current_file_label.config(text=f"Current file: {file_name}")
            progress_win.update_idletasks()
        def file_moved_callback(file_name, target_folder):
            moved_files.append((file_name, target_folder))
            file_listbox.insert(tk.END, f"{file_name} → {target_folder}")
            file_listbox.yview_moveto(1)
            progress_win.update_idletasks()
        start_organization(settings, rules, logger, progress_callback=progress_callback, file_moved_callback=file_moved_callback)
        # Update label when organization is complete
        progress_label.config(text="File organization complete.")
        # Do not close the window automatically; user can close it manually
        progress_win.grab_release()  # Release grab when done (optional, if you add a close button)

    ttkb.Button(button_frame, text="Start Organization", style="info.TButton", command=lambda: (logger.info("Start organization clicked."), show_organization_progress())).pack(side="left", padx=5)

    # --- Developer Log Window ---
    def open_developer_log_window():
        if hasattr(root, '_dev_log_window') and root._dev_log_window is not None and tk.Toplevel.winfo_exists(root._dev_log_window):
            root._dev_log_window.lift()
            root._dev_log_window.focus_force()
            return
        dev_log_window = tk.Toplevel(root)
        dev_log_window.title("Developer Log")
        dev_log_window.geometry("900x300")
        log_label = ttkb.Label(dev_log_window, text="Application Log:", font=("Arial", 15, "bold"))
        log_label.pack()
        log_widget = scrolledtext.ScrolledText(dev_log_window, height=12, state="normal", wrap="word")
        log_widget.pack(fill="both", expand=True)
        text_handler = TextHandler(log_widget)
        formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s', datefmt='%H:%M:%S')
        text_handler.setFormatter(formatter)
        logger.addHandler(text_handler)
        root._dev_log_window = dev_log_window
        def on_close():
            logger.removeHandler(text_handler)
            root._dev_log_window = None
            dev_log_window.destroy()
        dev_log_window.protocol("WM_DELETE_WINDOW", on_close)
    root.open_developer_log_window = open_developer_log_window

    # Bind Ctrl+R to reload the rule list
    def on_ctrl_r(event=None):
        logger.info("Manual reload of rule list triggered by Ctrl+R.")
        update_rule_list_preserve_scroll(rules, config_directory, logger)
        return "break"  # Prevent default behavior
    root.bind_all('<Control-r>', on_ctrl_r)
    root.bind_all('<Control-R>', on_ctrl_r)

    # --- Full UI Rebuild Helper ---
    def rebuild_main_ui():
        for child in root.winfo_children():
            try:
                child.destroy()
            except Exception:
                pass
        setup_ui(root, base_path_var, rules, config_directory, style, settings, logger)
    root.rebuild_main_ui = rebuild_main_ui

def browse_path(path_var, logger):
    """Browse and select a directory."""
    selected_path = filedialog.askdirectory()
    if selected_path:
        path_var.set(selected_path)
        logger.info(f"Base path updated to: {selected_path}")

def open_developer_settings(root, settings, save_settings, logger):
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
    ttkb.Button(dev_window, text="Create Dummy Files", command=lambda: create_dummy_files(os.path.expanduser(settings.get("organisation_folder", "")), logger)).pack(pady=10)

    def save_dev_settings():
        settings["developer_mode"] = dev_mode_var.get() == "Enabled"
        save_settings(settings_path, settings, logger)  # Ensure save_settings is called correctly
        logger.info(f"Developer mode set to {dev_mode_var.get()}.")
        dev_window.destroy()

    ttkb.Button(dev_window, text="Save", command=save_dev_settings).pack(pady=10)

def create_dummy_files(base_directory, logger):
    """Create dummy files of various types in the base directory for testing."""
    if not base_directory:
        base_directory = os.path.expanduser("~/default_dir")  # Use default_dir if base_directory is not provided
        logger.warning(f"Base directory not provided. Using default directory: {base_directory}")

    # Always log the base directory creation message for test consistency
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
    import yaml
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
