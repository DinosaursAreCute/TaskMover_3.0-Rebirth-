from tkinter import simpledialog, messagebox

from taskmover.config import save_rules

def add_rule(rules, config_path, rule_frame, logger, root):
    """Add a new rule to the rules dictionary."""
    rule_name = simpledialog.askstring("Add Rule", "Enter the name of the new rule:")
    if rule_name:
        if rule_name in rules:
            messagebox.showerror("Error", f"Rule '{rule_name}' already exists.")
            logger.warning(f"Attempted to add duplicate rule: {rule_name}")
        else:
            rules[rule_name] = {"patterns": [], "path": "", "unzip": False, "active": True}
            save_rules(config_path, rules)
            rule_frame.update_rules(rules)
            messagebox.showinfo("Success", f"Rule '{rule_name}' added successfully.")
            logger.info(f"Added new rule: {rule_name}")
