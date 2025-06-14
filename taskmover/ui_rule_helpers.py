"""
Rule management UI helpers for TaskMover.
"""

import tkinter as tk
import ttkbootstrap as ttkb
from tkinter import messagebox, filedialog, simpledialog
from taskmover.config import save_rules
from taskmover.pattern_grid_helpers import pattern_grid_label, pattern_grid_edit

def update_rule_list(rule_frame, rules, config_path, logger):
    """
    Populate the main rule list UI in the provided frame. Handles dynamic pattern editing,
    including inline editing, dynamic add fields, and a plus (+) button for adding multiple patterns.
    Only the last add pattern field shows a plus button, and focus moves to new fields automatically.
    Args:
        rule_frame: The parent frame for all rule UI elements (should be inside a scrollable canvas).
        rules: The rules dictionary.
        config_path: Path to the config file.
        logger: Logger instance for logging events.
    """
    for widget in rule_frame.winfo_children():
        widget.destroy()
    for rule_key, rule in rules.items():
        frame = ttkb.Frame(rule_frame)
        frame.pack(fill="x", pady=5, padx=10)
        ttkb.Label(frame, text=f"{rule_key}", font=("Helvetica", 12, "bold")).pack(anchor="w", pady=5)

        # --- Patterns: label by default, editable on click, dynamic grid layout ---
        patterns_frame = ttkb.Frame(frame)
        patterns_frame.pack(anchor="w", padx=10, pady=2, fill="x")
        ttkb.Label(patterns_frame, text="Patterns:", font=("Helvetica", 10)).pack(anchor="w")
        patterns_grid = ttkb.Frame(patterns_frame)
        patterns_grid.pack(anchor="w", fill="x")
        # Fix: pass patterns_grid as argument to closure to bind the correct instance
        def make_show_pattern_label(rk, pg):
            def show_pattern_label():
                pattern_grid_label(pg, rules, rk, make_show_pattern_edit(rk, pg))
            return show_pattern_label
        def make_show_pattern_edit(rk, pg):
            def show_pattern_edit():
                pattern_grid_edit(pg, rules, rk, config_path, logger, make_show_pattern_label(rk, pg))
            return show_pattern_edit
        make_show_pattern_label(rule_key, patterns_grid)()  # Call the label function for this rule and grid

        # --- Path field clickable, fixed for closure ---
        path_var = tk.StringVar(value=rule['path'])
        def choose_path(event=None, rk=rule_key, pv=path_var):
            selected = filedialog.askdirectory(title="Select Directory", initialdir=pv.get())
            if selected:
                pv.set(selected)
                rules[rk]['path'] = selected
                save_rules(config_path, rules)
                logger.info(f"Path for rule '{rk}' updated: {selected}")
                update_rule_list(rule_frame, rules, config_path, logger)
        path_entry = ttkb.Entry(frame, textvariable=path_var, font=("Helvetica", 10), width=40)
        path_entry.pack(anchor="w", padx=10)
        path_entry.bind("<Button-1>", lambda event, rk=rule_key, pv=path_var: choose_path(event, rk, pv))
        path_entry.bind("<Return>", lambda event, rk=rule_key, pv=path_var: choose_path(event, rk, pv))
        path_entry.config(state="readonly", cursor="hand2")

        # --- Rule details switches ---
        details_frame = ttkb.Frame(frame)
        details_frame.pack(fill="x", pady=5)
        active_var = tk.IntVar(value=1 if rule['active'] else 0)
        active_switch = ttkb.Checkbutton(
            details_frame,
            text="Active",
            variable=active_var,
            command=lambda rk=rule_key, av=active_var: toggle_rule_active(rk, rules, config_path, av.get(), logger)
        )
        active_switch.pack(side="left", padx=10)
        unzip_var = tk.IntVar(value=1 if rule.get('unzip', False) else 0)
        unzip_switch = ttkb.Checkbutton(
            details_frame,
            text="Unzip",
            variable=unzip_var,
            command=lambda rk=rule_key, uv=unzip_var: toggle_unzip(rk, rules, config_path, uv.get(), logger)
        )
        unzip_switch.pack(side="left", padx=10)

        # --- Action buttons ---
        actions_frame = ttkb.Frame(frame)
        actions_frame.pack(fill="x", pady=5)
        edit_button = ttkb.Button(actions_frame, text="Edit", style="info.TButton", command=lambda rk=rule_key: edit_rule(rk, rules, config_path, logger, rule_frame))
        edit_button.pack(side="left", padx=10)
        delete_button = ttkb.Button(actions_frame, text="Delete", style="danger.TButton", command=lambda rk=rule_key: delete_rule(rk, rules, config_path, logger, rule_frame))
        delete_button.pack(side="left", padx=10)

def open_file_dialog(initial_dir):
    from pathlib import Path
    import os
    dir_path = filedialog.askdirectory(initialdir=initial_dir, title="Select Directory")
    if dir_path:
        dir_path = Path(dir_path)
        if os.name == 'nt':  # Windows
            dir_path = str(dir_path).replace("/", "\\")
        else:  # macOS and Linux
            dir_path = str(dir_path)
        return dir_path
    return initial_dir

def toggle_rule_active(rule_key, rules, config_path, active, logger):
    import logging
    rules[rule_key]['active'] = bool(active)
    save_rules(config_path, rules)
    logging.getLogger("UI").info(f"User toggled rule '{rule_key}' to {'enabled' if active else 'disabled'}.")
    logging.getLogger("Rules").info(f"Rule '{rule_key}' active state set to {bool(active)}.")

def toggle_unzip(rule_key, rules, config_path, unzip, logger):
    import logging
    rules[rule_key]['unzip'] = bool(unzip)
    save_rules(config_path, rules)
    logging.getLogger("UI").info(f"User toggled unzip for rule '{rule_key}' to {bool(unzip)}.")
    logging.getLogger("Rules").info(f"Rule '{rule_key}' unzip state set to {bool(unzip)}.")

def enable_all_rules(rules, config_path, rule_frame, logger):
    import logging
    for rule_key, rule in rules.items():
        rule['active'] = True
        logging.getLogger("UI").info(f"User enabled rule '{rule_key}'.")
        logging.getLogger("Rules").info(f"Rule '{rule_key}' enabled.")
    save_rules(config_path, rules)
    update_rule_list(rule_frame, rules, config_path, logger)

def disable_all_rules(rules, config_path, rule_frame, logger):
    import logging
    for rule_key, rule in rules.items():
        rule['active'] = False
        logging.getLogger("UI").info(f"User disabled rule '{rule_key}'.")
        logging.getLogger("Rules").info(f"Rule '{rule_key}' disabled.")
    save_rules(config_path, rules)
    update_rule_list(rule_frame, rules, config_path, logger)

def add_rule_button(rules, config_path, rule_frame, logger, root):
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
            edit_rule(rule_name, rules, config_path, logger, rule_frame)

def delete_rule(rule_key, rules, config_path, logger, rule_frame):
    if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete the rule '{rule_key}'?"):
        del rules[rule_key]
        save_rules(config_path, rules)
        logger.info(f"Rule '{rule_key}' deleted.")
        update_rule_list(rule_frame, rules, config_path, logger)

def delete_multiple_rules(rules, config_path, logger, rule_frame):
    import taskmover.center_window as cw
    delete_window = tk.Toplevel()
    delete_window.title("Delete Rules")
    delete_window.geometry("600x600")
    cw.center_window(delete_window)
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
    import taskmover.center_window as cw
    edit_window = tk.Toplevel()
    edit_window.title(f"Edit Rule: {rule_key}")
    edit_window.geometry("400x300")
    # Center on the same display as the main window (rule_frame is a child of rule_frame.winfo_toplevel())
    root = rule_frame.winfo_toplevel()
    cw.center_window(edit_window)
    edit_window.attributes('-topmost', True)
    edit_window.update()  # Ensure the window is drawn
    edit_window.attributes('-topmost', False)
    edit_window.grab_set()
    ttkb.Label(edit_window, text=f"Edit Rule: {rule_key}", font=("Helvetica", 12, "bold")).pack(pady=10)
    ttkb.Label(edit_window, text="Directory:").pack(anchor="w", padx=10)
    dir_var = tk.StringVar(value=rules[rule_key]['path'])
    dir_entry = ttkb.Entry(edit_window, textvariable=dir_var, width=50)
    dir_entry.pack(pady=5, padx=10)
    dir_entry.bind("<Button-1>", lambda e: dir_var.set(filedialog.askdirectory(title="Select Directory")))
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
