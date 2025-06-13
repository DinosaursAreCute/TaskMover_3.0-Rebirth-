"""
Rule management UI helpers for TaskMover.
"""

import tkinter as tk
import ttkbootstrap as ttkb
from tkinter import messagebox, filedialog, simpledialog
from taskmover.config import save_rules

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
        def show_pattern_label(rule_key=rule_key, patterns_frame=patterns_frame, patterns_grid=patterns_grid):
            def layout_patterns(event=None):
                for w in patterns_grid.winfo_children():
                    w.destroy()
                pattern_strs = rules[rule_key]['patterns']
                width = patterns_grid.winfo_width()
                if width <= 1:
                    patterns_grid.after(10, layout_patterns)
                    return
                pattern_pixel_width = 120
                max_per_row = max(1, width // pattern_pixel_width)
                for idx, pattern in enumerate(pattern_strs):
                    row = idx // max_per_row
                    col = idx % max_per_row
                    label = ttkb.Label(patterns_grid, text=pattern, font=("Helvetica", 10), style="light.TLabel", cursor="hand2")
                    label.grid(row=row, column=col, padx=2, pady=2, sticky="w")
                    label.bind("<Button-1>", lambda event, rk=rule_key, pf=patterns_frame, pg=patterns_grid: show_pattern_edit(rk, pf, pg))
                if not pattern_strs:
                    label = ttkb.Label(patterns_grid, text="<no patterns>", font=("Helvetica", 10), style="light.TLabel", cursor="hand2")
                    label.grid(row=0, column=0, padx=2, pady=2, sticky="w")
                    label.bind("<Button-1>", lambda event, rk=rule_key, pf=patterns_frame, pg=patterns_grid: show_pattern_edit(rk, pf, pg))
            patterns_grid.bind("<Configure>", layout_patterns)
            layout_patterns()
        def show_pattern_edit(rule_key=rule_key, patterns_frame=patterns_frame, patterns_grid=patterns_grid):
            print(f"[DEBUG] show_pattern_edit called for rule: {rule_key}")
            patterns_grid.unbind("<Configure>")
            def layout_entries(event=None):
                for w in patterns_grid.winfo_children():
                    w.destroy()
                width = patterns_grid.winfo_width()
                if width <= 1:
                    patterns_grid.after(10, layout_entries)
                    return
                entry_pixel_width = 120
                max_per_row = max(1, width // entry_pixel_width)
                pattern_vars = []
                entries = []
                def save_patterns(event=None):
                    new_patterns = [v.get().strip() for v in pattern_vars if v.get().strip() and v.get().strip() != '<add pattern>']
                    new_patterns += [v.get().strip() for v in new_vars if v.get().strip() and v.get().strip() != '<add pattern>']
                    rules[rule_key]['patterns'] = new_patterns
                    save_rules(config_path, rules)
                    logger.info(f"Patterns for rule '{rule_key}' updated: {new_patterns}")
                    show_pattern_label(rule_key, patterns_frame, patterns_grid)
                def discard_patterns(event=None):
                    show_pattern_label(rule_key, patterns_frame, patterns_grid)
                # Existing patterns
                for idx, pattern in enumerate(rules[rule_key]['patterns']):
                    row = idx // max_per_row
                    col = idx % max_per_row
                    var = tk.StringVar(value=pattern)
                    entry = ttkb.Entry(patterns_grid, textvariable=var, width=15)
                    entry.grid(row=row, column=col, padx=2, pady=2, sticky="w")
                    entry.bind("<Return>", save_patterns)
                    entry.bind("<Escape>", discard_patterns)
                    pattern_vars.append(var)
                    entries.append(entry)
                # Dynamic add pattern entries with a plus button
                new_vars = []
                plus_buttons = []
                def add_new_pattern_entry():
                    idx = len(rules[rule_key]['patterns']) + len(new_vars)
                    row = idx // max_per_row
                    col = idx % max_per_row
                    new_var = tk.StringVar()
                    new_vars.append(new_var)
                    entry = ttkb.Entry(patterns_grid, textvariable=new_var, width=15)
                    entry.grid(row=row, column=col, padx=2, pady=2, sticky="w")
                    entry.insert(0, "<add pattern>")
                    def clear_placeholder(event, v=new_var):
                        if entry.get() == "<add pattern>":
                            entry.delete(0, tk.END)
                    entry.bind("<FocusIn>", clear_placeholder)
                    entry.bind("<Return>", save_patterns)
                    entry.bind("<Escape>", discard_patterns)
                    entries.append(entry)
                    # Remove previous plus button if it exists
                    if plus_buttons:
                        plus_buttons[-1].destroy()
                    # Add plus button next to the new entry
                    def add_and_focus():
                        add_new_pattern_entry()
                        # Focus the last entry (the new one)
                        entries[-1].focus_set()
                        entries[-1].icursor(tk.END)
                    plus_btn = ttkb.Button(patterns_grid, text="+", width=2, style="success.TButton", command=add_and_focus)
                    plus_btn.grid(row=row, column=col+1, padx=(0, 6), pady=2, sticky="w")
                    plus_buttons.append(plus_btn)
                add_new_pattern_entry()
                if entries:
                    entries[0].focus_set()
                def save_patterns(event=None):
                    new_patterns = [v.get().strip() for v in pattern_vars if v.get().strip() and v.get().strip() != '<add pattern>']
                    new_patterns += [v.get().strip() for v in new_vars if v.get().strip() and v.get().strip() != '<add pattern>']
                    rules[rule_key]['patterns'] = new_patterns
                    save_rules(config_path, rules)
                    logger.info(f"Patterns for rule '{rule_key}' updated: {new_patterns}")
                    show_pattern_label(rule_key, patterns_frame, patterns_grid)
                # Only one definition for discard_patterns
                def discard_patterns(event=None):
                    show_pattern_label(rule_key, patterns_frame, patterns_grid)
            patterns_grid.pack(anchor="w", fill="x")
            layout_entries()
  
        show_pattern_label(rule_key, patterns_frame, patterns_grid)

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

# Remove scrollable canvas/scrollbar logic from here; use the provided frame for all content
    # Place all rule UI elements in main_content instead of rule_frame
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
        def show_pattern_label(rule_key=rule_key, patterns_frame=patterns_frame, patterns_grid=patterns_grid):
            def layout_patterns(event=None):
                for w in patterns_grid.winfo_children():
                    w.destroy()
                pattern_strs = rules[rule_key]['patterns']
                width = patterns_grid.winfo_width()
                if width <= 1:
                    patterns_grid.after(10, layout_patterns)
                    return
                pattern_pixel_width = 120
                max_per_row = max(1, width // pattern_pixel_width)
                for idx, pattern in enumerate(pattern_strs):
                    row = idx // max_per_row
                    col = idx % max_per_row
                    label = ttkb.Label(patterns_grid, text=pattern, font=("Helvetica", 10), style="light.TLabel", cursor="hand2")
                    label.grid(row=row, column=col, padx=2, pady=2, sticky="w")
                    label.bind("<Button-1>", lambda event, rk=rule_key, pf=patterns_frame, pg=patterns_grid: show_pattern_edit(rk, pf, pg))
                if not pattern_strs:
                    label = ttkb.Label(patterns_grid, text="<no patterns>", font=("Helvetica", 10), style="light.TLabel", cursor="hand2")
                    label.grid(row=0, column=0, padx=2, pady=2, sticky="w")
                    label.bind("<Button-1>", lambda event, rk=rule_key, pf=patterns_frame, pg=patterns_grid: show_pattern_edit(rk, pf, pg))
            patterns_grid.bind("<Configure>", layout_patterns)
            layout_patterns()
        def show_pattern_edit(rule_key=rule_key, patterns_frame=patterns_frame, patterns_grid=patterns_grid):
            print(f"[DEBUG] show_pattern_edit called for rule: {rule_key}")
            patterns_grid.unbind("<Configure>")
            def layout_entries(event=None):
                for w in patterns_grid.winfo_children():
                    w.destroy()
                width = patterns_grid.winfo_width()
                if width <= 1:
                    patterns_grid.after(10, layout_entries)
                    return
                entry_pixel_width = 120
                max_per_row = max(1, width // entry_pixel_width)
                pattern_vars = []
                entries = []
                def save_patterns(event=None):
                    new_patterns = [v.get().strip() for v in pattern_vars if v.get().strip() and v.get().strip() != '<add pattern>']
                    new_patterns += [v.get().strip() for v in new_vars if v.get().strip() and v.get().strip() != '<add pattern>']
                    rules[rule_key]['patterns'] = new_patterns
                    save_rules(config_path, rules)
                    logger.info(f"Patterns for rule '{rule_key}' updated: {new_patterns}")
                    show_pattern_label(rule_key, patterns_frame, patterns_grid)
                def discard_patterns(event=None):
                    show_pattern_label(rule_key, patterns_frame, patterns_grid)
                # Existing patterns
                for idx, pattern in enumerate(rules[rule_key]['patterns']):
                    row = idx // max_per_row
                    col = idx % max_per_row
                    var = tk.StringVar(value=pattern)
                    entry = ttkb.Entry(patterns_grid, textvariable=var, width=15)
                    entry.grid(row=row, column=col, padx=2, pady=2, sticky="w")
                    entry.bind("<Return>", save_patterns)
                    entry.bind("<Escape>", discard_patterns)
                    pattern_vars.append(var)
                    entries.append(entry)
                # Dynamic add pattern entries with a plus button
                new_vars = []
                plus_buttons = []
                def add_new_pattern_entry():
                    idx = len(rules[rule_key]['patterns']) + len(new_vars)
                    row = idx // max_per_row
                    col = idx % max_per_row
                    new_var = tk.StringVar()
                    new_vars.append(new_var)
                    entry = ttkb.Entry(patterns_grid, textvariable=new_var, width=15)
                    entry.grid(row=row, column=col, padx=2, pady=2, sticky="w")
                    entry.insert(0, "<add pattern>")
                    def clear_placeholder(event, v=new_var):
                        if entry.get() == "<add pattern>":
                            entry.delete(0, tk.END)
                    entry.bind("<FocusIn>", clear_placeholder)
                    entry.bind("<Return>", save_patterns)
                    entry.bind("<Escape>", discard_patterns)
                    entries.append(entry)
                    # Remove previous plus button if it exists
                    if plus_buttons:
                        plus_buttons[-1].destroy()
                    # Add plus button next to the new entry
                    def add_and_focus():
                        add_new_pattern_entry()
                        # Focus the last entry (the new one)
                        entries[-1].focus_set()
                        entries[-1].icursor(tk.END)
                    plus_btn = ttkb.Button(patterns_grid, text="+", width=2, style="success.TButton", command=add_and_focus)
                    plus_btn.grid(row=row, column=col+1, padx=(0, 6), pady=2, sticky="w")
                    plus_buttons.append(plus_btn)
                add_new_pattern_entry()
                if entries:
                    entries[0].focus_set()
                def save_patterns(event=None):
                    new_patterns = [v.get().strip() for v in pattern_vars if v.get().strip() and v.get().strip() != '<add pattern>']
                    new_patterns += [v.get().strip() for v in new_vars if v.get().strip() and v.get().strip() != '<add pattern>']
                    rules[rule_key]['patterns'] = new_patterns
                    save_rules(config_path, rules)
                    logger.info(f"Patterns for rule '{rule_key}' updated: {new_patterns}")
                    show_pattern_label(rule_key, patterns_frame, patterns_grid)
                # Only one definition for discard_patterns
                def discard_patterns(event=None):
                    show_pattern_label(rule_key, patterns_frame, patterns_grid)
            patterns_grid.pack(anchor="w", fill="x")
            layout_entries()
  
        show_pattern_label(rule_key, patterns_frame, patterns_grid)

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
