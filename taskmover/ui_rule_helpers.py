"""
Rule management UI helpers for TaskMover.
"""

import tkinter as tk
from .ui_helpers import Tooltip
import ttkbootstrap as ttkb
from tkinter import messagebox, filedialog, simpledialog
from taskmover.config import save_rules
from taskmover.pattern_grid_helpers import pattern_grid_label, pattern_grid_edit

def update_rule_list(rule_frame, rules, config_path, logger, update_rule_list_fn=None, scrollable_widget=None):
    # Maintain a mapping of rule_key to frame
    if not hasattr(rule_frame, '_rule_frames'):
        rule_frame._rule_frames = {}
    rule_frames = rule_frame._rule_frames
    # Remove frames for deleted rules
    for key in list(rule_frames.keys()):
        if key not in rules:
            rule_frames[key].destroy()
            del rule_frames[key]
    # Add or update frames for all rules
    for rule_key in rules:
        update_or_create_rule_frame(rule_key, rules, config_path, logger, rule_frame, rule_frames, update_rule_list_fn, scrollable_widget)

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

def enable_all_rules(rules, config_path, rule_frame, logger, update_rule_list_fn=None):
    import logging
    rule_frames = getattr(rule_frame, '_rule_frames', {})
    for rule_key, rule in rules.items():
        rule['active'] = True
        var = rule_frames.get(rule_key+'_active_var')
        if var:
            var.set(1)
        logging.getLogger("UI").info(f"User enabled rule '{rule_key}'.")
        logging.getLogger("Rules").info(f"Rule '{rule_key}' enabled.")
    save_rules(config_path, rules)
    # No UI rebuild needed

def disable_all_rules(rules, config_path, rule_frame, logger, update_rule_list_fn=None):
    import logging
    rule_frames = getattr(rule_frame, '_rule_frames', {})
    for rule_key, rule in rules.items():
        rule['active'] = False
        var = rule_frames.get(rule_key+'_active_var')
        if var:
            var.set(0)
        logging.getLogger("UI").info(f"User disabled rule '{rule_key}'.")
        logging.getLogger("Rules").info(f"Rule '{rule_key}' disabled.")
    save_rules(config_path, rules)
    # No UI rebuild needed

def add_rule_button(rules, config_path, rule_frame, logger, root, update_rule_list_fn=None):
    rule_name = simpledialog.askstring("Add Rule", "Enter the name of the new rule:", parent=root)
    if rule_name:
        if rule_name in rules:
            messagebox.showerror("Error", f"Rule '{rule_name}' already exists.", parent=root)
            logger.warning(f"Attempted to add duplicate rule: {rule_name}")
        else:
            rules[rule_name] = {"patterns": [], "path": "", "unzip": False, "active": True}
            save_rules(config_path, rules)
            if update_rule_list_fn:
                update_rule_list_fn(rules, config_path, logger)
            else:
                update_rule_list(rule_frame, rules, config_path, logger)
            logger.info(f"Added new rule: {rule_name}")
            edit_rule(rule_name, rules, config_path, logger, rule_frame)

def delete_rule(rule_key, rules, config_path, logger, rule_frame, update_rule_list_fn=None):
    if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete the rule '{rule_key}'?"):
        del rules[rule_key]
        save_rules(config_path, rules)
        logger.info(f"Rule '{rule_key}' deleted.")
        if update_rule_list_fn:
            update_rule_list_fn(rules, config_path, logger)
        else:
            update_rule_list(rule_frame, rules, config_path, logger)

def delete_multiple_rules(rules, config_path, logger, rule_frame, update_rule_list_fn=None):
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
            if update_rule_list_fn:
                update_rule_list_fn(rules, config_path, logger)
            else:
                update_rule_list(rule_frame, rules, config_path, logger)
            delete_window.destroy()
    ttkb.Button(delete_window, text="Delete Selected", command=confirm_delete).pack(pady=10)
    ttkb.Button(delete_window, text="Cancel", command=delete_window.destroy).pack(pady=5)

def edit_rule(rule_key, rules, config_path, logger, rule_frame):
    import taskmover.center_window as cw
    edit_window = tk.Toplevel()
    edit_window.title(f"Edit Rule: {rule_key}")
    edit_window.geometry("400x300")
    root = rule_frame.winfo_toplevel()
    cw.center_window(edit_window)
    edit_window.attributes('-topmost', True)
    edit_window.update()
    edit_window.attributes('-topmost', False)
    edit_window.grab_set()
    # --- Editable rule name ---
    def on_rename(new_name):
        edit_window.title(f"Edit Rule: {new_name}")
        # Update the rest of the UI if needed
    name_frame, name_var = editable_rule_name(edit_window, rule_key, rules, config_path, logger, on_rename, font=("Helvetica", 12, "bold"))
    name_frame.pack(pady=10)
    ttkb.Label(edit_window, text="Directory:").pack(anchor="w", padx=10)
    dir_var = tk.StringVar(value=rules[name_var.get()]['path'])
    dir_entry = ttkb.Entry(edit_window, textvariable=dir_var, width=50)
    dir_entry.pack(pady=5, padx=10)
    dir_entry.bind("<Button-1>", lambda e: dir_var.set(filedialog.askdirectory(title="Select Directory")))
    ttkb.Label(edit_window, text="Patterns (comma-separated):").pack(anchor="w", padx=10)
    patterns_var = tk.StringVar(value=", ".join(rules[name_var.get()]['patterns']))
    patterns_entry = ttkb.Entry(edit_window, textvariable=patterns_var, width=50)
    patterns_entry.pack(pady=5, padx=10)
    def save_changes():
        current_key = name_var.get()
        rules[current_key]['path'] = dir_var.get()
        rules[current_key]['patterns'] = [pattern.strip() for pattern in patterns_var.get().split(",")]
        save_rules(config_path, rules)
        logger.info(f"Rule '{current_key}' updated.")
        update_rule_list(rule_frame, rules, config_path, logger)
        edit_window.destroy()
    ttkb.Button(edit_window, text="Save", command=save_changes).pack(pady=10)
    ttkb.Button(edit_window, text="Cancel", command=edit_window.destroy).pack(pady=5)

def update_or_create_rule_frame(rule_key, rules, config_path, logger, rule_frame, rule_frames, update_rule_list_fn=None, scrollable_widget=None):
    # Remove old frame if it exists (for rename or delete)
    if rule_key in rule_frames:
        rule_frames[rule_key].destroy()
    frame = ttkb.Frame(rule_frame)
    frame.pack(fill="x", pady=5, padx=10)
    rule_frames[rule_key] = frame
    # --- Editable rule name ---
    def on_rename(new_name):
        # Remove old frame and create new one for renamed rule
        frame.destroy()
        rule_frames.pop(rule_key, None)
        update_or_create_rule_frame(new_name, rules, config_path, logger, rule_frame, rule_frames, update_rule_list_fn, scrollable_widget)
    name_frame, _ = editable_rule_name(frame, rule_key, rules, config_path, logger, on_rename)
    name_frame.pack(anchor="w", pady=5)
    # --- Patterns ---
    patterns_frame = ttkb.Frame(frame)
    patterns_frame.pack(anchor="w", padx=10, pady=2, fill="x")
    patterns_label = ttkb.Label(patterns_frame, text="Patterns:", font=("Helvetica", 10))
    patterns_label.pack(anchor="w")
    Tooltip(patterns_label, "File name patterns (e.g., *.pdf, report_*.docx) that this rule will match.")
    patterns_grid = ttkb.Frame(patterns_frame)
    patterns_grid.pack(anchor="w", fill="x")
    def make_show_pattern_label(rk, pg):
        def show_pattern_label():
            pattern_grid_label(pg, rules, rk, make_show_pattern_edit(rk, pg), scrollable_widget)
        return show_pattern_label
    def make_show_pattern_edit(rk, pg):
        def show_pattern_edit():
            pattern_grid_edit(pg, rules, rk, config_path, logger, make_show_pattern_label(rk, pg), scrollable_widget)
        return show_pattern_edit
    make_show_pattern_label(rule_key, patterns_grid)()
    # --- Path field ---
    path_var = tk.StringVar(value=rules[rule_key]['path'])
    def choose_path(event=None, rk=rule_key, pv=path_var):
        selected = filedialog.askdirectory(title="Select Directory", initialdir=pv.get())
        if selected:
            pv.set(selected)
            rules[rk]['path'] = selected
            save_rules(config_path, rules)
            logger.info(f"Path for rule '{rk}' updated: {selected}")
            update_or_create_rule_frame(rk, rules, config_path, logger, rule_frame, rule_frames, update_rule_list_fn, scrollable_widget)
    path_entry = ttkb.Entry(frame, textvariable=path_var, font=("Helvetica", 10), width=40)
    path_entry.pack(anchor="w", padx=10)
    path_entry.bind("<Button-1>", lambda event, rk=rule_key, pv=path_var: choose_path(event, rk, pv))
    path_entry.bind("<Return>", lambda event, rk=rule_key, pv=path_var: choose_path(event, rk, pv))
    path_entry.config(state="readonly", cursor="hand2")
    Tooltip(path_entry, "Click to select the folder where files matching this rule will be moved.")
    # --- Details switches ---
    details_frame = ttkb.Frame(frame)
    details_frame.pack(fill="x", pady=5)
    active_var = tk.IntVar(value=1 if rules[rule_key]['active'] else 0)
    rule_frames[rule_key+'_active_var'] = active_var  # Store for fast access
    active_switch = ttkb.Checkbutton(
        details_frame,
        text="Active",
        variable=active_var,
        command=lambda rk=rule_key, av=active_var: toggle_rule_active(rk, rules, config_path, av.get(), logger)
    )
    active_switch.pack(side="left", padx=10)
    Tooltip(active_switch, "Enable or disable this rule.")
    unzip_var = tk.IntVar(value=1 if rules[rule_key].get('unzip', False) else 0)
    unzip_switch = ttkb.Checkbutton(
        details_frame,
        text="Unzip",
        variable=unzip_var,
        command=lambda rk=rule_key, uv=unzip_var: toggle_unzip(rk, rules, config_path, uv.get(), logger)
    )
    unzip_switch.pack(side="left", padx=10)
    Tooltip(unzip_switch, "Automatically unzip .zip files matching this rule.")
    # --- Action buttons ---
    actions_frame = ttkb.Frame(frame)
    actions_frame.pack(fill="x", pady=5)
    edit_button = ttkb.Button(actions_frame, text="Edit", style="info.TButton", command=lambda rk=rule_key: edit_rule(rk, rules, config_path, logger, rule_frame))
    edit_button.pack(side="left", padx=10)
    Tooltip(edit_button, "Edit this rule.")
    delete_button = ttkb.Button(actions_frame, text="Delete", style="danger.TButton", command=lambda rk=rule_key: delete_rule(rk, rules, config_path, logger, rule_frame))
    delete_button.pack(side="left", padx=10)
    Tooltip(delete_button, "Delete this rule.")

def editable_rule_name(parent, rule_key, rules, config_path, logger, on_rename, font=("Helvetica", 12, "bold")):
    frame = ttkb.Frame(parent)
    name_var = tk.StringVar(value=rule_key)
    label = ttkb.Label(frame, textvariable=name_var, font=font, cursor="xterm")
    entry = ttkb.Entry(frame, textvariable=name_var, font=font, width=24)
    check_btn = ttkb.Button(frame, text="✔", width=2, style="success.TButton")
    cancel_flag = {'cancel': False}
    current_key = [rule_key]  # mutable container for current rule key
    def show_entry(event=None):
        label.pack_forget()
        entry.pack(side="left", fill="x", expand=True)
        check_btn.pack(side="left")
        entry.focus_set()
        entry.icursor(tk.END)
    def save_name(event=None):
        new_name = name_var.get().strip()
        if not new_name or new_name == current_key[0]:
            cancel_edit()
            return
        if new_name in rules:
            messagebox.showerror("Name Exists", f"A rule named '{new_name}' already exists.")
            return
        rules[new_name] = rules.pop(current_key[0])
        save_rules(config_path, rules)
        logger.info(f"Rule renamed from '{current_key[0]}' to '{new_name}'")
        current_key[0] = new_name
        name_var.set(new_name)
        entry.pack_forget()
        check_btn.pack_forget()
        label.pack(side="left")
        on_rename(new_name)
    def cancel_edit(event=None):
        if cancel_flag['cancel']:
            return
        name_var.set(current_key[0])
        entry.pack_forget()
        check_btn.pack_forget()
        label.pack(side="left")
    def check_and_save():
        cancel_flag['cancel'] = True
        save_name()
        cancel_flag['cancel'] = False
    label.bind("<Button-1>", show_entry)
    entry.bind("<Return>", save_name)
    entry.bind("<Escape>", cancel_edit)
    entry.bind("<FocusOut>", cancel_edit)
    check_btn.config(command=check_and_save)
    label.pack(side="left")
    return frame, name_var
