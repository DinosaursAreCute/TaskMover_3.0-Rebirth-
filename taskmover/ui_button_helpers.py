"""
UI button helpers for TaskMover.
"""

import ttkbootstrap as ttkb
from .ui_rule_helpers import add_rule_button, delete_multiple_rules, enable_all_rules, disable_all_rules

# Button helpers

def add_buttons_to_ui(root, rules, config_path, rule_frame, logger):
    """Add buttons for adding, removing, enabling, and disabling all rules to the existing UI."""
    button_frame = ttkb.Frame(root)
    button_frame.pack(fill="x", pady=10)

    ttkb.Button(button_frame, text="Add Rule", command=lambda: add_rule_button(rules, config_path, rule_frame, logger, root)).pack(side="left", padx=5)
    ttkb.Button(button_frame, text="Remove Rule", command=lambda: delete_multiple_rules(rules, config_path, logger, rule_frame)).pack(side="left", padx=5)
    ttkb.Button(button_frame, text="Enable All", command=lambda: enable_all_rules(rules, config_path, rule_frame, logger)).pack(side="left", padx=5)
    ttkb.Button(button_frame, text="Disable All", command=lambda: disable_all_rules(rules, config_path, rule_frame, logger)).pack(side="left", padx=5)

def activate_all_button(rules, config_path, rule_frame, logger):
    """Activate all rules."""
    enable_all_rules(rules, config_path, rule_frame, logger)

def deactivate_all_button(rules, config_path, rule_frame, logger):
    """Deactivate all rules."""
    disable_all_rules(rules, config_path, rule_frame, logger)
