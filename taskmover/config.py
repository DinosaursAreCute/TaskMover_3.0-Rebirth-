"""
Configuration management for the TaskMover application.

This module provides functions for loading, saving, and applying application
settings and rules.
"""

import os
import yaml
import logging
from ttkbootstrap import Style

def load_rules(config_path, fallback_path):
    """Load rules from a configuration file or fallback to a backup."""
    try:
        if os.path.exists(config_path):
            with open(config_path, 'r') as file:
                rules = yaml.safe_load(file)
                for rule in rules.values():
                    rule.setdefault('unzip', False)  # Add default value for 'unzip'
                return rules
        elif os.path.exists(fallback_path):
            with open(fallback_path, 'r') as file:
                rules = yaml.safe_load(file)
                for rule in rules.values():
                    rule.setdefault('unzip', False)  # Add default value for 'unzip'
                return rules
        else:
            return create_default_rules(config_path)
    except Exception as e:
        raise RuntimeError(f"Failed to load rules: {e}")

def create_default_rules(config_path):
    """
    Create default rules and save them to the configuration file.

    Args:
        config_path (str): Path to the configuration file.

    Returns:
        dict: Dictionary of default rules.
    """
    default_dir = os.path.expanduser("~/default_dir")
    default_rules = {
        "Pictures": {"patterns": ["*.jpg", "*.png"], "path": os.path.join(default_dir, "Pictures"),"unzip":False, "active": True},
        "Documents": {"patterns": ["*.pdf", "*.docx"], "path": os.path.join(default_dir, "Documents"),"unzip":False, "active": True},
    }
    os.makedirs(default_dir, exist_ok=True)
    save_rules(config_path, default_rules)
    return default_rules

def save_rules(config_path, rules):
    """Save rules to the configuration file."""
    config_directory = os.path.expanduser("~/default_dir/config")
    config_path = os.path.join(config_directory, "rules.yml")
    try:
        with open(config_path, 'w') as file:
            yaml.dump(rules, file, default_flow_style=False)
    except Exception as e:
        raise RuntimeError(f"Failed to save rules: {e}")

def load_settings(settings_path):
    """Load settings from the settings file."""
    if not os.path.exists(settings_path):
        return {
            "base_directory": "",
            "theme": "flatly",
            "developer_mode": False,
            "logging_level": "INFO",
            "accent_color": "#FFFFFF",
            "background_color": "#FFFFFF",
            "text_color": "#000000",
            "logging_components": {
                "UI": 1,
                "File Operations": 1,
                "Rules": 1,
                "Settings": 1
            }
        }

    with open(settings_path, "r") as file:
        import yaml
        return yaml.safe_load(file)

def save_settings(settings_path, settings, logger=None):
    """Save application settings to a configuration file."""
    try:
        os.makedirs(os.path.dirname(settings_path), exist_ok=True)
        with open(settings_path, "w") as file:
            yaml.dump(settings, file)
        if logger:
            logger.info(f"Settings saved successfully to {settings_path}.")
    except Exception as e:
        if logger:
            logger.error(f"Failed to save settings: {e}")
        raise RuntimeError(f"Failed to save settings: {e}")

def apply_settings(root, settings, logger):
    """Apply settings to the application."""
    style = Style()
    try:
        style.theme_use(settings.get("theme", "flatly"))
    except Exception as e:
        logger.error(f"Failed to apply theme: {e}")

    root.configure(bg=settings.get("background_color", "#FFFFFF"))
    # Note: Tkinter root does not support 'fg' or 'accent_color' directly.
    logger.setLevel(settings.get("logging_level", "INFO"))

    # Apply logging component levels (if needed)
    for component, enabled in settings.get("logging_components", {}).items():
        if enabled:
            logger.info(f"Logging enabled for {component}")
        else:
            logger.info(f"Logging disabled for {component}")

def load_or_initialize_rules(config_path, fallback_path, logger=None):
    """Load rules from a configuration file or initialize default rules."""
    try:
        if os.path.exists(config_path):
            if logger:
                logger.info(f"Loading rules from configuration file: {config_path}")
            rules = load_rules(config_path, fallback_path)
            for rule in rules.values():
                rule.setdefault('unzip', False)  # Add default value for 'unzip'
            return rules
        else:
            if logger:
                logger.warning(f"Configuration file not found. Creating default rules at: {config_path}")
            return create_default_rules(config_path)
    except Exception as e:
        if logger:
            logger.error(f"Error loading or initializing rules: {e}")
        raise
