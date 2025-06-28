"""
Conflict Resolution Models

Data models for representing and managing conflicts.
"""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from uuid import UUID, uuid4

from .enums import (
    ConflictType, ConflictScope, ResolutionStrategy, 
    ConflictSeverity, ConflictPriority, ConflictSource
)


@dataclass
class ConflictContext:
    """Context information for a conflict."""
    source_component: ConflictSource
    operation_id: Optional[str] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    workspace_path: Optional[Path] = None
    additional_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ConflictItem:
    """Represents an item involved in a conflict."""
    id: str
    name: str
    path: Optional[Path] = None
    size: Optional[int] = None
    modified_date: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __str__(self) -> str:
        return f"{self.name} ({self.id})"


@dataclass
class Conflict:
    """Represents a conflict that needs resolution."""
    id: UUID = field(default_factory=uuid4)
    conflict_type: ConflictType = ConflictType.FILE_EXISTS
    severity: ConflictSeverity = ConflictSeverity.MEDIUM
    priority: ConflictPriority = ConflictPriority.NORMAL
    
    # Conflict details
    title: str = ""
    description: str = ""
    suggested_resolution: Optional[ResolutionStrategy] = None
    
    # Items involved in the conflict
    existing_item: Optional[ConflictItem] = None
    new_item: Optional[ConflictItem] = None
    related_items: List[ConflictItem] = field(default_factory=list)
    
    # Context and metadata
    context: Optional[ConflictContext] = None
    scope: ConflictScope = ConflictScope.OPERATION
    
    # Resolution information
    resolution_strategy: Optional[ResolutionStrategy] = None
    resolution_data: Dict[str, Any] = field(default_factory=dict)
    auto_resolvable: bool = False
    
    # Tracking
    created_date: datetime = field(default_factory=datetime.utcnow)
    resolved_date: Optional[datetime] = None
    is_resolved: bool = False
    
    # Additional data
    extra_data: Dict[str, Any] = field(default_factory=dict)
    
    def __str__(self) -> str:
        return f"{self.conflict_type.value}: {self.title}"


@dataclass
class ResolutionResult:
    """Result of a conflict resolution attempt."""
    conflict_id: UUID
    success: bool
    strategy_used: ResolutionStrategy
    
    # Resolution details
    action_taken: str = ""
    files_affected: List[Path] = field(default_factory=list)
    data_changes: Dict[str, Any] = field(default_factory=dict)
    
    # Error information
    error_message: Optional[str] = None
    warnings: List[str] = field(default_factory=list)
    
    # Performance metrics
    resolution_time_ms: float = 0.0
    resources_used: Dict[str, Any] = field(default_factory=dict)
    
    # Rollback information
    rollback_data: Optional[Dict[str, Any]] = None
    can_rollback: bool = False
    
    # Timestamp
    resolved_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ConflictRule:
    """Rule for automatically resolving specific types of conflicts."""
    id: UUID = field(default_factory=uuid4)
    name: str = ""
    description: str = ""
    
    # Rule conditions
    conflict_types: List[ConflictType] = field(default_factory=list)
    scopes: List[ConflictScope] = field(default_factory=list)
    severity_levels: List[ConflictSeverity] = field(default_factory=list)
    
    # Pattern matching
    path_patterns: List[str] = field(default_factory=list)
    name_patterns: List[str] = field(default_factory=list)
    size_conditions: Dict[str, Any] = field(default_factory=dict)
    
    # Resolution strategy
    strategy: ResolutionStrategy = ResolutionStrategy.PROMPT_USER
    strategy_config: Dict[str, Any] = field(default_factory=dict)
    
    # Rule metadata
    priority: int = 0  # Higher numbers = higher priority
    enabled: bool = True
    created_date: datetime = field(default_factory=datetime.utcnow)
    author: str = ""
    
    # Usage statistics
    usage_count: int = 0
    success_rate: float = 0.0
    last_used: Optional[datetime] = None
    
    def matches_conflict(self, conflict: Conflict) -> bool:
        """Check if this rule applies to the given conflict."""
        # Check conflict type
        if self.conflict_types and conflict.conflict_type not in self.conflict_types:
            return False
        
        # Check scope
        if self.scopes and conflict.scope not in self.scopes:
            return False
        
        # Check severity
        if self.severity_levels and conflict.severity not in self.severity_levels:
            return False
        
        # Check path patterns
        if self.path_patterns and conflict.existing_item and conflict.existing_item.path:
            import fnmatch
            path_str = str(conflict.existing_item.path)
            if not any(fnmatch.fnmatch(path_str, pattern) for pattern in self.path_patterns):
                return False
        
        # Check name patterns
        if self.name_patterns:
            names_to_check = []
            if conflict.existing_item:
                names_to_check.append(conflict.existing_item.name)
            if conflict.new_item:
                names_to_check.append(conflict.new_item.name)
            
            if names_to_check:
                import fnmatch
                match_found = False
                for name in names_to_check:
                    if any(fnmatch.fnmatch(name, pattern) for pattern in self.name_patterns):
                        match_found = True
                        break
                if not match_found:
                    return False
        
        return True


@dataclass
class ConflictPreferences:
    """User or system preferences for conflict resolution."""
    scope: ConflictScope
    
    # Default strategies for different conflict types
    default_strategies: Dict[ConflictType, ResolutionStrategy] = field(default_factory=dict)
    
    # Auto-resolution preferences
    auto_resolve_low_severity: bool = True
    auto_resolve_medium_severity: bool = False
    auto_resolve_high_severity: bool = False
    
    # Backup preferences
    always_backup_before_overwrite: bool = True
    backup_retention_days: int = 30
    
    # Notification preferences
    notify_on_conflict: bool = True
    notify_on_resolution: bool = False
    
    # Custom rules
    custom_rules: List[ConflictRule] = field(default_factory=list)
    rule_priorities: Dict[UUID, int] = field(default_factory=dict)
    
    # Metadata
    created_date: datetime = field(default_factory=datetime.utcnow)
    modified_date: datetime = field(default_factory=datetime.utcnow)
    version: int = 1
