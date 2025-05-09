import os
import yaml
import shutil
from tkinter import messagebox

def load_rules(config_path, fallback_path):
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as file:
                rules = yaml.safe_load(file)
                shutil.copy(config_path, fallback_path)
                return rules
        except (yaml.YAMLError, IOError):
            if os.path.exists(fallback_path):
                with open(fallback_path, 'r') as file:
                    return yaml.safe_load(file)
            else:
                return create_default_rules(config_path)
    else:
        return create_default_rules(config_path)

def create_default_rules(config_path):
    default_dir = os.path.expanduser("~/default_dir")
    default_rules = {
        "Pictures": {"patterns": ["*.jpg", "*.jpeg", "*.png", "*.gif"], "path": os.path.join(default_dir, "Pictures"), "unzip": False, "active": True},
        "Documents": {"patterns": ["*.pdf", "*.docx", "*.txt"], "path": os.path.join(default_dir, "Documents"), "unzip": False, "active": True},
        "Videos": {"patterns": ["*.mp4", "*.mkv", "*.avi"], "path": os.path.join(default_dir, "Videos"), "unzip": False, "active": True},
        "Archives": {"patterns": ["*.zip", "*.rar"], "path": os.path.join(default_dir, "Archives"), "unzip": True, "active": True},
    }
    os.makedirs(default_dir, exist_ok=True)
    save_rules(config_path, default_rules)
    return default_rules

def save_rules(config_path, rules, logger=None):
    with open(config_path, 'w') as file:
        yaml.dump(rules, file, default_flow_style=False)
    if logger:
        logger.info(f"Rules saved to {config_path}.")
