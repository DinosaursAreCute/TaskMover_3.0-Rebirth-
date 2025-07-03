"""
Settings Storage Implementation

Provides file-based storage for settings with support for multiple formats,
backup/restore functionality, and atomic operations.
"""

import json
import logging
import shutil
import threading
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

import yaml

from . import SettingScope, ISettingStorage


class FileSettingStorage(ISettingStorage):
    """
    File-based settings storage with backup functionality.
    
    Features:
    - Atomic write operations
    - Automatic backup creation
    - Directory structure management
    - Thread-safe operations
    - Multiple format support
    """
    
    def __init__(self, base_path: Path, create_dirs: bool = True):
        """
        Initialize file-based settings storage.
        
        Args:
            base_path: Base directory for settings files
            create_dirs: Whether to create directories automatically
        """
        self._base_path = Path(base_path)
        self._create_dirs = create_dirs
        self._lock = threading.RLock()
        self._logger = logging.getLogger(f"{__name__}.FileSettingStorage")
        
        # Define file names for each scope
        self._scope_files = {
            SettingScope.USER: "user_settings.yaml",
            SettingScope.APPLICATION: "app_settings.yaml",
            SettingScope.SYSTEM: "system_settings.yaml",
            SettingScope.RULE: "rule_settings.yaml",
            SettingScope.UI: "ui_settings.yaml",
            SettingScope.LOGGING: "logging_settings.yaml",
        }
        
        # Create base directory if needed
        if self._create_dirs:
            self._base_path.mkdir(parents=True, exist_ok=True)
            self._logger.debug(f"Initialized settings storage at: {self._base_path}")
    
    def _get_settings_file(self, scope: SettingScope) -> Path:
        """Get the settings file path for a scope."""
        return self._base_path / self._scope_files[scope]
    
    def _get_backup_dir(self, scope: SettingScope) -> Path:
        """Get the backup directory for a scope."""
        backup_dir = self._base_path / "backups" / scope.value
        if self._create_dirs:
            backup_dir.mkdir(parents=True, exist_ok=True)
        return backup_dir
    
    def load(self, scope: SettingScope) -> Dict[str, Any]:
        """Load settings for a specific scope."""
        with self._lock:
            try:
                settings_file = self._get_settings_file(scope)
                
                if not settings_file.exists():
                    self._logger.debug(f"Settings file not found for scope {scope.value}: {settings_file}")
                    return {}
                
                with open(settings_file, 'r', encoding='utf-8') as f:
                    if settings_file.suffix.lower() == '.json':
                        settings = json.load(f)
                    else:  # Default to YAML
                        settings = yaml.safe_load(f) or {}
                
                self._logger.debug(f"Loaded {len(settings)} settings for scope {scope.value}")
                return settings
                
            except Exception as e:
                self._logger.error(f"Error loading settings for scope {scope.value}: {e}")
                return {}
    
    def save(self, scope: SettingScope, settings: Dict[str, Any]) -> None:
        """Save settings for a specific scope."""
        with self._lock:
            try:
                settings_file = self._get_settings_file(scope)
                
                # Create directory if needed
                if self._create_dirs:
                    settings_file.parent.mkdir(parents=True, exist_ok=True)
                
                # Atomic write using temporary file
                temp_file = settings_file.with_suffix(settings_file.suffix + '.tmp')
                
                with open(temp_file, 'w', encoding='utf-8') as f:
                    if settings_file.suffix.lower() == '.json':
                        json.dump(settings, f, indent=2, ensure_ascii=False)
                    else:  # Default to YAML
                        yaml.dump(settings, f, default_flow_style=False, allow_unicode=True)
                
                # Atomic move
                temp_file.replace(settings_file)
                
                self._logger.debug(f"Saved {len(settings)} settings for scope {scope.value}")
                
            except Exception as e:
                self._logger.error(f"Error saving settings for scope {scope.value}: {e}")
                # Clean up temp file if it exists
                temp_file = self._get_settings_file(scope).with_suffix('.tmp')
                if temp_file.exists():
                    temp_file.unlink()
                raise
    
    def delete(self, scope: SettingScope, key: str) -> bool:
        """Delete a specific setting."""
        with self._lock:
            try:
                settings = self.load(scope)
                
                if key in settings:
                    del settings[key]
                    self.save(scope, settings)
                    self._logger.debug(f"Deleted setting '{key}' from scope {scope.value}")
                    return True
                else:
                    self._logger.debug(f"Setting '{key}' not found in scope {scope.value}")
                    return False
                    
            except Exception as e:
                self._logger.error(f"Error deleting setting '{key}' from scope {scope.value}: {e}")
                return False
    
    def exists(self, scope: SettingScope, key: str) -> bool:
        """Check if a setting exists."""
        try:
            settings = self.load(scope)
            return key in settings
        except Exception:
            return False
    
    def backup(self, scope: SettingScope) -> str:
        """Create a backup of settings and return backup identifier."""
        with self._lock:
            try:
                settings_file = self._get_settings_file(scope)
                
                if not settings_file.exists():
                    self._logger.warning(f"No settings file to backup for scope {scope.value}")
                    return ""
                
                # Generate backup ID with timestamp
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]  # Include milliseconds
                backup_id = f"{scope.value}_{timestamp}"
                
                # Create backup directory
                backup_dir = self._get_backup_dir(scope)
                backup_file = backup_dir / f"{backup_id}.yaml"
                
                # Copy settings file to backup
                shutil.copy2(settings_file, backup_file)
                
                self._logger.info(f"Created backup {backup_id} for scope {scope.value}")
                return backup_id
                
            except Exception as e:
                self._logger.error(f"Error creating backup for scope {scope.value}: {e}")
                raise
    
    def restore(self, scope: SettingScope, backup_id: str) -> bool:
        """Restore settings from backup."""
        with self._lock:
            try:
                backup_dir = self._get_backup_dir(scope)
                backup_file = backup_dir / f"{backup_id}.yaml"
                
                if not backup_file.exists():
                    self._logger.error(f"Backup file not found: {backup_file}")
                    return False
                
                settings_file = self._get_settings_file(scope)
                
                # Create current backup before restoring
                current_backup_id = self.backup(scope)
                self._logger.info(f"Created current backup {current_backup_id} before restore")
                
                # Restore from backup
                shutil.copy2(backup_file, settings_file)
                
                self._logger.info(f"Restored settings for scope {scope.value} from backup {backup_id}")
                return True
                
            except Exception as e:
                self._logger.error(f"Error restoring backup {backup_id} for scope {scope.value}: {e}")
                return False
    
    def list_backups(self, scope: SettingScope) -> list[str]:
        """List available backups for a scope."""
        try:
            backup_dir = self._get_backup_dir(scope)
            
            if not backup_dir.exists():
                return []
            
            backup_files = list(backup_dir.glob(f"{scope.value}_*.yaml"))
            backup_ids = [f.stem for f in backup_files]
            backup_ids.sort(reverse=True)  # Most recent first
            
            return backup_ids
            
        except Exception as e:
            self._logger.error(f"Error listing backups for scope {scope.value}: {e}")
            return []
    
    def cleanup_old_backups(self, scope: SettingScope, keep_count: int = 10) -> int:
        """
        Clean up old backups, keeping only the most recent ones.
        
        Args:
            scope: The settings scope
            keep_count: Number of backups to keep
            
        Returns:
            Number of backups deleted
        """
        with self._lock:
            try:
                backup_ids = self.list_backups(scope)
                
                if len(backup_ids) <= keep_count:
                    return 0
                
                backups_to_delete = backup_ids[keep_count:]
                deleted_count = 0
                
                backup_dir = self._get_backup_dir(scope)
                
                for backup_id in backups_to_delete:
                    backup_file = backup_dir / f"{backup_id}.yaml"
                    if backup_file.exists():
                        backup_file.unlink()
                        deleted_count += 1
                
                self._logger.info(f"Cleaned up {deleted_count} old backups for scope {scope.value}")
                return deleted_count
                
            except Exception as e:
                self._logger.error(f"Error cleaning up backups for scope {scope.value}: {e}")
                return 0


class MemorySettingStorage(ISettingStorage):
    """
    In-memory settings storage for testing and temporary use.
    
    This storage does not persist settings between application runs
    but supports all the same operations as file storage.
    """
    
    def __init__(self):
        """Initialize in-memory settings storage."""
        self._settings: Dict[SettingScope, Dict[str, Any]] = {}
        self._backups: Dict[SettingScope, Dict[str, Dict[str, Any]]] = {}
        self._lock = threading.RLock()
        self._logger = logging.getLogger(f"{__name__}.MemorySettingStorage")
        
        # Initialize empty settings for all scopes
        for scope in SettingScope:
            self._settings[scope] = {}
            self._backups[scope] = {}
        
        self._logger.debug("Initialized in-memory settings storage")
    
    def load(self, scope: SettingScope) -> Dict[str, Any]:
        """Load settings for a specific scope."""
        with self._lock:
            settings = self._settings[scope].copy()
            self._logger.debug(f"Loaded {len(settings)} settings for scope {scope.value}")
            return settings
    
    def save(self, scope: SettingScope, settings: Dict[str, Any]) -> None:
        """Save settings for a specific scope."""
        with self._lock:
            self._settings[scope] = settings.copy()
            self._logger.debug(f"Saved {len(settings)} settings for scope {scope.value}")
    
    def delete(self, scope: SettingScope, key: str) -> bool:
        """Delete a specific setting."""
        with self._lock:
            if key in self._settings[scope]:
                del self._settings[scope][key]
                self._logger.debug(f"Deleted setting '{key}' from scope {scope.value}")
                return True
            return False
    
    def exists(self, scope: SettingScope, key: str) -> bool:
        """Check if a setting exists."""
        with self._lock:
            return key in self._settings[scope]
    
    def backup(self, scope: SettingScope) -> str:
        """Create a backup of settings and return backup identifier."""
        with self._lock:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]
            backup_id = f"{scope.value}_{timestamp}"
            
            self._backups[scope][backup_id] = self._settings[scope].copy()
            
            self._logger.info(f"Created backup {backup_id} for scope {scope.value}")
            return backup_id
    
    def restore(self, scope: SettingScope, backup_id: str) -> bool:
        """Restore settings from backup."""
        with self._lock:
            if backup_id in self._backups[scope]:
                self._settings[scope] = self._backups[scope][backup_id].copy()
                self._logger.info(f"Restored settings for scope {scope.value} from backup {backup_id}")
                return True
            else:
                self._logger.error(f"Backup {backup_id} not found for scope {scope.value}")
                return False
