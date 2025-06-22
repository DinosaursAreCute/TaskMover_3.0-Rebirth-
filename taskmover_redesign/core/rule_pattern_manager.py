"""
Rule-Pattern Integration Manager for TaskMover
Manages the relationship between rules and patterns.
"""

import logging
from typing import List, Dict, Any, Tuple, Optional
from .pattern_library import PatternLibrary
from .ruleset_manager import RulesetManager


class RulePatternManager:
    """Manages the integration between rules and patterns."""
    
    def __init__(self, ruleset_manager: RulesetManager, pattern_library: PatternLibrary):
        self.ruleset_manager = ruleset_manager
        self.pattern_library = pattern_library
        self.logger = logging.getLogger(__name__)
    
    def get_pattern_usage(self, pattern_id: str) -> List[Dict[str, str]]:
        """Get all rules using this pattern across all rulesets.
        
        Returns:
            List of dicts with 'ruleset', 'rule_name' keys
        """
        usage = []
        
        try:
            for ruleset_data in self.ruleset_manager.get_available_rulesets():
                ruleset_name = ruleset_data['name']
                rules = self.ruleset_manager.load_ruleset_rules(ruleset_name)
                
                for rule_name, rule_data in rules.items():
                    pattern_ids = rule_data.get('pattern_ids', [])
                    if pattern_id in pattern_ids:
                        usage.append({
                            'ruleset': ruleset_name,
                            'rule_name': rule_name
                        })
        except Exception as e:
            self.logger.error(f"Error checking pattern usage: {e}")
        
        return usage
    
    def can_delete_pattern(self, pattern_id: str) -> Tuple[bool, List[Dict[str, str]]]:
        """Check if pattern can be safely deleted.
        
        Returns:
            (can_delete, usage_list)
        """
        usage = self.get_pattern_usage(pattern_id)
        return len(usage) == 0, usage
    
    def remove_pattern_from_rules(self, pattern_id: str) -> int:
        """Remove pattern from all rules that use it.
        
        Returns:
            Number of rules modified
        """
        modified_count = 0
        
        try:
            for ruleset_data in self.ruleset_manager.get_available_rulesets():
                ruleset_name = ruleset_data['name']
                rules = self.ruleset_manager.load_ruleset_rules(ruleset_name)
                modified = False
                
                for rule_name, rule_data in rules.items():
                    pattern_ids = rule_data.get('pattern_ids', [])
                    if pattern_id in pattern_ids:
                        pattern_ids.remove(pattern_id)
                        rule_data['pattern_ids'] = pattern_ids
                        modified = True
                        modified_count += 1
                
                if modified:
                    self.ruleset_manager.save_ruleset_rules(ruleset_name, rules)
                    
        except Exception as e:
            self.logger.error(f"Error removing pattern from rules: {e}")
        
        return modified_count
    
    def get_rule_patterns(self, ruleset_name: str, rule_name: str) -> List[Dict[str, Any]]:
        """Get all patterns used by a specific rule.
        
        Returns:
            List of pattern data dicts
        """
        patterns = []
        
        try:
            rules = self.ruleset_manager.load_ruleset_rules(ruleset_name)
            rule_data = rules.get(rule_name, {})
            pattern_ids = rule_data.get('pattern_ids', [])
            
            for pattern_id in pattern_ids:
                pattern = self.pattern_library.get_pattern(pattern_id)
                if pattern:
                    patterns.append({
                        'id': pattern.id,
                        'name': pattern.name,
                        'pattern': pattern.pattern,
                        'type': pattern.type,
                        'description': pattern.description
                    })
        except Exception as e:
            self.logger.error(f"Error getting rule patterns: {e}")
        
        return patterns
    
    def update_rule_patterns(self, ruleset_name: str, rule_name: str, 
                           pattern_ids: List[str]) -> bool:
        """Update the patterns used by a specific rule.
        
        Args:
            ruleset_name: Name of the ruleset
            rule_name: Name of the rule
            pattern_ids: List of pattern IDs to assign to the rule
            
        Returns:
            True if successful
        """
        try:
            rules = self.ruleset_manager.load_ruleset_rules(ruleset_name)
            
            if rule_name not in rules:
                return False
            
            # Validate that all pattern IDs exist
            for pattern_id in pattern_ids:
                if not self.pattern_library.get_pattern(pattern_id):
                    raise ValueError(f"Pattern ID {pattern_id} does not exist")
            
            rules[rule_name]['pattern_ids'] = pattern_ids
            return self.ruleset_manager.save_ruleset_rules(ruleset_name, rules)
            
        except Exception as e:
            self.logger.error(f"Error updating rule patterns: {e}")
            return False
    
    def test_rule_patterns(self, ruleset_name: str, rule_name: str, 
                          test_filenames: List[str]) -> Dict[str, List[str]]:
        """Test all patterns in a rule against a list of filenames.
        
        Returns:
            Dict mapping pattern names to lists of matching filenames
        """
        results = {}
        
        try:
            patterns = self.get_rule_patterns(ruleset_name, rule_name)
            
            for pattern_data in patterns:
                matches = self.pattern_library.test_pattern(
                    pattern_data['id'], 
                    test_filenames
                )
                results[pattern_data['name']] = matches
                
        except Exception as e:
            self.logger.error(f"Error testing rule patterns: {e}")
        
        return results
    
    def validate_rule_patterns(self, pattern_ids: List[str]) -> Tuple[bool, List[str]]:
        """Validate that all pattern IDs exist and are valid.
        
        Returns:
            (is_valid, error_messages)
        """
        errors = []
        
        if not pattern_ids:
            errors.append("At least one pattern is required")
            return False, errors
        
        for pattern_id in pattern_ids:
            pattern = self.pattern_library.get_pattern(pattern_id)
            if not pattern:
                errors.append(f"Pattern ID {pattern_id} does not exist")
            else:
                # Validate the pattern syntax
                is_valid, error_msg = self.pattern_library.validate_pattern(
                    pattern.pattern, pattern.type
                )
                if not is_valid:
                    errors.append(f"Pattern '{pattern.name}': {error_msg}")
        
        return len(errors) == 0, errors
    
    def get_unused_patterns(self) -> List[str]:
        """Get list of pattern IDs that are not used by any rule.
        
        Returns:
            List of unused pattern IDs
        """
        all_pattern_ids = set(self.pattern_library.patterns.keys())
        used_pattern_ids = set()
        
        try:
            for ruleset_data in self.ruleset_manager.get_available_rulesets():
                ruleset_name = ruleset_data['name']
                rules = self.ruleset_manager.load_ruleset_rules(ruleset_name)
                
                for rule_data in rules.values():
                    pattern_ids = rule_data.get('pattern_ids', [])
                    used_pattern_ids.update(pattern_ids)
                    
        except Exception as e:
            self.logger.error(f"Error finding unused patterns: {e}")
        
        return list(all_pattern_ids - used_pattern_ids)
    
    def cleanup_orphaned_patterns(self) -> int:
        """Remove patterns that are not used by any rule.
        
        Returns:
            Number of patterns removed
        """
        unused_patterns = self.get_unused_patterns()
        removed_count = 0
        
        for pattern_id in unused_patterns:
            if self.pattern_library.delete_pattern(pattern_id):
                removed_count += 1
        
        if removed_count > 0:
            self.logger.info(f"Cleaned up {removed_count} orphaned patterns")
        
        return removed_count
    
    def migrate_legacy_patterns(self, ruleset_name: str) -> int:
        """Migrate legacy 'patterns' list to pattern IDs for a ruleset.
        
        This is used to convert old rule format to new format.
        
        Returns:
            Number of rules migrated
        """
        migrated_count = 0
        
        try:
            rules = self.ruleset_manager.load_ruleset_rules(ruleset_name)
            modified = False
            
            for rule_name, rule_data in rules.items():
                # Check if rule uses legacy 'patterns' list
                if 'patterns' in rule_data and 'pattern_ids' not in rule_data:
                    legacy_patterns = rule_data.get('patterns', [])
                    pattern_ids = []
                    
                    # Convert each legacy pattern to a pattern object
                    for pattern_str in legacy_patterns:
                        # Create a pattern in the library
                        pattern_name = f"{rule_name} - {pattern_str}"
                        try:
                            # Determine pattern type (simple heuristic)
                            if '*' in pattern_str or '?' in pattern_str:
                                pattern_type = 'glob'
                            elif pattern_str.startswith('^') or pattern_str.endswith('$'):
                                pattern_type = 'regex'
                            else:
                                pattern_type = 'glob'  # Default to glob
                            
                            pattern_id = self.pattern_library.create_pattern(
                                name=pattern_name,
                                pattern=pattern_str,
                                pattern_type=pattern_type,
                                description=f"Migrated from rule '{rule_name}'",
                                tags=['migrated']
                            )
                            pattern_ids.append(pattern_id)
                            
                        except Exception as e:
                            self.logger.warning(f"Failed to migrate pattern '{pattern_str}': {e}")
                    
                    # Update rule to use pattern IDs
                    rule_data['pattern_ids'] = pattern_ids
                    del rule_data['patterns']  # Remove legacy field
                    modified = True
                    migrated_count += 1
            
            if modified:
                self.ruleset_manager.save_ruleset_rules(ruleset_name, rules)
                
        except Exception as e:
            self.logger.error(f"Error migrating legacy patterns: {e}")
        
        return migrated_count
