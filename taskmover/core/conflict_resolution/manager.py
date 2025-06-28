"""
Conflict Resolution Manager

Main manager class that coordinates conflict detection, resolution,
and strategy application across all scopes.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
from uuid import UUID

from ..logging import get_logger
from .models import (
    Conflict, ConflictRule, ConflictPreferences, ResolutionResult,
    ConflictContext, ConflictItem
)
from .enums import ConflictScope, ConflictType, ResolutionStrategy, ConflictSeverity
from .resolver import ConflictResolver
from .strategies import (
    SkipStrategy, OverwriteStrategy, RenameStrategy,
    BackupStrategy, PromptUserStrategy, MergeStrategy
)


class ConflictManager:
    """
    Central manager for conflict resolution across all TaskMover components.
    
    Manages resolution preferences at different scopes (global, ruleset, rule, pattern)
    and coordinates strategy selection and execution.
    """
    
    def __init__(self, storage_path: Optional[Path] = None):
        self._logger = get_logger("conflict_manager")
        self._storage_path = storage_path or Path.cwd() / "conflicts"
        
        # Resolution components
        self._resolver = ConflictResolver()
        self._register_default_strategies()
        
        # Preferences by scope
        self._preferences: Dict[ConflictScope, ConflictPreferences] = {}
        self._scope_rules: Dict[ConflictScope, Dict[UUID, ConflictRule]] = {
            scope: {} for scope in ConflictScope
        }
        
        # Active conflicts
        self._active_conflicts: Dict[UUID, Conflict] = {}
        self._resolved_conflicts: List[Conflict] = []
        
        # Load existing preferences and rules
        self._load_preferences()
        
        self._logger.info("ConflictManager initialized")
    
    def _register_default_strategies(self):
        """Register default conflict resolution strategies."""
        strategies = [
            SkipStrategy(),
            OverwriteStrategy(),
            RenameStrategy(),
            BackupStrategy(),
            PromptUserStrategy(),
            MergeStrategy()
        ]
        
        for strategy in strategies:
            self._resolver.register_strategy(strategy)
    
    def set_preferences(self, scope: ConflictScope, preferences: ConflictPreferences) -> None:
        """Set conflict resolution preferences for a specific scope."""
        self._logger.info(f"Setting preferences for scope: {scope.value}")
        preferences.scope = scope
        self._preferences[scope] = preferences
        self._save_preferences(scope)
    
    def get_preferences(self, scope: ConflictScope) -> ConflictPreferences:
        """Get conflict resolution preferences for a scope."""
        if scope not in self._preferences:
            # Create default preferences for the scope
            self._preferences[scope] = self._create_default_preferences(scope)
        
        return self._preferences[scope]
    
    def add_rule(self, scope: ConflictScope, rule: ConflictRule) -> None:
        """Add a conflict resolution rule for a specific scope."""
        self._logger.info(f"Adding rule '{rule.name}' to scope: {scope.value}")
        self._scope_rules[scope][rule.id] = rule
        self._save_rules(scope)
    
    def remove_rule(self, scope: ConflictScope, rule_id: UUID) -> bool:
        """Remove a conflict resolution rule."""
        if rule_id in self._scope_rules[scope]:
            rule = self._scope_rules[scope][rule_id]
            self._logger.info(f"Removing rule '{rule.name}' from scope: {scope.value}")
            del self._scope_rules[scope][rule_id]
            self._save_rules(scope)
            return True
        return False
    
    def get_rules(self, scope: ConflictScope) -> List[ConflictRule]:
        """Get all rules for a specific scope."""
        return list(self._scope_rules[scope].values())
    
    def detect_conflict(self, 
                       conflict_type: ConflictType,
                       existing_item: Optional[ConflictItem] = None,
                       new_item: Optional[ConflictItem] = None,
                       context: Optional[ConflictContext] = None,
                       scope: ConflictScope = ConflictScope.OPERATION) -> Optional[Conflict]:
        """Detect and create a conflict object."""
        try:
            conflict = Conflict(
                conflict_type=conflict_type,
                existing_item=existing_item,
                new_item=new_item,
                context=context,
                scope=scope,
                title=self._generate_conflict_title(conflict_type, existing_item, new_item),
                description=self._generate_conflict_description(conflict_type, existing_item, new_item)
            )
            
            # Determine severity
            conflict.severity = self._assess_conflict_severity(conflict)
            
            # Find applicable rules and suggest resolution
            applicable_rules = self._find_applicable_rules(conflict)
            if applicable_rules:
                best_rule = max(applicable_rules, key=lambda r: r.priority)
                conflict.suggested_resolution = best_rule.strategy
                conflict.auto_resolvable = self._can_auto_resolve(conflict, best_rule)
            else:
                # Use default strategy from preferences
                preferences = self._get_effective_preferences(scope)
                conflict.suggested_resolution = preferences.default_strategies.get(
                    conflict_type, ResolutionStrategy.PROMPT_USER
                )
            
            self._active_conflicts[conflict.id] = conflict
            
            self._logger.info(f"Detected conflict: {conflict.title}")
            return conflict
            
        except Exception as e:
            self._logger.error(f"Failed to detect conflict: {e}")
            return None
    
    def resolve_conflict(self, 
                        conflict: Conflict,
                        strategy: Optional[ResolutionStrategy] = None,
                        config: Optional[Dict] = None) -> ResolutionResult:
        """Resolve a specific conflict."""
        try:
            # Use provided strategy or suggested strategy
            resolution_strategy = strategy or conflict.suggested_resolution or ResolutionStrategy.PROMPT_USER
            
            self._logger.info(f"Resolving conflict {conflict.id} with strategy: {resolution_strategy.value}")
            
            # Execute resolution
            result = self._resolver.resolve(conflict, resolution_strategy, config or {})
            
            # Update conflict status
            if result.success:
                conflict.is_resolved = True
                conflict.resolved_date = result.resolved_at
                conflict.resolution_strategy = resolution_strategy
                conflict.resolution_data = result.data_changes
                
                # Move to resolved conflicts
                if conflict.id in self._active_conflicts:
                    del self._active_conflicts[conflict.id]
                self._resolved_conflicts.append(conflict)
                
                # Update rule statistics if applicable
                self._update_rule_statistics(conflict, result)
            
            return result
            
        except Exception as e:
            self._logger.error(f"Failed to resolve conflict {conflict.id}: {e}")
            return ResolutionResult(
                conflict_id=conflict.id,
                success=False,
                strategy_used=strategy or ResolutionStrategy.PROMPT_USER,
                error_message=str(e)
            )
    
    def resolve_all_auto_resolvable(self, scope: Optional[ConflictScope] = None) -> List[ResolutionResult]:
        """Resolve all conflicts that can be automatically resolved."""
        results = []
        conflicts_to_resolve = []
        
        for conflict in self._active_conflicts.values():
            if scope and conflict.scope != scope:
                continue
            
            if conflict.auto_resolvable:
                conflicts_to_resolve.append(conflict)
        
        self._logger.info(f"Auto-resolving {len(conflicts_to_resolve)} conflicts")
        
        for conflict in conflicts_to_resolve:
            result = self.resolve_conflict(conflict)
            results.append(result)
        
        return results
    
    def get_active_conflicts(self, scope: Optional[ConflictScope] = None) -> List[Conflict]:
        """Get all active conflicts, optionally filtered by scope."""
        conflicts = list(self._active_conflicts.values())
        
        if scope:
            conflicts = [c for c in conflicts if c.scope == scope]
        
        return conflicts
    
    def get_conflict_statistics(self) -> Dict[str, Any]:
        """Get statistics about conflicts and resolutions."""
        total_conflicts = len(self._active_conflicts) + len(self._resolved_conflicts)
        resolved_count = len(self._resolved_conflicts)
        
        # Count by type
        type_counts = {}
        severity_counts = {}
        
        all_conflicts = list(self._active_conflicts.values()) + self._resolved_conflicts
        
        for conflict in all_conflicts:
            conflict_type = conflict.conflict_type.value
            severity = conflict.severity.value
            
            type_counts[conflict_type] = type_counts.get(conflict_type, 0) + 1
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        return {
            "total_conflicts": total_conflicts,
            "active_conflicts": len(self._active_conflicts),
            "resolved_conflicts": resolved_count,
            "resolution_rate": resolved_count / total_conflicts if total_conflicts > 0 else 0,
            "conflicts_by_type": type_counts,
            "conflicts_by_severity": severity_counts
        }
    
    def _find_applicable_rules(self, conflict: Conflict) -> List[ConflictRule]:
        """Find all rules that apply to the given conflict."""
        applicable_rules = []
        
        # Check rules from most specific to least specific scope
        scopes_to_check = [conflict.scope]
        
        # Add broader scopes if current scope is more specific
        if conflict.scope == ConflictScope.PATTERN:
            scopes_to_check.extend([ConflictScope.RULE, ConflictScope.RULESET, ConflictScope.GLOBAL])
        elif conflict.scope == ConflictScope.RULE:
            scopes_to_check.extend([ConflictScope.RULESET, ConflictScope.GLOBAL])
        elif conflict.scope == ConflictScope.RULESET:
            scopes_to_check.append(ConflictScope.GLOBAL)
        
        for scope in scopes_to_check:
            for rule in self._scope_rules[scope].values():
                if rule.enabled and rule.matches_conflict(conflict):
                    applicable_rules.append(rule)
        
        # Sort by priority (highest first)
        applicable_rules.sort(key=lambda r: r.priority, reverse=True)
        
        return applicable_rules
    
    def _get_effective_preferences(self, scope: ConflictScope) -> ConflictPreferences:
        """Get effective preferences, falling back to broader scopes if needed."""
        # Try current scope first
        if scope in self._preferences:
            return self._preferences[scope]
        
        # Fall back to broader scopes
        fallback_order = {
            ConflictScope.PATTERN: [ConflictScope.RULE, ConflictScope.RULESET, ConflictScope.GLOBAL],
            ConflictScope.RULE: [ConflictScope.RULESET, ConflictScope.GLOBAL],
            ConflictScope.RULESET: [ConflictScope.GLOBAL],
            ConflictScope.OPERATION: [ConflictScope.GLOBAL]
        }
        
        if scope in fallback_order:
            for fallback_scope in fallback_order[scope]:
                if fallback_scope in self._preferences:
                    return self._preferences[fallback_scope]
        
        # Create and return default global preferences
        if ConflictScope.GLOBAL not in self._preferences:
            self._preferences[ConflictScope.GLOBAL] = self._create_default_preferences(ConflictScope.GLOBAL)
        
        return self._preferences[ConflictScope.GLOBAL]
    
    def _create_default_preferences(self, scope: ConflictScope) -> ConflictPreferences:
        """Create default preferences for a scope."""
        return ConflictPreferences(
            scope=scope,
            default_strategies={
                ConflictType.FILE_EXISTS: ResolutionStrategy.PROMPT_USER,
                ConflictType.DUPLICATE_NAME: ResolutionStrategy.RENAME,
                ConflictType.VERSION_MISMATCH: ResolutionStrategy.BACKUP_AND_REPLACE,
                ConflictType.PERMISSION_DENIED: ResolutionStrategy.SKIP,
                ConflictType.PATTERN_OVERLAP: ResolutionStrategy.PROMPT_USER,
                ConflictType.RULE_CONFLICT: ResolutionStrategy.PROMPT_USER
            }
        )
    
    def _generate_conflict_title(self, conflict_type: ConflictType, 
                                existing_item: Optional[ConflictItem],
                                new_item: Optional[ConflictItem]) -> str:
        """Generate a descriptive title for the conflict."""
        if conflict_type == ConflictType.FILE_EXISTS:
            name = new_item.name if new_item else "file"
            return f"File already exists: {name}"
        elif conflict_type == ConflictType.DUPLICATE_NAME:
            name = new_item.name if new_item else "item"
            return f"Duplicate name: {name}"
        elif conflict_type == ConflictType.PATTERN_OVERLAP:
            return "Pattern overlap detected"
        else:
            return f"{conflict_type.value.replace('_', ' ').title()}"
    
    def _generate_conflict_description(self, conflict_type: ConflictType,
                                     existing_item: Optional[ConflictItem],
                                     new_item: Optional[ConflictItem]) -> str:
        """Generate a detailed description for the conflict."""
        if conflict_type == ConflictType.FILE_EXISTS and existing_item and new_item:
            return (f"Attempting to create '{new_item.name}' but '{existing_item.name}' "
                   f"already exists at the target location.")
        else:
            return f"A {conflict_type.value.replace('_', ' ')} conflict has occurred."
    
    def _assess_conflict_severity(self, conflict: Conflict) -> ConflictSeverity:
        """Assess the severity of a conflict."""
        if conflict.conflict_type in [ConflictType.PERMISSION_DENIED, ConflictType.DATA_INCONSISTENCY]:
            return ConflictSeverity.HIGH
        elif conflict.conflict_type in [ConflictType.FILE_EXISTS, ConflictType.VERSION_MISMATCH]:
            return ConflictSeverity.MEDIUM
        else:
            return ConflictSeverity.LOW
    
    def _can_auto_resolve(self, conflict: Conflict, rule: ConflictRule) -> bool:
        """Determine if a conflict can be automatically resolved."""
        preferences = self._get_effective_preferences(conflict.scope)
        
        if conflict.severity == ConflictSeverity.LOW and preferences.auto_resolve_low_severity:
            return True
        elif conflict.severity == ConflictSeverity.MEDIUM and preferences.auto_resolve_medium_severity:
            return True
        elif conflict.severity == ConflictSeverity.HIGH and preferences.auto_resolve_high_severity:
            return True
        
        return False
    
    def _update_rule_statistics(self, conflict: Conflict, result: ResolutionResult) -> None:
        """Update statistics for rules used in resolution."""
        # Find the rule that was used
        applicable_rules = self._find_applicable_rules(conflict)
        
        for rule in applicable_rules:
            if rule.strategy == result.strategy_used:
                rule.usage_count += 1
                rule.last_used = result.resolved_at
                
                # Update success rate
                if result.success:
                    rule.success_rate = ((rule.success_rate * (rule.usage_count - 1)) + 1.0) / rule.usage_count
                else:
                    rule.success_rate = (rule.success_rate * (rule.usage_count - 1)) / rule.usage_count
                
                break
    
    def _load_preferences(self) -> None:
        """Load preferences from storage."""
        # Placeholder for loading from file/database
        # For now, create default global preferences
        self._preferences[ConflictScope.GLOBAL] = self._create_default_preferences(ConflictScope.GLOBAL)
    
    def _save_preferences(self, scope: ConflictScope) -> None:
        """Save preferences to storage."""
        # Placeholder for saving to file/database
        pass
    
    def _save_rules(self, scope: ConflictScope) -> None:
        """Save rules to storage."""
        # Placeholder for saving to file/database
        pass
