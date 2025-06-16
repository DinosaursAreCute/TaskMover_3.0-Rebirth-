"""
Core configuration management for TaskMover Redesigned.
Streamlined version with better organization and extensibility.
"""

import os
import yaml
import logging
import uuid
from pathlib import Path
from typing import Dict, Any, Optional

# Configure logging
logger = logging.getLogger("TaskMover.Config")


class ConfigManager:
    """Centralized configuration management for TaskMover."""
    
    def __init__(self, config_dir: Optional[str] = None):
        self.config_dir = Path(config_dir) if config_dir else Path.home() / "default_dir" / "config"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        self.rules_file = self.config_dir / "rules.yml"
        self.settings_file = self.config_dir / "settings.yml"
        
    def load_rules(self) -> Dict[str, Any]:
        """Load rules with error handling and fallback to defaults."""
        if not self.rules_file.exists():
            logger.info("No rules file found, creating default rules")
            return self._create_default_rules()
        
        try:
            with open(self.rules_file, 'r', encoding='utf-8') as file:
                rules = yaml.safe_load(file) or {}
                
            # Ensure all rules have required fields
            self._validate_and_fix_rules(rules)
            return rules
            
        except Exception as e:
            logger.error(f"Failed to load rules: {e}")
            logger.info("Creating backup of corrupted rules and loading defaults")
            self._backup_corrupted_file(self.rules_file)
            return self._create_default_rules()
    
    def save_rules(self, rules: Dict[str, Any]) -> bool:
        """Save rules to file with error handling."""
        try:
            # Validate rules before saving
            self._validate_and_fix_rules(rules)
            
            with open(self.rules_file, 'w', encoding='utf-8') as file:
                yaml.dump(rules, file, default_flow_style=False, allow_unicode=True)
            
            logger.info(f"Saved {len(rules)} rules to {self.rules_file}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save rules: {e}")
            return False
    
    def load_settings(self) -> Dict[str, Any]:
        """Load application settings with defaults."""
        default_settings = {
            "organisation_folder": str(Path.home() / "Downloads"),
            "theme": "flatly",
            "developer_mode": False,
            "logging_level": "INFO",
            "collapse_on_start": True,
            "auto_save": True,
            "confirm_deletions": True,
            "logging_components": {
                "UI": True,
                "File Operations": True,
                "Rules": True,
                "Settings": True
            }
        }
        
        if not self.settings_file.exists():
            logger.info("No settings file found, using defaults")
            self.save_settings(default_settings)
            return default_settings
        
        try:
            with open(self.settings_file, 'r', encoding='utf-8') as file:
                settings = yaml.safe_load(file) or {}
            
            # Merge with defaults to ensure all keys exist
            merged_settings = {**default_settings, **settings}
            return merged_settings
            
        except Exception as e:
            logger.error(f"Failed to load settings: {e}")
            return default_settings
    
    def save_settings(self, settings: Dict[str, Any]) -> bool:
        """Save application settings."""
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as file:
                yaml.dump(settings, file, default_flow_style=False, allow_unicode=True)
            
            logger.info("Settings saved successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save settings: {e}")
            return False
    
    def _create_default_rules(self) -> Dict[str, Any]:
        """Create and save default rules."""
        user_dir = Path.home()
        default_rules = {
            "Documents": {
                "patterns": ["*.pdf", "*.docx", "*.txt", "*.xlsx", "*.csv", "*.pptx"],
                "path": str(user_dir / "Documents"),
                "unzip": False,
                "active": False,
                "priority": 0,
                "id": str(uuid.uuid4())
            },
            "Pictures": {
                "patterns": ["*.jpg", "*.jpeg", "*.png", "*.gif", "*.bmp", "*.svg"],
                "path": str(user_dir / "Pictures"),
                "unzip": False,
                "active": False,
                "priority": 1,
                "id": str(uuid.uuid4())
            },
            "Videos": {
                "patterns": ["*.mp4", "*.avi", "*.mkv", "*.mov", "*.wmv", "*.flv"],
                "path": str(user_dir / "Videos"),
                "unzip": False,
                "active": False,
                "priority": 2,
                "id": str(uuid.uuid4())
            },
            "Archives": {
                "patterns": ["*.zip", "*.rar", "*.7z", "*.tar.gz", "*.tar"],
                "path": str(user_dir / "Downloads" / "Archives"),
                "unzip": True,
                "active": False,
                "priority": 3,
                "id": str(uuid.uuid4())
            }
        }
        
        self.save_rules(default_rules)
        logger.info("Created default rules")
        return default_rules
    
    def _validate_and_fix_rules(self, rules: Dict[str, Any]) -> None:
        """Ensure all rules have required fields with proper defaults."""
        for rule_name, rule_data in rules.items():
            # Ensure required fields exist
            if 'patterns' not in rule_data:
                rule_data['patterns'] = []
            if 'path' not in rule_data:
                rule_data['path'] = ""
            if 'active' not in rule_data:
                rule_data['active'] = True
            if 'unzip' not in rule_data:
                rule_data['unzip'] = False
            if 'priority' not in rule_data:
                rule_data['priority'] = 0
            if 'id' not in rule_data:
                rule_data['id'] = str(uuid.uuid4())
                
            # Ensure patterns is a list
            if isinstance(rule_data['patterns'], str):
                rule_data['patterns'] = [rule_data['patterns']]
            elif not isinstance(rule_data['patterns'], list):
                rule_data['patterns'] = []
    
    def _backup_corrupted_file(self, file_path: Path) -> None:
        """Create a backup of a corrupted file."""
        try:
            backup_path = file_path.with_suffix(f"{file_path.suffix}.backup")
            file_path.rename(backup_path)
            logger.info(f"Backed up corrupted file to {backup_path}")
        except Exception as e:
            logger.error(f"Failed to backup corrupted file: {e}")


# Backward compatibility functions
def load_rules(config_path: str, fallback_path: Optional[str] = None) -> Dict[str, Any]:
    """Legacy function for backward compatibility."""
    config_dir = Path(config_path).parent
    manager = ConfigManager(str(config_dir))
    return manager.load_rules()


def save_rules(config_path: str, rules: Dict[str, Any]) -> None:
    """Legacy function for backward compatibility."""
    config_dir = Path(config_path).parent
    manager = ConfigManager(str(config_dir))
    manager.save_rules(rules)


def load_settings(logger_instance: Optional[logging.Logger] = None) -> Dict[str, Any]:
    """Legacy function for backward compatibility."""
    manager = ConfigManager()
    return manager.load_settings()


def save_settings(settings_path: str, settings: Dict[str, Any], 
                  logger_instance: Optional[logging.Logger] = None) -> None:
    """Legacy function for backward compatibility."""
    config_dir = Path(settings_path).parent
    manager = ConfigManager(str(config_dir))
    manager.save_settings(settings)


def load_or_initialize_rules(config_directory: str, logger_instance: logging.Logger) -> Dict[str, Any]:
    """Legacy function for backward compatibility."""
    manager = ConfigManager(config_directory)
    return manager.load_rules()
