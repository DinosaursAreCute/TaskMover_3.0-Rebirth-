import os
import shutil
import fnmatch
import logging
import colorlog
import zipfile
import tkinter as tk
from tkinter import messagebox, filedialog, Menu
import yaml
import ttkbootstrap as ttkb
from ttkbootstrap.constants import *
import sys
import subprocess

# Ensure required modules are installed
required_modules = ['colorlog', 'ttkbootstrap', 'pyyaml']
for module in required_modules:
    try:
        __import__(module)
    except ImportError:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', module])

# Configure logging with colorlog
handler = colorlog.StreamHandler()
handler.setFormatter(colorlog.ColoredFormatter(
    '%(log_color)s%(asctime)s - %(levelname)s - %(message)s',
    log_colors={
        'DEBUG': 'cyan',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'bold_red',
    }
))
logger = colorlog.getLogger()
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

def load_rules(config_path, fallback_path):
    logger.info(f"Loading rules from '{config_path}'")
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as file:
                rules = yaml.safe_load(file)
                logger.debug(f"Loaded rules: {rules}")
                shutil.copy(config_path, fallback_path)
                return rules
        except (yaml.YAMLError, IOError) as e:
            logger.error(f"Failed to load config file '{config_path}': {e}")
            if os.path.exists(fallback_path):
                logger.warning(f"Using fallback configuration from '{fallback_path}'")
                with open(fallback_path, 'r') as file:
                    rules = yaml.safe_load(file)
                    return rules
            else:
                logger.error("No valid configuration available. Using default rules.")
                messagebox.showwarning("Warning", "Configuration is invalid. Using default rules.")
                return create_default_rules(config_path)
    else:
        logger.warning(f"Config file '{config_path}' does not exist. Creating default rules.")
        return create_default_rules(config_path)

def create_default_rules(config_path):
    default_dir = os.path.expanduser("~/default_dir")
    default_rules = {
        "Pictures": {"patterns": ["*.jpg", "*.jpeg", "*.png", "*.gif"], "path": os.path.join(default_dir, "Pictures"), "unzip": False, "active": True},
        "Documents": {"patterns": ["*.pdf", "*.docx", "*.txt"], "path": os.path.join(default_dir, "Documents"), "unzip": False, "active": True},
        "Videos": {"patterns": ["*.mp4", "*.mkv", "*.avi"], "path": os.path.join(default_dir, "Videos"), "unzip": False, "active": True},
        "Archives": {"patterns": ["*.zip", "*.rar"], "path": os.path.join(default_dir, "Archives"), "unzip": True, "active": True},
    }
    os.makedirs(default_dir, exist_ok=True)
    save_rules(config_path, default_rules)
    return default_rules

def save_rules(config_path, rules):
    logger.info(f"Saving rules to '{config_path}'")
    with open(config_path, 'w') as file:
        yaml.dump(rules, file, default_flow_style=False)
        logger.debug(f"Saved rules: {rules}")

def organize_files(base_directory, rules):
    logger.info(f"Organizing files in directory: {base_directory}")

    if not os.path.exists(base_directory):
        logger.error(f"Directory '{base_directory}' does not exist.")
        return

    files = [item for item in os.listdir(base_directory) if os.path.isfile(os.path.join(base_directory, item))]
    total_files = len(files)

    progress_window = tk.Toplevel(root)
    progress_window.title("Organizing Files")
    progress_window.geometry("400x150")
    center_window(progress_window)

    progress_label = ttkb.Label(progress_window, text="Organizing files...", font=("Helvetica", 10, "bold"))
    progress_label.pack(pady=10)

    progress_bar = ttkb.Progressbar(progress_window, orient='horizontal', length=300, mode='determinate', maximum=total_files)
    progress_bar.pack(pady=10)

    for index, item in enumerate(files, start=1):
        item_path = os.path.join(base_directory, item)
        progress_label.config(text=f"Processing: {item}")
        move_file(item_path, base_directory, rules)
        progress_bar['value'] = index  # Update progress bar with each file
        progress_window.update_idletasks()

    progress_label.config(text="Organization Complete")
    ttkb.Button(progress_window, text="Close", command=progress_window.destroy).pack(pady=10)

def move_file(file_path, base_directory, rules):
    file_name = os.path.basename(file_path)
    file_extension = os.path.splitext(file_name)[1].lower()

    for folder, rule in rules.items():
        if not rule.get('active', True):
            continue

        patterns = rule['patterns']
        target_folder = rule['path'] if rule['path'] else os.path.join(base_directory, folder)
        unzip = rule['unzip']

        if file_extension in patterns or any(fnmatch.fnmatch(file_name, pattern) for pattern in patterns):
            os.makedirs(target_folder, exist_ok=True)
            shutil.move(file_path, os.path.join(target_folder, file_name))
            logger.info(f"Moved file '{file_name}' to '{target_folder}'")

            if unzip and file_extension == '.zip':
                unzip_file(os.path.join(target_folder, file_name), target_folder)

            break
    else:
        logger.warning(f"No matching rule found for file '{file_name}'")

def unzip_file(zip_path, extract_to):
    try:
        zip_name = os.path.splitext(os.path.basename(zip_path))[0]
        target_dir = os.path.join(extract_to, zip_name)
        os.makedirs(target_dir, exist_ok=True)

        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(target_dir)
            logger.info(f"Unzipped '{zip_path}' to '{target_dir}'")
    except zipfile.BadZipFile:
        logger.error(f"Failed to unzip '{zip_path}': Bad zip file")

def browse_path(path_var):
    logger.info("Opening directory selection dialog.")
    selected_path = filedialog.askdirectory()
    if selected_path:
        path_var.set(selected_path)
        logger.info(f"Path selected: {selected_path}")
    else:
        logger.warning("No path selected.")

def save_rule_immediate(rule_key, rule, listbox, path_widget, unzip_var, active_var, config_path):
    logger.info(f"Saving rule '{rule_key}' immediately.")
    patterns = list(listbox.get(0, tk.END))
    path = path_widget.get()
    unzip = unzip_var.get()
    active = active_var.get()
    rules[rule_key] = {"patterns": patterns, "path": path, "unzip": unzip, "active": active}
    logger.debug(f"Updated rule: {rules[rule_key]}")
    save_rules(config_path, rules)

def cancel_rule_changes():
    logger.info("Cancelling rule changes and reverting to the last saved state.")
    update_rule_list()

def add_pattern(listbox, entry_widget):
    pattern = entry_widget.get()
    if pattern:
        listbox.insert(tk.END, pattern)
        entry_widget.delete(0, tk.END)
        logger.info(f"Added pattern: {pattern}")
    else:
        logger.warning("Attempted to add an empty pattern.")

def remove_selected_pattern(listbox):
    selected_indices = listbox.curselection()
    if selected_indices:
        for index in reversed(selected_indices):
            removed_pattern = listbox.get(index)
            listbox.delete(index)
            logger.info(f"Removed pattern: {removed_pattern}")
    else:
        logger.warning("No pattern selected for removal.")

def enable_all_rules():
    logger.info("Enabling all rules.")
    for rule in rules.values():
        rule['active'] = True
    save_rules(config_path, rules)
    update_rule_list()

def disable_all_rules():
    logger.info("Disabling all rules.")
    for rule in rules.values():
        rule['active'] = False
    save_rules(config_path, rules)
    update_rule_list()

def update_rule_list():
    for widget in rule_frame.winfo_children():
        widget.destroy()

    for rule_key, rule in rules.items():
        frame = ttkb.Frame(rule_frame, padding=10, bootstyle="secondary")
        frame.pack(fill="x", pady=5, padx=5)

        # Title
        rule_label = ttkb.Label(frame, text=f"{rule_key}", font=("Helvetica", 10, "bold"))
        rule_label.pack(anchor="w", pady=2)

        # Columns Frame
        columns_frame = ttkb.Frame(frame)
        columns_frame.pack(fill="x", pady=5)

        # Left Column (Buttons)
        left_column = ttkb.Frame(columns_frame)
        left_column.pack(side="left", fill="y", padx=5)

        # Center Column (Inputs)
        center_column = ttkb.Frame(columns_frame)
        center_column.pack(side="left", fill="both", expand=True, padx=5)

        pattern_listbox = tk.Listbox(center_column, selectmode=tk.MULTIPLE, width=50, height=5, highlightthickness=1)
        pattern_listbox.pack(pady=2)

        for pattern in rule['patterns']:
            pattern_listbox.insert(tk.END, pattern)

        pattern_entry = ttkb.Entry(center_column, width=40)
        pattern_entry.pack(pady=2)

        path_var = tk.StringVar(value=rule['path'])
        path_widget = ttkb.Entry(center_column, textvariable=path_var, width=50)
        path_widget.pack(pady=2)

        # Right Column (Toggles)
        right_column = ttkb.Frame(columns_frame)
        right_column.pack(side="left", fill="y", padx=5)

        # Add buttons after defining pattern_listbox and pattern_entry
        add_button = ttkb.Button(left_column, text="Add Pattern", command=lambda lb=pattern_listbox, pe=pattern_entry: add_pattern(lb, pe))
        add_button.pack(pady=2)

        remove_button = ttkb.Button(left_column, text="Remove Selected", command=lambda lb=pattern_listbox: remove_selected_pattern(lb))
        remove_button.pack(pady=2)

        path_button = ttkb.Button(left_column, text="Browse", command=lambda pv=path_var: browse_path(pv))
        path_button.pack(pady=2)

        unzip_var = tk.BooleanVar(value=rule['unzip'])
        unzip_check = ttkb.Checkbutton(right_column, text="Unzip", variable=unzip_var, command=lambda: save_rule_immediate(rule_key, rule, pattern_listbox, path_widget, unzip_var, active_var, config_path))
        unzip_check.pack(pady=2)

        active_var = tk.BooleanVar(value=rule.get('active', True))
        active_check = ttkb.Checkbutton(right_column, text="Active", variable=active_var, command=lambda: save_rule_immediate(rule_key, rule, pattern_listbox, path_widget, unzip_var, active_var, config_path))
        active_check.pack(pady=2)

        save_button = ttkb.Button(right_column, text="Save", command=lambda rk=rule_key, r=rule, lb=pattern_listbox, pw=path_widget, uv=unzip_var, av=active_var: save_rule_immediate(rk, r, lb, pw, uv, av, config_path))
        save_button.pack(pady=2)

        cancel_button = ttkb.Button(right_column, text="Cancel", command=cancel_rule_changes)
        cancel_button.pack(pady=2)

def center_window(window):
    window.update_idletasks()
    width = window.winfo_width()
    height = window.winfo_height()
    x = (window.winfo_screenwidth() // 2) - (width // 2)
    y = (window.winfo_screenheight() // 2) - (height // 2)
    window.geometry(f'{width}x{height}+{x}+{y}')

def on_mouse_wheel(event):
    canvas.yview_scroll(-1 * int(event.delta / 120), "units")

def change_theme(theme_name):
    style.theme_use(theme_name)
    update_rule_list()

def choose_color(setting):
    color_code = filedialog.askcolor(title=f"Choose {setting} Color")[1]
    if color_code:
        if setting == "Accent":
            style.configure('TButton', foreground=color_code)
            style.configure('TLabel', foreground=color_code)
            style.configure('TCheckbutton', foreground=color_code)
        elif setting == "Background":
            root.configure(bg=color_code)
        elif setting == "Text":
            style.configure('TLabel', foreground=color_code)

def add_menubar(window):
    menubar = Menu(window)
    window.config(menu=menubar)

    file_menu = Menu(menubar, tearoff=0)
    file_menu.add_command(label='Organize Files', command=lambda: organize_files(base_directory, rules))
    file_menu.add_command(label='Exit', command=root.quit)
    menubar.add_cascade(label='File', menu=file_menu)

    theme_menu = Menu(menubar, tearoff=0)
    theme_menu.add_command(label='Default', command=lambda: change_theme('flatly'))
    theme_menu.add_command(label='Dark', command=lambda: change_theme('darkly'))
    menubar.add_cascade(label='Theme', menu=theme_menu)

    color_menu = Menu(menubar, tearoff=0)
    color_menu.add_command(label='Choose Accent Color', command=lambda: choose_color("Accent"))
    color_menu.add_command(label='Choose Background Color', command=lambda: choose_color("Background"))
    color_menu.add_command(label='Choose Text Color', command=lambda: choose_color("Text"))
    menubar.add_cascade(label='Colors', menu=color_menu)

def check_first_run(config_directory, base_directory_var):
    first_run_marker = os.path.join(config_directory, "first_run_marker.txt")
    if not os.path.exists(first_run_marker):
        logger.info("First run detected. Prompting user to select a base directory.")
        messagebox.showinfo("Welcome", "It seems this is your first time running the program. Please select a base directory.")
        selected_path = filedialog.askdirectory(title="Select Base Directory")
        if selected_path:
            base_directory_var.set(selected_path)
            os.makedirs(selected_path, exist_ok=True)
            logger.info(f"Base directory set to: {selected_path}")
            with open(first_run_marker, 'w') as marker_file:
                marker_file.write("This file marks that the program has been run before.")
            logger.debug("First run marker file created.")
        else:
            logger.warning("No base directory selected. Using default directory.")
            default_dir = os.path.expanduser("~/default_dir")
            base_directory_var.set(default_dir)
            os.makedirs(default_dir, exist_ok=True)
            with open(first_run_marker, 'w') as marker_file:
                marker_file.write("This file marks that the program has been run before.")
            logger.debug("First run marker file created with default directory.")

def main():
    global root, rules, base_directory, config_path, fallback_path, rule_frame, canvas, style
    logger.info("Starting the File Organizer application.")

    # Initialize Tkinter root before creating StringVar
    root = tk.Tk()
    root.withdraw()  # Hide the root window until fully configured

    base_directory_var = tk.StringVar(value=os.path.expanduser("~/default_dir"))
    base_directory = base_directory_var.get()
    config_directory = os.path.join(base_directory, "config")
    os.makedirs(config_directory, exist_ok=True)
    config_path = os.path.join(config_directory, "rules.yml")
    fallback_path = os.path.join(config_directory, "fallback_conf.yml")

    check_first_run(config_directory, base_directory_var)

    base_directory = base_directory_var.get()
    rules = load_rules(config_path, fallback_path)

    root.deiconify()  # Show the root window after configuration
    root.title("File Organizer")
    root.geometry("800x600")
    center_window(root)

    style = ttkb.Style()

    base_path_var = tk.StringVar(value=base_directory)
    
    # Base Path Frame
    base_path_frame = ttkb.Frame(root, padding=10)
    base_path_frame.pack(fill="x", pady=5, padx=5)

    ttkb.Label(base_path_frame, text="Base Path:", font=("Helvetica", 10, "bold")).pack(side="left", padx=5)
    base_path_entry = ttkb.Entry(base_path_frame, textvariable=base_path_var, width=40)
    base_path_entry.pack(side="left", padx=5)
    base_path_button = ttkb.Button(base_path_frame, text="Browse", command=lambda: browse_path(base_path_var))
    base_path_button.pack(side="left", padx=5)

    # Add Enable/Disable All Buttons
    button_frame = ttkb.Frame(root, padding=10)
    button_frame.pack(fill="x", pady=5)

    enable_all_button = ttkb.Button(button_frame, text="Enable All", command=enable_all_rules)
    enable_all_button.pack(side="left", padx=5)

    disable_all_button = ttkb.Button(button_frame, text="Disable All", command=disable_all_rules)
    disable_all_button.pack(side="left", padx=5)

    # Rule Frame
    canvas = tk.Canvas(root)
    scrollbar = ttkb.Scrollbar(root, orient="vertical", command=canvas.yview)
    rule_frame = ttkb.Frame(canvas)

    rule_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )

    canvas.create_window((0, 0), window=rule_frame, anchor="n", width=780)
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # Enable mouse wheel scrolling
    root.bind_all("<MouseWheel>", on_mouse_wheel)

    # Organize Files Button
    organize_button = ttkb.Button(root, text="Organize Files", command=lambda: organize_files(base_path_var.get(), rules))
    organize_button.pack(pady=20)

    update_rule_list()
    add_menubar(root)

    root.mainloop()

if __name__ == "__main__":
    main()
