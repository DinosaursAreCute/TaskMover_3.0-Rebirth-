"""
Rule management for TaskMover Redesigned.
Streamlined and more maintainable rule operations.
"""

import uuid
import logging
from typing import Dict, Any, List, Optional, Tuple
from .config import ConfigManager

logger = logging.getLogger("TaskMover.Rules")


class RuleManager:
    """Centralized rule management with CRUD operations."""
    
    def __init__(self, config_manager: ConfigManager):
        self.config = config_manager
        self._rules = self.config.load_rules()
    
    @property
    def rules(self) -> Dict[str, Any]:
        """Get current rules."""
        return self._rules
    
    def reload_rules(self) -> None:
        """Reload rules from disk."""
        self._rules = self.config.load_rules()
        logger.info("Rules reloaded from disk")
    
    def save_rules(self) -> bool:
        """Save current rules to disk."""
        success = self.config.save_rules(self._rules)
        if success:
            logger.info("Rules saved successfully")
        return success
    
    def get_sorted_rule_keys(self) -> List[str]:
        """Get rule keys sorted by priority."""
        return sorted(self._rules.keys(), key=lambda k: self._rules[k].get('priority', 0))
    
    def add_rule(self, name: str, patterns: Optional[List[str]] = None, path: str = "", 
                 active: bool = True, unzip: bool = False) -> bool:
        """Add a new rule with automatic priority assignment."""
        if name in self._rules:
            logger.warning(f"Rule '{name}' already exists")
            return False
        
        if patterns is None:
            patterns = []
        
        # Get next available priority
        max_priority = max((rule.get('priority', 0) for rule in self._rules.values()), default=-1)
        
        self._rules[name] = {
            "patterns": patterns or [],
            "path": path,
            "active": active,
            "unzip": unzip,
            "priority": max_priority + 1,
            "id": str(uuid.uuid4())
        }
        
        logger.info(f"Added rule '{name}' with priority {max_priority + 1}")
        return self.save_rules()
    
    def update_rule(self, name: str, **kwargs) -> bool:
        """Update an existing rule with new values."""
        if name not in self._rules:
            logger.warning(f"Rule '{name}' does not exist")
            return False
        
        old_values = self._rules[name].copy()
        
        # Update provided fields
        for key, value in kwargs.items():
            if key in ['patterns', 'path', 'active', 'unzip', 'priority']:
                self._rules[name][key] = value
        
        logger.info(f"Updated rule '{name}': {kwargs}")
        return self.save_rules()
    
    def delete_rule(self, name: str) -> bool:
        """Delete a rule and reorder priorities."""
        if name not in self._rules:
            logger.warning(f"Rule '{name}' does not exist")
            return False
        
        deleted_priority = self._rules[name].get('priority', 0)
        del self._rules[name]
        
        # Reorder priorities to fill the gap
        self._reorder_priorities_after_deletion(deleted_priority)
        
        logger.info(f"Deleted rule '{name}'")
        return self.save_rules()
    
    def rename_rule(self, old_name: str, new_name: str) -> bool:
        """Rename a rule while preserving all properties."""
        if old_name not in self._rules:
            logger.warning(f"Rule '{old_name}' does not exist")
            return False
        
        if new_name in self._rules:
            logger.warning(f"Rule '{new_name}' already exists")
            return False
        
        # Copy rule data to new name
        self._rules[new_name] = self._rules[old_name].copy()
        del self._rules[old_name]
        
        logger.info(f"Renamed rule '{old_name}' to '{new_name}'")
        return self.save_rules()
    
    def duplicate_rule(self, name: str, new_name: Optional[str] = None) -> bool:
        """Duplicate an existing rule with a new name."""
        if name not in self._rules:
            logger.warning(f"Rule '{name}' does not exist")
            return False
        
        # Generate new name if not provided
        if not new_name:
            counter = 1
            while f"{name} (Copy {counter})" in self._rules:
                counter += 1
            new_name = f"{name} (Copy {counter})"
        
        if new_name in self._rules:
            logger.warning(f"Rule '{new_name}' already exists")
            return False
        
        # Copy rule data
        rule_copy = self._rules[name].copy()
        rule_copy['id'] = str(uuid.uuid4())
        
        # Assign new priority
        max_priority = max((rule.get('priority', 0) for rule in self._rules.values()), default=-1)
        rule_copy['priority'] = max_priority + 1
        
        self._rules[new_name] = rule_copy
        
        logger.info(f"Duplicated rule '{name}' as '{new_name}'")
        return self.save_rules()
    
    def move_rule_priority(self, name: str, direction: int) -> bool:
        """Move rule up (-1) or down (+1) in priority."""
        if name not in self._rules:
            logger.warning(f"Rule '{name}' does not exist")
            return False
        
        current_priority = self._rules[name].get('priority', 0)
        new_priority = current_priority + direction
        
        # Find rule at target priority
        target_rule = None
        for rule_name, rule_data in self._rules.items():
            if rule_data.get('priority', 0) == new_priority:
                target_rule = rule_name
                break
        
        if target_rule:
            # Swap priorities
            self._rules[name]['priority'] = new_priority
            self._rules[target_rule]['priority'] = current_priority
            
            logger.info(f"Swapped priorities: '{name}' ({current_priority} → {new_priority}), "
                       f"'{target_rule}' ({new_priority} → {current_priority})")
            return self.save_rules()
        
        return False
    
    def toggle_rule_active(self, name: str, active: Optional[bool] = None) -> bool:
        """Toggle or set the active state of a rule."""
        if name not in self._rules:
            logger.warning(f"Rule '{name}' does not exist")
            return False
        
        if active is None:
            active = not self._rules[name].get('active', True)
        
        self._rules[name]['active'] = active
        logger.info(f"Rule '{name}' {'activated' if active else 'deactivated'}")
        return self.save_rules()
    
    def enable_all_rules(self) -> bool:
        """Enable all rules."""
        count = 0
        for rule_data in self._rules.values():
            if not rule_data.get('active', True):
                rule_data['active'] = True
                count += 1
        
        logger.info(f"Enabled {count} rules")
        return self.save_rules()
    
    def disable_all_rules(self) -> bool:
        """Disable all rules."""
        count = 0
        for rule_data in self._rules.values():
            if rule_data.get('active', True):
                rule_data['active'] = False
                count += 1
        
        logger.info(f"Disabled {count} rules")
        return self.save_rules()
    
    def get_active_rules(self) -> Dict[str, Any]:
        """Get only the active rules."""
        return {name: rule for name, rule in self._rules.items() 
                if rule.get('active', True)}
    
    def get_rule_stats(self) -> Dict[str, int]:
        """Get statistics about the rules."""
        total = len(self._rules)
        active = len(self.get_active_rules())
        return {
            'total': total,
            'active': active,
            'inactive': total - active
        }
    
    def validate_rule(self, rule_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate a rule and return errors if any."""
        errors = []
        
        if not rule_data.get('patterns'):
            errors.append("Rule must have at least one pattern")
        
        if not rule_data.get('path'):
            errors.append("Rule must have a destination path")
        
        # Check if path exists and is writable
        import os
        path = rule_data.get('path', '')
        if path and not os.path.exists(path):
            errors.append(f"Destination path does not exist: {path}")
        
        return len(errors) == 0, errors
    
    def _reorder_priorities_after_deletion(self, deleted_priority: int) -> None:
        """Reorder rule priorities after a deletion to maintain sequence."""
        for rule_data in self._rules.values():
            if rule_data.get('priority', 0) > deleted_priority:
                rule_data['priority'] -= 1


# Backward compatibility functions
def get_sorted_rule_keys(rules: Dict[str, Any]) -> List[str]:
    """Legacy function for backward compatibility."""
    return sorted(rules.keys(), key=lambda k: rules[k].get('priority', 0))


def move_rule_priority(rules: Dict[str, Any], rule_name: str, direction: int) -> bool:
    """Legacy function for backward compatibility."""
    # This is a simplified version for compatibility
    current_priority = rules[rule_name].get('priority', 0)
    new_priority = current_priority + direction
    
    # Find rule at target priority
    for name, rule_data in rules.items():
        if rule_data.get('priority', 0) == new_priority:
            # Swap priorities
            rules[rule_name]['priority'] = new_priority
            rule_data['priority'] = current_priority
            return True
    
    return False
