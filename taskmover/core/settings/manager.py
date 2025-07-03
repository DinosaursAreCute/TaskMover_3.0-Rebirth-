"""
Settings Manager Implementation

Provides the main SettingManager class with comprehensive settings management,
validation, serialization, change tracking, and backup functionality.
"""

import datetime
import logging
import threading
from pathlib import Path
from typing import Any, Dict, List, Optional, Type, TypeVar

from . import (
    SettingScope,
    SettingFormat,
    SettingType,
    SettingDefinition,
    SettingChange,
    SettingValidationResult,
    ISettingValidator,
    ISettingSerializer,
    ISettingStorage,
    ISettingChangeListener,
    ISettingManager,
)

T = TypeVar("T")


class SettingManager(ISettingManager):
    """
    Main settings manager implementation with comprehensive functionality.
    
    Features:
    - Multi-scope setting management
    - Validation and type checking
    - Change tracking and history
    - Backup and restore
    - Import/export functionality
    - Change notifications
    - Thread-safe operations
    """
    
    def __init__(self, storage: ISettingStorage, validator: ISettingValidator):
        """
        Initialize the settings manager.
        
        Args:
            storage: Settings storage backend
            validator: Settings validator
        """
        self._storage = storage
        self._validator = validator
        self._settings: Dict[SettingScope, Dict[str, Any]] = {}
        self._definitions: Dict[str, SettingDefinition] = {}
        self._change_history: List[SettingChange] = []
        self._change_listeners: List[ISettingChangeListener] = []
        self._serializers: Dict[SettingFormat, ISettingSerializer] = {}
        self._lock = threading.RLock()
        self._logger = logging.getLogger(f"{__name__}.SettingManager")
        
        # Initialize default scopes
        for scope in SettingScope:
            self._settings[scope] = {}
        
        self._logger.info("SettingManager initialized")
    
    def register_serializer(self, format: SettingFormat, serializer: ISettingSerializer) -> None:
        """Register a serializer for a specific format."""
        with self._lock:
            self._serializers[format] = serializer
            self._logger.debug(f"Registered serializer for format: {format.value}")
    
    def get(self, key: str, default: Optional[T] = None, scope: Optional[SettingScope] = None) -> T:
        """Get a setting value with scope resolution."""
        with self._lock:
            # If no scope specified, search in order of precedence
            if scope is None:
                scopes_to_search = [SettingScope.USER, SettingScope.APPLICATION, SettingScope.SYSTEM]
            else:
                scopes_to_search = [scope]
            
            for search_scope in scopes_to_search:
                if key in self._settings[search_scope]:
                    value = self._settings[search_scope][key]
                    self._logger.debug(f"Retrieved setting {key} = {value} from scope {search_scope.value}")
                    return value
            
            # Return default if not found
            definition = self._definitions.get(key)
            if definition and default is None:
                default = definition.default_value
            
            self._logger.debug(f"Setting {key} not found, returning default: {default}")
            return default
    
    def set(self, key: str, value: Any, scope: Optional[SettingScope] = None, 
            source: Optional[str] = None) -> bool:
        """Set a setting value with validation."""
        with self._lock:
            try:
                # Determine scope
                if scope is None:
                    definition = self._definitions.get(key)
                    scope = definition.scope if definition else SettingScope.USER
                
                # Validate the value
                validation_result = self.validate(key, value)
                if not validation_result.is_valid:
                    self._logger.error(f"Validation failed for setting {key}: {validation_result.errors}")
                    return False
                
                # Use normalized value if available
                final_value = validation_result.normalized_value if validation_result.normalized_value is not None else value
                
                # Get old value for change tracking
                old_value = self._settings[scope].get(key)
                
                # Set the value
                self._settings[scope][key] = final_value
                
                # Create change record
                change = SettingChange(
                    key=key,
                    old_value=old_value,
                    new_value=final_value,
                    timestamp=datetime.datetime.now(),
                    source=source
                )
                self._change_history.append(change)
                
                # Notify listeners
                self._notify_change_listeners(change)
                
                self._logger.info(f"Setting {key} changed from {old_value} to {final_value} in scope {scope.value}")
                return True
                
            except Exception as e:
                self._logger.error(f"Error setting {key}: {e}")
                return False
    
    def delete(self, key: str, scope: Optional[SettingScope] = None) -> bool:
        """Delete a setting."""
        with self._lock:
            try:
                if scope is None:
                    # Delete from all scopes
                    deleted = False
                    for s in SettingScope:
                        if key in self._settings[s]:
                            old_value = self._settings[s][key]
                            del self._settings[s][key]
                            
                            # Create change record
                            change = SettingChange(
                                key=key,
                                old_value=old_value,
                                new_value=None,
                                timestamp=datetime.datetime.now(),
                                source="delete"
                            )
                            self._change_history.append(change)
                            self._notify_change_listeners(change)
                            deleted = True
                    
                    if deleted:
                        self._logger.info(f"Setting {key} deleted from all scopes")
                    return deleted
                else:
                    if key in self._settings[scope]:
                        old_value = self._settings[scope][key]
                        del self._settings[scope][key]
                        
                        # Create change record
                        change = SettingChange(
                            key=key,
                            old_value=old_value,
                            new_value=None,
                            timestamp=datetime.datetime.now(),
                            source="delete"
                        )
                        self._change_history.append(change)
                        self._notify_change_listeners(change)
                        
                        self._logger.info(f"Setting {key} deleted from scope {scope.value}")
                        return True
                    return False
                    
            except Exception as e:
                self._logger.error(f"Error deleting setting {key}: {e}")
                return False
    
    def exists(self, key: str, scope: Optional[SettingScope] = None) -> bool:
        """Check if a setting exists."""
        with self._lock:
            if scope is None:
                return any(key in self._settings[s] for s in SettingScope)
            else:
                return key in self._settings[scope]
    
    def get_all(self, scope: Optional[SettingScope] = None) -> Dict[str, Any]:
        """Get all settings for a scope."""
        with self._lock:
            if scope is None:
                # Merge all scopes with precedence
                result = {}
                for s in reversed(list(SettingScope)):  # System < App < User
                    result.update(self._settings[s])
                return result
            else:
                return self._settings[scope].copy()
    
    def register_definition(self, definition: SettingDefinition) -> None:
        """Register a setting definition."""
        with self._lock:
            self._definitions[definition.key] = definition
            self._logger.debug(f"Registered definition for setting: {definition.key}")
    
    def get_definition(self, key: str) -> Optional[SettingDefinition]:
        """Get a setting definition."""
        return self._definitions.get(key)
    
    def get_definitions(self, scope: Optional[SettingScope] = None, 
                       category: Optional[str] = None) -> List[SettingDefinition]:
        """Get setting definitions with optional filtering."""
        definitions = list(self._definitions.values())
        
        if scope is not None:
            definitions = [d for d in definitions if d.scope == scope]
        
        if category is not None:
            definitions = [d for d in definitions if d.category == category]
        
        return definitions
    
    def validate(self, key: str, value: Any) -> SettingValidationResult:
        """Validate a setting value."""
        definition = self._definitions.get(key)
        if definition is None:
            # Allow unknown settings with basic validation
            return SettingValidationResult(is_valid=True, normalized_value=value)
        
        return self._validator.validate(definition, value)
    
    def reset(self, key: str, scope: Optional[SettingScope] = None) -> bool:
        """Reset a setting to its default value."""
        definition = self._definitions.get(key)
        if definition is None:
            self._logger.warning(f"Cannot reset {key}: no definition found")
            return False
        
        target_scope = scope if scope is not None else definition.scope
        return self.set(key, definition.default_value, target_scope, "reset")
    
    def reset_all(self, scope: Optional[SettingScope] = None) -> int:
        """Reset all settings in a scope to defaults."""
        with self._lock:
            reset_count = 0
            
            if scope is None:
                scopes_to_reset = list(SettingScope)
            else:
                scopes_to_reset = [scope]
            
            for target_scope in scopes_to_reset:
                # Get all settings in this scope
                settings_to_reset = list(self._settings[target_scope].keys())
                
                for key in settings_to_reset:
                    if self.reset(key, target_scope):
                        reset_count += 1
            
            self._logger.info(f"Reset {reset_count} settings")
            return reset_count
    
    def export_settings(self, scope: Optional[SettingScope] = None, 
                       format: SettingFormat = SettingFormat.YAML) -> str:
        """Export settings to string format."""
        with self._lock:
            serializer = self._serializers.get(format)
            if serializer is None:
                raise ValueError(f"No serializer registered for format: {format}")
            
            settings = self.get_all(scope)
            result = serializer.serialize(settings)
            
            self._logger.info(f"Exported {len(settings)} settings in {format.value} format")
            return result
    
    def import_settings(self, data: str, scope: Optional[SettingScope] = None,
                       format: SettingFormat = SettingFormat.YAML,
                       merge: bool = True) -> int:
        """Import settings from string format."""
        with self._lock:
            try:
                serializer = self._serializers.get(format)
                if serializer is None:
                    raise ValueError(f"No serializer registered for format: {format}")
                
                imported_settings = serializer.deserialize(data)
                
                if not merge and scope is not None:
                    # Clear existing settings in scope
                    self._settings[scope].clear()
                
                import_count = 0
                for key, value in imported_settings.items():
                    if self.set(key, value, scope, "import"):
                        import_count += 1
                
                self._logger.info(f"Imported {import_count} settings from {format.value} format")
                return import_count
                
            except Exception as e:
                self._logger.error(f"Error importing settings: {e}")
                raise
    
    def add_change_listener(self, listener: ISettingChangeListener) -> None:
        """Add a setting change listener."""
        with self._lock:
            if listener not in self._change_listeners:
                self._change_listeners.append(listener)
                self._logger.debug(f"Added change listener: {listener}")
    
    def remove_change_listener(self, listener: ISettingChangeListener) -> None:
        """Remove a setting change listener."""
        with self._lock:
            if listener in self._change_listeners:
                self._change_listeners.remove(listener)
                self._logger.debug(f"Removed change listener: {listener}")
    
    def get_change_history(self, key: Optional[str] = None, 
                          limit: Optional[int] = None) -> List[SettingChange]:
        """Get setting change history."""
        with self._lock:
            history = self._change_history
            
            if key is not None:
                history = [c for c in history if c.key == key]
            
            # Sort by timestamp (newest first)
            history = sorted(history, key=lambda c: c.timestamp, reverse=True)
            
            if limit is not None:
                history = history[:limit]
            
            return history
    
    def backup(self, scope: Optional[SettingScope] = None) -> str:
        """Create a backup of settings."""
        with self._lock:
            if scope is None:
                # Backup all scopes
                backup_id = f"all_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
                for s in SettingScope:
                    scope_backup_id = self._storage.backup(s)
                    self._logger.info(f"Created backup {scope_backup_id} for scope {s.value}")
            else:
                backup_id = self._storage.backup(scope)
                self._logger.info(f"Created backup {backup_id} for scope {scope.value}")
            
            return backup_id
    
    def restore(self, backup_id: str, scope: Optional[SettingScope] = None) -> bool:
        """Restore settings from backup."""
        with self._lock:
            try:
                if scope is None:
                    # Restore all scopes
                    success = True
                    for s in SettingScope:
                        if not self._storage.restore(s, backup_id):
                            success = False
                            self._logger.error(f"Failed to restore scope {s.value} from backup {backup_id}")
                    
                    if success:
                        self.reload()  # Reload all settings
                        self._logger.info(f"Successfully restored all scopes from backup {backup_id}")
                    
                    return success
                else:
                    success = self._storage.restore(scope, backup_id)
                    if success:
                        self.reload(scope)  # Reload the specific scope
                        self._logger.info(f"Successfully restored scope {scope.value} from backup {backup_id}")
                    else:
                        self._logger.error(f"Failed to restore scope {scope.value} from backup {backup_id}")
                    
                    return success
                    
            except Exception as e:
                self._logger.error(f"Error restoring from backup {backup_id}: {e}")
                return False
    
    def reload(self, scope: Optional[SettingScope] = None) -> None:
        """Reload settings from storage."""
        with self._lock:
            try:
                if scope is None:
                    # Reload all scopes
                    for s in SettingScope:
                        old_settings = self._settings[s].copy()
                        self._settings[s] = self._storage.load(s)
                        
                        # Notify listeners
                        for listener in self._change_listeners:
                            listener.on_settings_loaded(s, self._settings[s])
                        
                        self._logger.debug(f"Reloaded {len(self._settings[s])} settings for scope {s.value}")
                else:
                    old_settings = self._settings[scope].copy()
                    self._settings[scope] = self._storage.load(scope)
                    
                    # Notify listeners
                    for listener in self._change_listeners:
                        listener.on_settings_loaded(scope, self._settings[scope])
                    
                    self._logger.debug(f"Reloaded {len(self._settings[scope])} settings for scope {scope.value}")
                
            except Exception as e:
                self._logger.error(f"Error reloading settings: {e}")
                raise
    
    def save(self, scope: Optional[SettingScope] = None) -> None:
        """Save settings to storage."""
        with self._lock:
            try:
                if scope is None:
                    # Save all scopes
                    for s in SettingScope:
                        self._storage.save(s, self._settings[s])
                        
                        # Notify listeners
                        for listener in self._change_listeners:
                            listener.on_settings_saved(s, self._settings[s])
                        
                        self._logger.debug(f"Saved {len(self._settings[s])} settings for scope {s.value}")
                else:
                    self._storage.save(scope, self._settings[scope])
                    
                    # Notify listeners
                    for listener in self._change_listeners:
                        listener.on_settings_saved(scope, self._settings[scope])
                    
                    self._logger.debug(f"Saved {len(self._settings[scope])} settings for scope {scope.value}")
                
            except Exception as e:
                self._logger.error(f"Error saving settings: {e}")
                raise
    
    def _notify_change_listeners(self, change: SettingChange) -> None:
        """Notify all change listeners of a setting change."""
        for listener in self._change_listeners:
            try:
                listener.on_setting_changed(change)
            except Exception as e:
                self._logger.error(f"Error notifying change listener: {e}")
