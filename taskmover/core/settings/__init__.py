"""
Settings Management Module

Provides comprehensive settings management for TaskMover including user preferences,
application configuration, and rule system settings with validation, serialization,
and change tracking.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Type, TypeVar, Union, Callable
import datetime


T = TypeVar("T")


class SettingScope(Enum):
    """Settings scope enumeration"""
    USER = "user"
    APPLICATION = "application"
    SYSTEM = "system"
    RULE = "rule"
    UI = "ui"
    LOGGING = "logging"


class SettingFormat(Enum):
    """Settings serialization format"""
    YAML = "yaml"
    JSON = "json"
    INI = "ini"
    XML = "xml"


class SettingType(Enum):
    """Setting value types"""
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    LIST = "list"
    DICT = "dict"
    PATH = "path"
    COLOR = "color"
    ENUM = "enum"


@dataclass
class SettingDefinition:
    """Definition of a setting including metadata and validation"""
    key: str
    name: str
    description: str
    type: SettingType
    default_value: Any
    scope: SettingScope
    required: bool = False
    min_value: Optional[Union[int, float]] = None
    max_value: Optional[Union[int, float]] = None
    allowed_values: Optional[List[Any]] = None
    pattern: Optional[str] = None
    validator: Optional[Callable[[Any], bool]] = None
    dependencies: List[str] = field(default_factory=list)
    category: str = "General"
    subcategory: Optional[str] = None
    help_text: Optional[str] = None
    sensitive: bool = False  # For passwords, tokens, etc.
    restart_required: bool = False
    version_added: Optional[str] = None
    deprecated: bool = False
    deprecated_message: Optional[str] = None


@dataclass
class SettingChange:
    """Record of a setting change"""
    key: str
    old_value: Any
    new_value: Any
    timestamp: datetime.datetime
    user: Optional[str] = None
    source: Optional[str] = None  # UI, API, config file, etc.
    reason: Optional[str] = None


@dataclass
class SettingValidationResult:
    """Result of setting validation"""
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    normalized_value: Optional[Any] = None


class ISettingValidator(ABC):
    """Interface for setting validators"""
    
    @abstractmethod
    def validate(self, definition: SettingDefinition, value: Any) -> SettingValidationResult:
        """Validate a setting value against its definition"""
        pass


class ISettingSerializer(ABC):
    """Interface for setting serialization"""
    
    @abstractmethod
    def serialize(self, settings: Dict[str, Any]) -> str:
        """Serialize settings to string format"""
        pass
    
    @abstractmethod
    def deserialize(self, data: str) -> Dict[str, Any]:
        """Deserialize settings from string format"""
        pass
    
    @abstractmethod
    def get_file_extension(self) -> str:
        """Get the file extension for this format"""
        pass


class ISettingStorage(ABC):
    """Interface for setting storage backends"""
    
    @abstractmethod
    def load(self, scope: SettingScope) -> Dict[str, Any]:
        """Load settings for a specific scope"""
        pass
    
    @abstractmethod
    def save(self, scope: SettingScope, settings: Dict[str, Any]) -> None:
        """Save settings for a specific scope"""
        pass
    
    @abstractmethod
    def delete(self, scope: SettingScope, key: str) -> bool:
        """Delete a specific setting"""
        pass
    
    @abstractmethod
    def exists(self, scope: SettingScope, key: str) -> bool:
        """Check if a setting exists"""
        pass
    
    @abstractmethod
    def backup(self, scope: SettingScope) -> str:
        """Create a backup of settings and return backup identifier"""
        pass
    
    @abstractmethod
    def restore(self, scope: SettingScope, backup_id: str) -> bool:
        """Restore settings from backup"""
        pass


class ISettingChangeListener(ABC):
    """Interface for setting change listeners"""
    
    @abstractmethod
    def on_setting_changed(self, change: SettingChange) -> None:
        """Called when a setting changes"""
        pass
    
    @abstractmethod
    def on_settings_loaded(self, scope: SettingScope, settings: Dict[str, Any]) -> None:
        """Called when settings are loaded"""
        pass
    
    @abstractmethod
    def on_settings_saved(self, scope: SettingScope, settings: Dict[str, Any]) -> None:
        """Called when settings are saved"""
        pass


class ISettingManager(ABC):
    """Main interface for settings management"""
    
    @abstractmethod
    def get(self, key: str, default: Optional[T] = None, scope: Optional[SettingScope] = None) -> T:
        """Get a setting value"""
        pass
    
    @abstractmethod
    def set(self, key: str, value: Any, scope: Optional[SettingScope] = None, 
            source: Optional[str] = None) -> bool:
        """Set a setting value"""
        pass
    
    @abstractmethod
    def delete(self, key: str, scope: Optional[SettingScope] = None) -> bool:
        """Delete a setting"""
        pass
    
    @abstractmethod
    def exists(self, key: str, scope: Optional[SettingScope] = None) -> bool:
        """Check if a setting exists"""
        pass
    
    @abstractmethod
    def get_all(self, scope: Optional[SettingScope] = None) -> Dict[str, Any]:
        """Get all settings for a scope"""
        pass
    
    @abstractmethod
    def register_definition(self, definition: SettingDefinition) -> None:
        """Register a setting definition"""
        pass
    
    @abstractmethod
    def get_definition(self, key: str) -> Optional[SettingDefinition]:
        """Get a setting definition"""
        pass
    
    @abstractmethod
    def get_definitions(self, scope: Optional[SettingScope] = None, 
                       category: Optional[str] = None) -> List[SettingDefinition]:
        """Get setting definitions"""
        pass
    
    @abstractmethod
    def validate(self, key: str, value: Any) -> SettingValidationResult:
        """Validate a setting value"""
        pass
    
    @abstractmethod
    def reset(self, key: str, scope: Optional[SettingScope] = None) -> bool:
        """Reset a setting to its default value"""
        pass
    
    @abstractmethod
    def reset_all(self, scope: Optional[SettingScope] = None) -> int:
        """Reset all settings in a scope to defaults"""
        pass
    
    @abstractmethod
    def export_settings(self, scope: Optional[SettingScope] = None, 
                       format: SettingFormat = SettingFormat.YAML) -> str:
        """Export settings to string format"""
        pass
    
    @abstractmethod
    def import_settings(self, data: str, scope: Optional[SettingScope] = None,
                       format: SettingFormat = SettingFormat.YAML,
                       merge: bool = True) -> int:
        """Import settings from string format"""
        pass
    
    @abstractmethod
    def add_change_listener(self, listener: ISettingChangeListener) -> None:
        """Add a setting change listener"""
        pass
    
    @abstractmethod
    def remove_change_listener(self, listener: ISettingChangeListener) -> None:
        """Remove a setting change listener"""
        pass
    
    @abstractmethod
    def get_change_history(self, key: Optional[str] = None, 
                          limit: Optional[int] = None) -> List[SettingChange]:
        """Get setting change history"""
        pass
    
    @abstractmethod
    def backup(self, scope: Optional[SettingScope] = None) -> str:
        """Create a backup of settings"""
        pass
    
    @abstractmethod
    def restore(self, backup_id: str, scope: Optional[SettingScope] = None) -> bool:
        """Restore settings from backup"""
        pass
    
    @abstractmethod
    def reload(self, scope: Optional[SettingScope] = None) -> None:
        """Reload settings from storage"""
        pass
    
    @abstractmethod
    def save(self, scope: Optional[SettingScope] = None) -> None:
        """Save settings to storage"""
        pass


# Import concrete implementations
from .manager import SettingManager
from .validator import SettingValidator, BasicSettingValidator
from .storage import FileSettingStorage, MemorySettingStorage
from .serializers import (
    YamlSettingSerializer,
    JsonSettingSerializer,
    IniSettingSerializer,
    XmlSettingSerializer,
    SettingSerializerFactory,
)
from .definitions import (
    get_user_setting_definitions,
    get_application_setting_definitions,
    get_logging_setting_definitions,
    get_rule_setting_definitions,
    get_ui_setting_definitions,
    get_all_setting_definitions,
    register_all_definitions,
)


__all__ = [
    # Enums and data classes
    "SettingScope",
    "SettingFormat", 
    "SettingType",
    "SettingDefinition",
    "SettingChange",
    "SettingValidationResult",
    
    # Interfaces
    "ISettingValidator",
    "ISettingSerializer", 
    "ISettingStorage",
    "ISettingChangeListener",
    "ISettingManager",
    
    # Implementations
    "SettingManager",
    "SettingValidator",
    "BasicSettingValidator",
    "FileSettingStorage",
    "MemorySettingStorage",
    "YamlSettingSerializer",
    "JsonSettingSerializer",
    "IniSettingSerializer",
    "XmlSettingSerializer",
    "SettingSerializerFactory",
    
    # Predefined definitions
    "get_user_setting_definitions",
    "get_application_setting_definitions",
    "get_logging_setting_definitions",
    "get_rule_setting_definitions",
    "get_ui_setting_definitions",
    "get_all_setting_definitions",
    "register_all_definitions",
]