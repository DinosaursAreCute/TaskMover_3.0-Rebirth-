"""
UI button helpers for TaskMover.
"""

import ttkbootstrap as ttkb
import tkinter as tk
from .ui_helpers import Tooltip
from .ui_rule_helpers import add_rule_button, delete_multiple_rules, enable_all_rules, disable_all_rules

# Button helpers

def add_buttons_to_ui(root, rules, config_path, rule_frame, logger, update_rule_list_fn=None):
    """Add buttons for adding, removing, enabling, and disabling all rules to the existing UI."""
    button_frame = ttkb.Frame(root)
    button_frame.pack(fill="x", pady=10)

    add_btn = ttkb.Button(button_frame, text="Add Rule", command=lambda: add_rule_button(rules, config_path, rule_frame, logger, root, update_rule_list_fn))
    add_btn.pack(side="left", padx=5)
    Tooltip(add_btn, "Add a new rule for organizing files.")
    remove_btn = ttkb.Button(button_frame, text="Remove Rule", command=lambda: delete_multiple_rules(rules, config_path, logger, rule_frame, update_rule_list_fn))
    remove_btn.pack(side="left", padx=5)
    Tooltip(remove_btn, "Remove selected rules.")
    enable_btn = ttkb.Button(button_frame, text="Enable All", command=lambda: enable_all_rules(rules, config_path, rule_frame, logger, update_rule_list_fn))
    enable_btn.pack(side="left", padx=5)
    Tooltip(enable_btn, "Enable all rules.")
    disable_btn = ttkb.Button(button_frame, text="Disable All", command=lambda: disable_all_rules(rules, config_path, rule_frame, logger, update_rule_list_fn))
    disable_btn.pack(side="left", padx=5)
    Tooltip(disable_btn, "Disable all rules.")

def activate_all_button(rules, config_path, rule_frame, logger, update_rule_list_fn=None):
    """Activate all rules."""
    enable_all_rules(rules, config_path, rule_frame, logger, update_rule_list_fn)

def deactivate_all_button(rules, config_path, rule_frame, logger, update_rule_list_fn=None):
    """Deactivate all rules."""
    disable_all_rules(rules, config_path, rule_frame, logger, update_rule_list_fn)
