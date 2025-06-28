"""
Conflict Resolution Enums

Defines all enumeration types for the conflict resolution system.
"""

from enum import Enum


class ConflictType(Enum):
    """Types of conflicts that can occur."""
    FILE_EXISTS = "file_exists"
    DUPLICATE_NAME = "duplicate_name"
    VERSION_MISMATCH = "version_mismatch"
    PERMISSION_DENIED = "permission_denied"
    PATTERN_OVERLAP = "pattern_overlap"
    RULE_CONFLICT = "rule_conflict"
    DEPENDENCY_CONFLICT = "dependency_conflict"
    DATA_INCONSISTENCY = "data_inconsistency"
    CONCURRENT_MODIFICATION = "concurrent_modification"
    SCHEMA_MISMATCH = "schema_mismatch"


class ConflictScope(Enum):
    """Scope levels where conflicts can be resolved."""
    GLOBAL = "global"           # System-wide defaults
    RULESET = "ruleset"         # Ruleset-specific settings
    RULE = "rule"               # Individual rule settings
    PATTERN = "pattern"         # Pattern-specific settings
    OPERATION = "operation"     # Single operation override


class ResolutionStrategy(Enum):
    """Available conflict resolution strategies."""
    SKIP = "skip"                       # Skip conflicting item
    OVERWRITE = "overwrite"             # Replace existing item
    RENAME = "rename"                   # Auto-rename to avoid conflict
    BACKUP_AND_REPLACE = "backup_replace"  # Backup existing, then replace
    MERGE = "merge"                     # Attempt to merge items
    PROMPT_USER = "prompt_user"         # Ask user for decision
    USE_NEWER = "use_newer"             # Use the newer version
    USE_LARGER = "use_larger"           # Use the larger file
    CUSTOM = "custom"                   # Custom strategy implementation


class ConflictSeverity(Enum):
    """Severity levels for conflicts."""
    LOW = "low"                 # Can be auto-resolved safely
    MEDIUM = "medium"           # Requires some consideration
    HIGH = "high"               # Needs careful attention
    CRITICAL = "critical"       # Must be manually resolved


class ConflictPriority(Enum):
    """Priority for conflict resolution order."""
    IMMEDIATE = "immediate"     # Resolve immediately
    HIGH = "high"              # Resolve before other operations
    NORMAL = "normal"          # Standard priority
    LOW = "low"                # Can be deferred
    BACKGROUND = "background"  # Resolve in background


class ConflictSource(Enum):
    """Source components that can generate conflicts."""
    PATTERN_SYSTEM = "pattern_system"
    RULE_ENGINE = "rule_engine"
    FILE_OPERATIONS = "file_operations"
    DATA_STORAGE = "data_storage"
    USER_INTERFACE = "user_interface"
    EXTERNAL_SYSTEM = "external_system"
