"""
Configuration management for the TaskMover application.

This module provides functions for loading, saving, and applying application
settings and rules.
"""

import os
import yaml
import logging
from ttkbootstrap import Style
import uuid

def load_rules(config_path, fallback_path):
    """Load rules from a configuration file or fallback to a backup, auto-fixing broken YAML and missing parameters. If all else fails, ask the user before restoring defaults."""
    import re
    import sys
    required_params = {
        'patterns': [],
        'path': '',
        'unzip': False,
        'active': False
    }
    def clean_yaml_file(path):
        # Remove lines with Python object tags
        with open(path, 'r') as f:
            lines = f.readlines()
        cleaned = [line for line in lines if not re.match(r'^\s*!!python/object', line) and 'tag:yaml.org,2002:python/object' not in line]
        with open(path, 'w') as f:
            f.writelines(cleaned)
    def fix_missing_params(rules):
        changed = False
        for rule in rules.values():
            for k, v in required_params.items():
                if k not in rule:
                    rule[k] = v
                    changed = True
            # Assign UUID if missing
            if 'id' not in rule:
                rule['id'] = str(uuid.uuid4())
                changed = True
            # Assign priority if missing
            if 'priority' not in rule:
                rule['priority'] = 0
                changed = True
        return changed
    # Try loading, cleaning, and fixing
    for attempt in range(2):
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r') as file:
                    rules = yaml.safe_load(file)
                if not isinstance(rules, dict):
                    raise ValueError('Rules file is not a dictionary.')
                changed = fix_missing_params(rules)
                if changed:
                    save_rules(config_path, rules)
                return rules
            elif os.path.exists(fallback_path):
                with open(fallback_path, 'r') as file:
                    rules = yaml.safe_load(file)
                if not isinstance(rules, dict):
                    raise ValueError('Fallback rules file is not a dictionary.')
                changed = fix_missing_params(rules)
                if changed:
                    save_rules(config_path, rules)
                return rules
            else:
                # Only restore defaults without prompt if the file does not exist at all
                return create_default_rules(config_path)
        except yaml.YAMLError as e:
            if attempt == 0 and os.path.exists(config_path):
                clean_yaml_file(config_path)
                continue
            elif attempt == 0 and os.path.exists(fallback_path):
                clean_yaml_file(fallback_path)
                continue
            else:
                break
        except Exception as e:
            if attempt == 0 and os.path.exists(config_path):
                clean_yaml_file(config_path)
                continue
            elif attempt == 0 and os.path.exists(fallback_path):
                clean_yaml_file(fallback_path)
                continue
            else:
                break
    # If all else fails and the file exists, ask the user before restoring defaults
    if os.path.exists(config_path) or os.path.exists(fallback_path):
        prompt = ("Your rules file could not be loaded or auto-fixed. "
                  "Would you like to restore the default rules?\n"
                  "(Click Yes to restore defaults, or No to fix the file yourself and restart TaskMover.)")
        gui_prompted = False
        try:
            import tkinter as tk
            from tkinter import messagebox
            root = tk.Tk()
            root.withdraw()
            result = messagebox.askyesno("Restore Default Rules?", prompt)
            root.destroy()
            gui_prompted = True
            if result:
                return create_default_rules(config_path)
            else:
                raise RuntimeError("Rules file is invalid. Please fix it manually and restart TaskMover.")
        except Exception:
            if not gui_prompted:
                # Fallback to console prompt only if GUI prompt was not shown
                print(prompt)
                answer = input("Restore defaults? [y/N]: ").strip().lower()
                if answer == 'y':
                    return create_default_rules(config_path)
                else:
                    raise RuntimeError("Rules file is invalid. Please fix it manually and restart TaskMover.")
            else:
                # If GUI prompt was shown, do not prompt again
                raise RuntimeError("Rules file is invalid. Please fix it manually and restart TaskMover.")
    # If the file truly does not exist, restore defaults without prompt
    return create_default_rules(config_path)

def create_default_rules(config_path):
    """
    Create default rules and save them to the configuration file.

    Args:
        config_path (str): Path to the configuration file.

    Returns:
        dict: Dictionary of default rules.
    """
    user_dir = os.path.expanduser("~/")
    default_rules = {
        "Documents": {
            "patterns": ["*.pdf", "*.docx", "*.txt", "*.xlsx", "*.csv", "*.pptx"],
            "path": os.path.join(user_dir, "Documents"),
            "unzip": False,
            "active": False
        },
        "Pictures": {
            "patterns": ["*.jpg", "*.jpeg", "*.png", "*.gif", "*.bmp"],
            "path": os.path.join(user_dir, "Pictures"),
            "unzip": False,
            "active": False
        },
        "Compressed": {
            "patterns": ["*.zip", "*.rar", "*.7z", "*.tar.gz"],
            "path": os.path.join(user_dir, "Compressed"),
            "unzip": True,
            "active": False
        },
        "Videos": {
            "patterns": ["*.mp4", "*.mkv", "*.avi", "*.mov"],
            "path": os.path.join(user_dir, "Videos"),
            "unzip": False,
            "active": False
        },
        "Music": {
            "patterns": ["*.mp3", "*.wav", "*.flac"],
            "path": os.path.join(user_dir, "Music"),
            "unzip": False,
            "active": False
        },
        "Executables": {
            "patterns": ["*.exe", "*.msi"],
            "path": os.path.join(user_dir, "Executables"),
            "unzip": False,
            "active": False
        }
    }
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
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
    """Load settings from the settings file with strict validation and error handling."""
    import logging
    if not os.path.exists(settings_path):
        default_settings = {
            "base_directory": "",
            "theme": "superhero",
            "developer_mode": True,
            "logging_level": "DEBUG",
            "accent_color": "#0CEBC2",
            "background_color": "#FA069C",
            "text_color": "#000000",
            "logging_components": {
                "UI": 1,
                "File Operations": 1,
                "Rules": 1,
                "Settings": 1
            }
        }
        logging.getLogger("Settings").info(f"Loaded default settings: {default_settings}")
        return default_settings
    try:
        with open(settings_path, "r") as file:
            data = yaml.safe_load(file)
        # Strict validation: must be a dict and contain required keys
        required_keys = [
            "base_directory", "theme", "developer_mode", "logging_level",
            "accent_color", "background_color", "text_color", "logging_components"
        ]
        if not isinstance(data, dict) or not all(k in data for k in required_keys):
            raise ValueError("Settings file is not a valid TaskMover settings dictionary.")
        logging.getLogger("Settings").info(f"Settings loaded from {settings_path}: {data}")
        return data
    except FileNotFoundError:
        raise FileNotFoundError(f"Settings file not found: {settings_path}")
    except yaml.YAMLError as e:
        raise ValueError(f"Error parsing YAML settings file: {e}")
    except Exception as e:
        raise RuntimeError(f"Failed to load settings: {e}")

def save_settings(settings_path, settings, logger=None):
    import logging
    try:
        os.makedirs(os.path.dirname(settings_path), exist_ok=True)
        with open(settings_path, "w") as file:
            yaml.dump(settings, file)
        logging.getLogger("Settings").info(f"Settings saved successfully to {settings_path}.")
        if logger:
            logger.info(f"Settings saved successfully to {settings_path}.")
    except Exception as e:
        logging.getLogger("Settings").error(f"Failed to save settings: {e}")
        if logger:
            logger.error(f"Failed to save settings: {e}")
        raise RuntimeError(f"Failed to save settings: {e}")

def apply_settings(root, settings, logger):
    import logging
    style = Style()
    try:
        style.theme_use(settings.get("theme", "flatly"))
    except Exception as e:
        logging.getLogger("UI").error(f"Failed to apply theme: {e}")
        logger.error(f"Failed to apply theme: {e}")

   # root.configure(bg=settings.get("background_color", "#FFFFFF"))
    logger.setLevel(settings.get("logging_level", "INFO"))

    # Apply logging component levels
    apply_logging_component_settings(settings)
    for component, enabled in settings.get("logging_components", {}).items():
        if enabled:
            logging.getLogger("Settings").info(f"Logging enabled for {component}")
        else:
            logging.getLogger("Settings").info(f"Logging disabled for {component}")

def apply_logging_component_settings(settings):
    """
    Enable or disable logging for each component based on settings['logging_components'].
    """
    import logging
    component_loggers = {
        "UI": logging.getLogger("UI"),
        "File Operations": logging.getLogger("File Operations"),
        "Rules": logging.getLogger("Rules"),
        "Settings": logging.getLogger("Settings"),
    }
    for component, logger in component_loggers.items():
        enabled = settings.get("logging_components", {}).get(component, 0)
        if enabled:
            logger.setLevel(logging.DEBUG)
        else:
            logger.setLevel(logging.CRITICAL + 1)

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
