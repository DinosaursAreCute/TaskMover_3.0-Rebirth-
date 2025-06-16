"""
Rule management UI helpers for TaskMover.
"""

import tkinter as tk
from .ui_helpers import Tooltip
import ttkbootstrap as ttkb
from tkinter import messagebox, filedialog, simpledialog
from taskmover.config import save_rules
from taskmover.pattern_grid_helpers import pattern_grid_label, pattern_grid_edit
from .rule_priority import get_sorted_rule_keys, move_rule_priority, set_rule_priority
import logging
import time

# Import other functions from the original file
from .ui_rule_helpers import (
    update_parent_canvas_scrollregion, update_rule_list, open_file_dialog, 
    toggle_rule_active, toggle_unzip, enable_all_rules, disable_all_rules, 
    add_rule_button, delete_rule, delete_multiple_rules, edit_rule,
    update_or_create_rule_frame, log_widget_tree
)

def editable_rule_name(parent, rule_key, rules, config_path, logger, on_rename, font=("Helvetica", 12, "bold")):
    """Create an editable rule name label that can be clicked to edit inline."""
    frame = ttkb.Frame(parent)
    name_var = tk.StringVar(value=rule_key)
    label = ttkb.Label(frame, textvariable=name_var, font=font, cursor="xterm")
    entry = ttkb.Entry(frame, textvariable=name_var, font=font, width=24)
    check_btn = ttkb.Button(frame, text="✔", width=2, style="success.TButton")
    cancel_flag = {'cancel': False}
    current_key = [rule_key]  # mutable container for current rule key
    
    def show_entry(event=None):
        """Show the entry field to allow editing."""
        label.pack_forget()
        entry.pack(side="left", fill="x", expand=True)
        check_btn.pack(side="left")
        entry.focus_set()
        entry.icursor(tk.END)
        
    def save_name(event=None):
        """Save the new name and update the rule."""
        new_name = name_var.get().strip()
        if not new_name or new_name == current_key[0]:
            cancel_edit()
            return
        if new_name in rules:
            messagebox.showerror("Name Exists", f"A rule named '{new_name}' already exists.")
            return
            
        # Store old priority and ID before rename
        old_priority = rules[current_key[0]].get('priority', 0)
        old_id = rules[current_key[0]].get('id', '')
        
        # Get complete rule data
        rule_data = rules.pop(current_key[0])
        
        # Explicitly ensure priority is set before adding to rules dict
        if 'priority' not in rule_data:
            rule_data['priority'] = old_priority
        if 'id' not in rule_data:
            import uuid
            rule_data['id'] = old_id or str(uuid.uuid4())
            
        # Add with new name
        rules[new_name] = rule_data
            
        logger.info(f"Rule renamed from '{current_key[0]}' to '{new_name}' (priority: {rule_data.get('priority')})")
        save_rules(config_path, rules)
        current_key[0] = new_name
        name_var.set(new_name)
        entry.pack_forget()
        check_btn.pack_forget()
        label.pack(side="left")
        
        # Find the main rule list frame (the one with _rule_frames)
        main_rule_frame = parent
        while main_rule_frame is not None and not hasattr(main_rule_frame, '_rule_frames'):
            main_rule_frame = getattr(main_rule_frame, 'master', None)
            
        # Update UI with sorted rules
        if main_rule_frame is not None:
            update_rule_list(main_rule_frame, rules, config_path, logger)
            
        # Notify parent that rename happened
        on_rename(new_name)
        
    def cancel_edit(event=None):
        """Cancel editing and restore original name."""
        if cancel_flag['cancel']:
            return
        name_var.set(current_key[0])
        entry.pack_forget()
        check_btn.pack_forget()
        label.pack(side="left")
        
    def check_and_save():
        """Handle the check button click."""
        cancel_flag['cancel'] = True
        save_name()
        cancel_flag['cancel'] = False
        
    # Bind events
    label.bind("<Button-1>", show_entry)
    entry.bind("<Return>", save_name)
    entry.bind("<Escape>", cancel_edit)
    entry.bind("<FocusOut>", cancel_edit)
    check_btn.config(command=check_and_save)
    
    # Initial state
    label.pack(side="left")
    
    return frame, name_var
