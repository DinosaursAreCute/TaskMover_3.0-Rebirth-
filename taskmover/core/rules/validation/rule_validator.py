"""
Rule Validator

Comprehensive validation logic for rules including pattern conflicts,
priority analysis, and reachability detection.
"""

from pathlib import Path
from typing import List, Dict, Set, Tuple, Optional
from uuid import UUID

from ...patterns.interfaces import BasePatternComponent
from ...patterns import PatternSystem
from ..models import Rule, RuleValidationResult, RuleConflictInfo
from ..exceptions import RuleValidationError


class RuleValidator(BasePatternComponent):
    """
    Validates rules for correctness and detects conflicts.
    
    Provides comprehensive validation including pattern conflicts,
    priority issues, and reachability analysis.
    """
    
    def __init__(self, pattern_system: PatternSystem):
        super().__init__("rule_validator")
        self._pattern_system = pattern_system
        
        self._logger.info("RuleValidator initialized")
    
    def validate_rule(self, rule: Rule) -> RuleValidationResult:
        """
        Validate a single rule for correctness.
        
        Args:
            rule: Rule to validate
            
        Returns:
            RuleValidationResult with validation details
        """
        try:
            self._log_operation("validate_rule", rule_id=str(rule.id), rule_name=rule.name)
            
            result = RuleValidationResult(rule_id=rule.id, is_valid=True)
            
            # Basic rule validation
            basic_errors = rule.validate()
            for error in basic_errors:
                result.add_error(error)
            
            # Pattern existence validation
            if rule.pattern_id:
                pattern = self._pattern_system.get_pattern(rule.pattern_id)
                if not pattern:
                    result.add_error(f"Referenced pattern {rule.pattern_id} does not exist")
                elif not pattern.is_valid:
                    result.add_warning(f"Referenced pattern '{pattern.name}' has validation errors")
            
            # Destination path validation
            if rule.destination_path:
                if not rule.destination_path.exists():
                    result.add_error(f"Destination directory does not exist: {rule.destination_path}")
                elif not rule.destination_path.is_dir():
                    result.add_error(f"Destination path is not a directory: {rule.destination_path}")
                else:
                    # Check if destination is writable
                    try:
                        test_file = rule.destination_path / ".write_test"
                        test_file.touch()
                        test_file.unlink()
                    except Exception:
                        result.add_warning(f"Destination directory may not be writable: {rule.destination_path}")
            
            self._logger.info(f"Rule validation completed: {rule.name} - Valid: {result.is_valid}")
            
            return result
            
        except Exception as e:
            self._log_error(e, "validate_rule", rule_id=str(rule.id))
            result = RuleValidationResult(rule_id=rule.id, is_valid=False)
            result.add_error(f"Validation failed: {e}")
            return result
    
    def detect_rule_conflicts(self, rules: List[Rule]) -> List[RuleConflictInfo]:
        """
        Detect conflicts between multiple rules.
        
        Args:
            rules: List of rules to analyze
            
        Returns:
            List of detected conflicts
        """
        try:
            self._log_operation("detect_rule_conflicts", rules_count=len(rules))
            
            conflicts = []
            active_rules = [rule for rule in rules if rule.is_enabled]
            
            # Detect same pattern conflicts
            pattern_conflicts = self._detect_pattern_conflicts(active_rules)
            conflicts.extend(pattern_conflicts)
            
            # Detect same priority conflicts  
            priority_conflicts = self._detect_priority_conflicts(active_rules)
            conflicts.extend(priority_conflicts)
            
            # Detect unreachable rules
            unreachable_conflicts = self._detect_unreachable_rules(active_rules)
            conflicts.extend(unreachable_conflicts)
            
            self._logger.info(f"Detected {len(conflicts)} rule conflicts")
            
            return conflicts
            
        except Exception as e:
            self._log_error(e, "detect_rule_conflicts")
            return []
    
    def _detect_pattern_conflicts(self, rules: List[Rule]) -> List[RuleConflictInfo]:
        """Detect rules that use the same pattern."""
        conflicts = []
        
        # Group rules by pattern_id
        pattern_groups: Dict[UUID, List[Rule]] = {}
        for rule in rules:
            if rule.pattern_id not in pattern_groups:
                pattern_groups[rule.pattern_id] = []
            pattern_groups[rule.pattern_id].append(rule)
        
        # Find conflicts (multiple rules with same pattern)
        for pattern_id, rules_with_pattern in pattern_groups.items():
            if len(rules_with_pattern) > 1:
                # Get pattern name for better messaging
                pattern = self._pattern_system.get_pattern(pattern_id)
                pattern_name = pattern.name if pattern else str(pattern_id)
                
                for rule in rules_with_pattern:
                    other_rules = [r.id for r in rules_with_pattern if r.id != rule.id]
                    
                    conflicts.append(RuleConflictInfo(
                        rule_id=rule.id,
                        conflicting_rules=other_rules,
                        conflict_type="same_pattern",
                        severity="warning",
                        message=f"Rule '{rule.name}' shares pattern '{pattern_name}' with {len(other_rules)} other rule(s)"
                    ))
        
        return conflicts
    
    def _detect_priority_conflicts(self, rules: List[Rule]) -> List[RuleConflictInfo]:
        """Detect rules with same priority that use same pattern."""
        conflicts = []
        
        # Group by priority and pattern
        priority_pattern_groups: Dict[Tuple[int, UUID], List[Rule]] = {}
        
        for rule in rules:
            key = (rule.priority, rule.pattern_id)
            if key not in priority_pattern_groups:
                priority_pattern_groups[key] = []
            priority_pattern_groups[key].append(rule)
        
        # Find conflicts (multiple rules with same priority and pattern)
        for (priority, pattern_id), rules_group in priority_pattern_groups.items():
            if len(rules_group) > 1:
                pattern = self._pattern_system.get_pattern(pattern_id)
                pattern_name = pattern.name if pattern else str(pattern_id)
                
                for rule in rules_group:
                    other_rules = [r.id for r in rules_group if r.id != rule.id]
                    
                    conflicts.append(RuleConflictInfo(
                        rule_id=rule.id,
                        conflicting_rules=other_rules,
                        conflict_type="same_priority",
                        severity="error",
                        message=f"Rule '{rule.name}' has same priority ({priority}) as other rules using pattern '{pattern_name}' - requires manual resolution"
                    ))
        
        return conflicts
    
    def _detect_unreachable_rules(self, rules: List[Rule]) -> List[RuleConflictInfo]:
        """Detect rules that can never execute due to higher priority rules."""
        conflicts = []
        
        # Group rules by pattern and sort by priority
        pattern_groups: Dict[UUID, List[Rule]] = {}
        for rule in rules:
            if rule.pattern_id not in pattern_groups:
                pattern_groups[rule.pattern_id] = []
            pattern_groups[rule.pattern_id].append(rule)
        
        # Sort each group by priority (highest first)
        for pattern_id, rules_group in pattern_groups.items():
            rules_group.sort(key=lambda r: -r.priority)
            
            # Check if lower priority rules are unreachable
            if len(rules_group) > 1:
                highest_priority = rules_group[0].priority
                
                for i, rule in enumerate(rules_group[1:], 1):
                    if rule.priority < highest_priority:
                        # This rule might be unreachable
                        higher_priority_rules = [r.id for r in rules_group[:i]]
                        
                        pattern = self._pattern_system.get_pattern(pattern_id)
                        pattern_name = pattern.name if pattern else str(pattern_id)
                        
                        conflicts.append(RuleConflictInfo(
                            rule_id=rule.id,
                            conflicting_rules=higher_priority_rules,
                            conflict_type="unreachable",
                            severity="warning",
                            message=f"Rule '{rule.name}' (priority {rule.priority}) may be unreachable due to higher priority rules using pattern '{pattern_name}'"
                        ))
        
        return conflicts
    
    def analyze_rule_execution_order(self, rules: List[Rule]) -> List[Tuple[Rule, int, str]]:
        """
        Analyze the execution order of rules.
        
        Args:
            rules: List of rules to analyze
            
        Returns:
            List of tuples (rule, execution_order, status)
            where status is "will_execute", "may_conflict", or "unreachable"
        """
        try:
            active_rules = [rule for rule in rules if rule.is_enabled]
            
            # Sort by priority (highest first), then by name for consistency
            sorted_rules = sorted(active_rules, key=lambda r: (-r.priority, r.name))
            
            analysis = []
            seen_patterns: Set[UUID] = set()
            
            for i, rule in enumerate(sorted_rules):
                if rule.pattern_id in seen_patterns:
                    # Pattern already handled by higher priority rule
                    status = "may_conflict"
                else:
                    seen_patterns.add(rule.pattern_id)
                    status = "will_execute"
                
                analysis.append((rule, i + 1, status))
            
            self._log_operation("analyze_execution_order", 
                              rules_count=len(active_rules),
                              unique_patterns=len(seen_patterns))
            
            return analysis
            
        except Exception as e:
            self._log_error(e, "analyze_execution_order")
            return []
    
    def validate_destination_paths(self, rules: List[Rule]) -> Dict[UUID, List[str]]:
        """
        Validate destination paths for all rules.
        
        Args:
            rules: List of rules to validate
            
        Returns:
            Dictionary mapping rule IDs to list of validation errors
        """
        try:
            validation_results = {}
            
            for rule in rules:
                errors = []
                
                if not rule.destination_path:
                    errors.append("No destination path specified")
                else:
                    dest_path = rule.destination_path
                    
                    if not dest_path.exists():
                        errors.append(f"Destination does not exist: {dest_path}")
                    elif not dest_path.is_dir():
                        errors.append(f"Destination is not a directory: {dest_path}")
                    else:
                        # Check permissions
                        try:
                            test_file = dest_path / ".write_test"
                            test_file.touch()
                            test_file.unlink()
                        except PermissionError:
                            errors.append(f"No write permission: {dest_path}")
                        except Exception as e:
                            errors.append(f"Cannot write to destination: {e}")
                
                if errors:
                    validation_results[rule.id] = errors
            
            self._log_operation("validate_destination_paths",
                              rules_count=len(rules),
                              invalid_count=len(validation_results))
            
            return validation_results
            
        except Exception as e:
            self._log_error(e, "validate_destination_paths")
            return {}
