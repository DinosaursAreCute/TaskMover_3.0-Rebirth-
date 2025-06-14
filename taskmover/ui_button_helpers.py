"""
UI button helpers for TaskMover.
"""

import ttkbootstrap as ttkb
from .ui_rule_helpers import add_rule_button, delete_multiple_rules, enable_all_rules, disable_all_rules

# Button helpers

def add_buttons_to_ui(root, rules, config_path, rule_frame, logger, update_rule_list_fn=None):
    """Add buttons for adding, removing, enabling, and disabling all rules to the existing UI."""
    button_frame = ttkb.Frame(root)
    button_frame.pack(fill="x", pady=10)

    ttkb.Button(button_frame, text="Add Rule", command=lambda: add_rule_button(rules, config_path, rule_frame, logger, root, update_rule_list_fn)).pack(side="left", padx=5)
    ttkb.Button(button_frame, text="Remove Rule", command=lambda: delete_multiple_rules(rules, config_path, logger, rule_frame, update_rule_list_fn)).pack(side="left", padx=5)
    ttkb.Button(button_frame, text="Enable All", command=lambda: enable_all_rules(rules, config_path, rule_frame, logger, update_rule_list_fn)).pack(side="left", padx=5)
    ttkb.Button(button_frame, text="Disable All", command=lambda: disable_all_rules(rules, config_path, rule_frame, logger, update_rule_list_fn)).pack(side="left", padx=5)

def activate_all_button(rules, config_path, rule_frame, logger, update_rule_list_fn=None):
    """Activate all rules."""
    enable_all_rules(rules, config_path, rule_frame, logger, update_rule_list_fn)

def deactivate_all_button(rules, config_path, rule_frame, logger, update_rule_list_fn=None):
    """Deactivate all rules."""
    disable_all_rules(rules, config_path, rule_frame, logger, update_rule_list_fn)
