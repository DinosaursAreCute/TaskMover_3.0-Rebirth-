import os
import yaml

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
    """Create default rules and save them to the configuration file."""
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

def load_settings(logger=None):
    """Load application settings from a configuration file."""
    settings_path = os.path.expanduser("~/default_dir/config/settings.yml")
    default_settings = {
        "theme": "flatly",
        "developer_mode": False,
        "accent_color": None,
        "background_color": None,
        "text_color": None,
    }

    if not os.path.exists(settings_path):
        if logger:
            logger.warning(f"Settings file not found. Creating default settings at {settings_path}.")
        save_settings(settings_path, default_settings)
        return default_settings

    try:
        with open(settings_path, "r") as file:
            settings = yaml.safe_load(file)
            if not isinstance(settings, dict):
                raise ValueError("Invalid settings format")
            return settings
    except (yaml.YAMLError, ValueError) as e:
        if logger:
            logger.error(f"Failed to load settings: {e}. Reverting to default settings.")
        save_settings(settings_path, default_settings)
        return default_settings

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
