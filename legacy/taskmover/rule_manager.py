"""
Centralized rule management for TaskMover.
Handles adding, deleting, enabling/disabling, and updating rules.
"""
import tkinter as tk
import ttkbootstrap as ttkb
from tkinter import messagebox, simpledialog, filedialog
from taskmover.config import save_rules

def update_rule_list(rule_frame, rules, config_path, logger):
    # Get the canvas parent of the rule_frame (if it has one)
    canvas = None
    yview = (0, 1)  # Default scroll position (top)
    if rule_frame.master and isinstance(rule_frame.master, tk.Canvas):
        canvas = rule_frame.master
        # Store current scroll position if this is inside a canvas
        yview = canvas.yview()

    # Clear existing widgets
    for widget in rule_frame.winfo_children():
        widget.destroy()
        
    # Sort rules by priority before displaying
    from taskmover.rule_priority import get_sorted_rule_keys
    sorted_keys = get_sorted_rule_keys(rules)
    
    # Recreate the rule widgets in order of priority
    for rule_key in sorted_keys:
        rule = rules[rule_key]
        frame = ttkb.Frame(rule_frame)
        frame.pack(fill="x", pady=5, padx=10)
        ttkb.Label(frame, text=f"{rule_key}", font=("Helvetica", 12, "bold")).pack(anchor="w", pady=5)
        ttkb.Label(frame, text=f"Patterns: {', '.join(rule['patterns'])}", font=("Helvetica", 10)).pack(anchor="w", padx=10)
        ttkb.Label(frame, text=f"Path: {rule['path']}", font=("Helvetica", 10)).pack(anchor="w", padx=10)
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
        actions_frame = ttkb.Frame(frame)
        actions_frame.pack(fill="x", pady=5)
        edit_button = ttkb.Button(actions_frame, text="Edit", style="info.TButton", command=lambda rk=rule_key: edit_rule(rk, rules, config_path, logger, rule_frame))
        edit_button.pack(side="left", padx=10)
        delete_button = ttkb.Button(actions_frame, text="Delete", style="danger.TButton", command=lambda rk=rule_key: delete_rule(rk, rules, config_path, logger, rule_frame))
        delete_button.pack(side="left", padx=10)
    
    # Update the rule frame and canvas
    rule_frame.update_idletasks()
    
    # Restore the scroll position if we have a canvas
    if canvas:
        # Need to update the canvas's scroll region first
        canvas.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox("all"))
        # Then restore the view position
        canvas.after(10, lambda: canvas.yview_moveto(yview[0]))

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
    update_rule_list(rule_frame, rules, config_path, logger)

def disable_all_rules(rules, config_path, rule_frame, logger):
    for rule_key, rule in rules.items():
        rule['active'] = False
        logger.info(f"Rule '{rule_key}' disabled.")
    save_rules(config_path, rules)
    update_rule_list(rule_frame, rules, config_path, logger)

def add_rule(rules, config_path, rule_frame, logger, root):
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
    from taskmover.rule_priority import set_rule_priority
    
    edit_window = tk.Toplevel()
    edit_window.title(f"Edit Rule: {rule_key}")
    edit_window.geometry("500x400")
    cw.center_window(edit_window)
    edit_window.attributes('-topmost', True)
    
    ttkb.Label(edit_window, text=f"Edit Rule: {rule_key}", font=("Helvetica", 12, "bold")).pack(pady=10)
    
    # Rule name field
    ttkb.Label(edit_window, text="Rule Name:").pack(anchor="w", padx=10)
    name_var = tk.StringVar(value=rule_key)
    name_entry = ttkb.Entry(edit_window, textvariable=name_var, width=50)
    name_entry.pack(pady=5, padx=10)
    
    ttkb.Label(edit_window, text="Directory:").pack(anchor="w", padx=10)
    dir_var = tk.StringVar(value=rules[rule_key]['path'])
    dir_entry = ttkb.Entry(edit_window, textvariable=dir_var, width=50)
    dir_entry.pack(pady=5, padx=10)
    ttkb.Button(edit_window, text="Browse", command=lambda: dir_var.set(filedialog.askdirectory(title="Select Directory"))).pack(pady=5)
    
    ttkb.Label(edit_window, text="Patterns (comma-separated):").pack(anchor="w", padx=10)
    patterns_var = tk.StringVar(value=", ".join(rules[rule_key]['patterns']))
    patterns_entry = ttkb.Entry(edit_window, textvariable=patterns_var, width=50)
    patterns_entry.pack(pady=5, padx=10)
    
    def save_changes():
        new_name = name_var.get().strip()
        
        # If name is changed, handle it specially to maintain priority
        if new_name != rule_key and new_name:
            # Check if the new name already exists
            if new_name in rules:
                messagebox.showerror("Error", f"Rule '{new_name}' already exists.", parent=edit_window)
                return
                
            # Get current priority and other properties
            priority = rules[rule_key].get('priority', 0)
            rule_id = rules[rule_key].get('id', '')
            rule_data = rules[rule_key].copy()  # Copy all properties
            
            # Update properties
            rule_data['path'] = dir_var.get()
            rule_data['patterns'] = [pattern.strip() for pattern in patterns_var.get().split(",")]
            
            # Delete old and add new rule with the same priority
            del rules[rule_key]
            rules[new_name] = rule_data
            
            # Make sure priority is maintained
            if 'priority' not in rules[new_name]:
                rules[new_name]['priority'] = priority
            
            # Keep the same ID if it exists, or assign one
            if 'id' not in rules[new_name] or not rules[new_name]['id']:
                import uuid
                rules[new_name]['id'] = rule_id if rule_id else str(uuid.uuid4())
                
            # Log the rename action
            logger.info(f"Rule renamed from '{rule_key}' to '{new_name}'")
        else:
            # Just update existing rule
            rules[rule_key]['path'] = dir_var.get()
            rules[rule_key]['patterns'] = [pattern.strip() for pattern in patterns_var.get().split(",")]
            logger.info(f"Rule '{rule_key}' updated.")
            
            # Ensure it has a priority
            if 'priority' not in rules[rule_key]:
                rules[rule_key]['priority'] = 0
                
            # Ensure it has an ID
            if 'id' not in rules[rule_key] or not rules[rule_key]['id']:
                import uuid
                rules[rule_key]['id'] = str(uuid.uuid4())
        
        # Save and update UI
        save_rules(config_path, rules)
        update_rule_list(rule_frame, rules, config_path, logger)
        edit_window.destroy()
    
    ttkb.Button(edit_window, text="Save", command=save_changes).pack(pady=10)
    ttkb.Button(edit_window, text="Cancel", command=edit_window.destroy).pack(pady=5)
