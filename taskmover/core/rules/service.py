"""
Rule Service

Main service for managing and executing file organization rules.
Integrates with pattern system and conflict resolution.
"""

import shutil
import time
from pathlib import Path
from typing import List, Optional, Dict, Any, Tuple
from uuid import UUID

from ..patterns.interfaces import BasePatternComponent
from ..patterns import PatternSystem
from ..conflict_resolution import ConflictManager, ConflictType, ConflictScope, ConflictContext
from ..conflict_resolution.models import ConflictItem
from ..conflict_resolution.enums import ConflictSource
from .models import Rule, RuleExecutionResult, RuleConflictInfo, RuleValidationResult, RuleStatus, ErrorHandlingBehavior, FileOperationResult
from .storage import RuleRepository
from .validation import RuleValidator
from .exceptions import RuleSystemError, RuleNotFoundError, RuleValidationError, RuleExecutionError, DestinationNotFoundError


class RuleService(BasePatternComponent):
    """
    Service for managing and executing file organization rules.
    
    Provides CRUD operations for rules and execution with conflict resolution.
    Integrates with existing PatternSystem and ConflictManager.
    """
    
    def __init__(self, 
                 pattern_system: PatternSystem,
                 conflict_manager: ConflictManager,
                 storage_path: Path):
        super().__init__("rule_service")
        
        self._pattern_system = pattern_system
        self._conflict_manager = conflict_manager
        self._repository = RuleRepository(storage_path)
        self._validator = RuleValidator(pattern_system)
        
        # Default error handling behavior (user configurable)
        self._default_error_handling = ErrorHandlingBehavior.CONTINUE_ON_RECOVERABLE
        
        self._logger.info("RuleService initialized")
    
    # CRUD Operations
    
    def create_rule(self, 
                   name: str,
                   pattern_id: UUID,
                   destination_path: Path,
                   description: str = "",
                   priority: int = 0,
                   is_enabled: bool = True,
                   error_handling: Optional[ErrorHandlingBehavior] = None,
                   **kwargs) -> Rule:
        """
        Create a new rule.
        
        Args:
            name: Rule name
            pattern_id: ID of existing pattern to use
            destination_path: Where to move matching files
            description: Optional rule description
            priority: Rule priority (higher = executes first)
            is_enabled: Whether rule is active
            error_handling: How to handle errors during execution
            **kwargs: Additional rule properties
            
        Returns:
            Created Rule object
            
        Raises:
            RuleValidationError: If rule validation fails
            RuleSystemError: If creation fails
        """
        try:
            self._log_operation("create_rule", name=name, pattern_id=str(pattern_id))
            
            # Ensure destination_path is Path object
            if isinstance(destination_path, str):
                destination_path = Path(destination_path)
            
            # Create rule object
            rule = Rule(
                name=name,
                description=description,
                pattern_id=pattern_id,
                destination_path=destination_path,
                priority=priority,
                is_enabled=is_enabled,
                error_handling=error_handling or self._default_error_handling,
                **kwargs
            )
            
            # Validate the rule
            validation_result = self._validator.validate_rule(rule)
            if not validation_result.is_valid:
                raise RuleValidationError(
                    f"Rule validation failed: {'; '.join(validation_result.errors)}",
                    rule_id=rule.id,
                    errors=validation_result.errors
                )
            
            # Save to repository
            self._repository.save(rule)
            
            self._logger.info(f"Created rule: {rule.name} ({rule.id})")
            
            return rule
            
        except RuleValidationError:
            raise
        except Exception as e:
            self._log_error(e, "create_rule", name=name, pattern_id=str(pattern_id))
            raise RuleSystemError(f"Failed to create rule: {e}")
    
    def get_rule(self, rule_id: UUID) -> Optional[Rule]:
        """
        Retrieve a rule by ID.
        
        Args:
            rule_id: UUID of the rule
            
        Returns:
            Rule if found, None otherwise
        """
        try:
            return self._repository.get(rule_id)
        except Exception as e:
            self._log_error(e, "get_rule", rule_id=str(rule_id))
            return None
    
    def update_rule(self, rule: Rule) -> None:
        """
        Update an existing rule.
        
        Args:
            rule: Rule object to update
            
        Raises:
            RuleNotFoundError: If rule doesn't exist
            RuleValidationError: If updated rule is invalid
            RuleSystemError: If update fails
        """
        try:
            self._log_operation("update_rule", rule_id=str(rule.id), rule_name=rule.name)
            
            # Check if rule exists
            existing = self._repository.get(rule.id)
            if not existing:
                raise RuleNotFoundError(rule.id)
            
            # Validate the updated rule
            validation_result = self._validator.validate_rule(rule)
            if not validation_result.is_valid:
                raise RuleValidationError(
                    f"Rule validation failed: {'; '.join(validation_result.errors)}",
                    rule_id=rule.id,
                    errors=validation_result.errors
                )
            
            # Update in repository
            self._repository.save(rule)
            
            self._logger.info(f"Updated rule: {rule.name} ({rule.id})")
            
        except (RuleNotFoundError, RuleValidationError):
            raise
        except Exception as e:
            self._log_error(e, "update_rule", rule_id=str(rule.id))
            raise RuleSystemError(f"Failed to update rule: {e}")
    
    def delete_rule(self, rule_id: UUID) -> bool:
        """
        Delete a rule.
        
        Args:
            rule_id: UUID of the rule to delete
            
        Returns:
            True if rule was deleted, False if not found
        """
        try:
            self._log_operation("delete_rule", rule_id=str(rule_id))
            
            success = self._repository.delete(rule_id)
            
            if success:
                self._logger.info(f"Deleted rule: {rule_id}")
            
            return success
            
        except Exception as e:
            self._log_error(e, "delete_rule", rule_id=str(rule_id))
            return False
    
    def list_rules(self, active_only: bool = False) -> List[Rule]:
        """
        List rules with optional filtering.
        
        Args:
            active_only: If True, only return enabled rules
            
        Returns:
            List of rules
        """
        try:
            return self._repository.list_rules(active_only=active_only)
        except Exception as e:
            self._log_error(e, "list_rules", active_only=active_only)
            return []
    
    def search_rules(self, query: str) -> List[Rule]:
        """
        Search rules by text query.
        
        Args:
            query: Search query string
            
        Returns:
            List of rules matching the query
        """
        try:
            return self._repository.search_rules(query)
        except Exception as e:
            self._log_error(e, "search_rules", query=query)
            return []
    
    # Execution Operations
    
    def execute_rule(self, 
                    rule_id: UUID, 
                    source_directory: Path,
                    dry_run: bool = False) -> RuleExecutionResult:
        """
        Execute a single rule against a source directory.
        
        Args:
            rule_id: ID of rule to execute
            source_directory: Directory to scan for files
            dry_run: If True, simulate execution without moving files
            
        Returns:
            RuleExecutionResult with execution details
            
        Raises:
            RuleNotFoundError: If rule doesn't exist
            RuleExecutionError: If execution fails
        """
        try:
            self._log_operation("execute_rule", 
                              rule_id=str(rule_id),
                              source_directory=str(source_directory),
                              dry_run=dry_run)
            
            # Get and validate rule
            rule = self._repository.get(rule_id)
            if not rule:
                raise RuleNotFoundError(rule_id)
            
            if not rule.is_enabled:
                raise RuleExecutionError(f"Rule '{rule.name}' is disabled", rule_id)
            
            # Validate destination exists
            if not rule.destination_path.exists():
                raise DestinationNotFoundError(str(rule.destination_path), rule_id)
            
            # Create execution result
            result = RuleExecutionResult(
                rule_id=rule.id,
                rule_name=rule.name,
                status=RuleStatus.RUNNING,
                dry_run=dry_run
            )
            
            start_time = time.perf_counter()
            
            try:
                # Get pattern and find matching files
                pattern = self._pattern_system.get_pattern(rule.pattern_id)
                if not pattern:
                    result.add_error(f"Pattern {rule.pattern_id} not found")
                    result.complete(success=False)
                    return result
                
                # Scan source directory for files
                file_paths = list(source_directory.rglob("*"))
                file_paths = [p for p in file_paths if p.is_file()]  # Only files, not directories
                
                # Match files against pattern
                match_result = self._pattern_system.match_pattern(pattern, file_paths)
                result.matched_files = match_result.matched_files
                
                if not result.matched_files:
                    result.add_warning("No files matched the pattern")
                    result.complete(success=True)
                    return result
                
                # Execute file operations
                for file_path in result.matched_files:
                    operation_result = self._execute_file_move(
                        file_path, 
                        rule.destination_path, 
                        dry_run,
                        rule.error_handling
                    )
                    result.add_file_operation(operation_result)
                    
                    # Check if we should continue on error
                    if not operation_result.success:
                        if rule.error_handling == ErrorHandlingBehavior.STOP_ON_FIRST_ERROR:
                            result.add_error("Stopping execution due to error handling policy")
                            break
                
                # Update rule statistics
                if not dry_run:
                    rule.update_execution_stats(result.files_moved)
                    self._repository.save(rule)
                
                # Complete execution
                result.complete(success=True)
                
                # Calculate execution time
                execution_time = (time.perf_counter() - start_time) * 1000
                result.execution_time_ms = execution_time
                
                self._log_performance("execute_rule", execution_time,
                                    rule_name=rule.name,
                                    files_matched=len(result.matched_files),
                                    files_moved=result.files_moved,
                                    dry_run=dry_run)
                
                return result
                
            except Exception as e:
                result.add_error(f"Execution failed: {e}")
                result.complete(success=False)
                raise RuleExecutionError(f"Rule execution failed: {e}", rule_id)
                
        except (RuleNotFoundError, RuleExecutionError, DestinationNotFoundError):
            raise
        except Exception as e:
            self._log_error(e, "execute_rule", rule_id=str(rule_id))
            raise RuleExecutionError(f"Rule execution failed: {e}", rule_id)
    
    def execute_multiple_rules(self, 
                              rule_ids: List[UUID],
                              source_directory: Path,
                              dry_run: bool = False) -> List[RuleExecutionResult]:
        """
        Execute multiple rules against a source directory.
        
        Args:
            rule_ids: List of rule IDs to execute
            source_directory: Directory to scan for files
            dry_run: If True, simulate execution without moving files
            
        Returns:
            List of RuleExecutionResult objects
        """
        try:
            self._log_operation("execute_multiple_rules",
                              rule_count=len(rule_ids),
                              source_directory=str(source_directory),
                              dry_run=dry_run)
            
            results = []
            
            # Get all rules and sort by priority
            rules = []
            for rule_id in rule_ids:
                rule = self._repository.get(rule_id)
                if rule and rule.is_enabled:
                    rules.append(rule)
                elif rule:
                    result = RuleExecutionResult(
                        rule_id=rule_id,
                        rule_name=rule.name,
                        status=RuleStatus.FAILED,
                        dry_run=dry_run
                    )
                    result.add_error("Rule is disabled")
                    results.append(result)
                else:
                    result = RuleExecutionResult(
                        rule_id=rule_id,
                        rule_name="Unknown",
                        status=RuleStatus.FAILED,
                        dry_run=dry_run
                    )
                    result.add_error("Rule not found")
                    results.append(result)
            
            # Sort by priority (highest first)
            rules.sort(key=lambda r: -r.priority)
            
            # Execute rules in priority order
            for rule in rules:
                try:
                    result = self.execute_rule(rule.id, source_directory, dry_run)
                    results.append(result)
                except Exception as e:
                    result = RuleExecutionResult(
                        rule_id=rule.id,
                        rule_name=rule.name,
                        status=RuleStatus.FAILED,
                        dry_run=dry_run
                    )
                    result.add_error(str(e))
                    results.append(result)
            
            self._logger.info(f"Executed {len(results)} rules")
            
            return results
            
        except Exception as e:
            self._log_error(e, "execute_multiple_rules")
            return []
    
    def _execute_file_move(self, 
                          source_path: Path,
                          destination_dir: Path,
                          dry_run: bool,
                          error_handling: ErrorHandlingBehavior) -> FileOperationResult:
        """Execute a single file move operation with conflict resolution."""
        try:
            destination_path = destination_dir / source_path.name
            
            operation = FileOperationResult(
                source_path=source_path,
                destination_path=destination_path,
                operation_type="move"
            )
            
            if dry_run:
                # Simulate the operation
                if destination_path.exists():
                    operation.error_message = f"Conflict: {destination_path.name} already exists"
                else:
                    operation.success = True
                return operation
            
            # Check for conflicts
            if destination_path.exists():
                # Use conflict resolution
                conflict_result = self._resolve_file_conflict(source_path, destination_path)
                
                if conflict_result['resolved']:
                    destination_path = Path(conflict_result['final_destination'])
                    operation.destination_path = destination_path
                else:
                    operation.error_message = conflict_result['error']
                    return operation
            
            # Perform the move
            try:
                shutil.move(str(source_path), str(destination_path))
                operation.success = True
                operation.destination_path = destination_path
                
            except Exception as e:
                operation.error_message = f"Move failed: {e}"
            
            return operation
            
        except Exception as e:
            return FileOperationResult(
                source_path=source_path,
                success=False,
                error_message=f"Operation failed: {e}"
            )
    
    def _resolve_file_conflict(self, source_path: Path, destination_path: Path) -> Dict[str, Any]:
        """Resolve file conflict using conflict manager."""
        try:
            # Create conflict items
            existing_item = ConflictItem(
                id=str(destination_path),
                name=destination_path.name,
                metadata={
                    "size": destination_path.stat().st_size,
                    "modified": destination_path.stat().st_mtime
                }
            )
            
            new_item = ConflictItem(
                id=str(source_path),
                name=source_path.name,
                metadata={
                    "size": source_path.stat().st_size,
                    "modified": source_path.stat().st_mtime
                }
            )
            
            context = ConflictContext(
                source_component=ConflictSource.RULE_ENGINE,
                additional_data={
                    "source_path": str(source_path),
                    "destination_path": str(destination_path)
                }
            )
            
            # Detect conflict
            conflict = self._conflict_manager.detect_conflict(
                ConflictType.FILE_EXISTS,
                existing_item=existing_item,
                new_item=new_item,
                context=context,
                scope=ConflictScope.RULE
            )
            
            if not conflict:
                return {"resolved": False, "error": "Could not create conflict"}
            
            # Resolve conflict
            resolution = self._conflict_manager.resolve_conflict(conflict)
            
            if resolution.success:
                # Apply resolution strategy
                final_destination = self._apply_conflict_resolution(
                    source_path, 
                    destination_path, 
                    resolution.strategy_used
                )
                
                return {
                    "resolved": True,
                    "final_destination": final_destination,
                    "strategy": resolution.strategy_used.value if resolution.strategy_used else None
                }
            else:
                return {"resolved": False, "error": "Conflict resolution failed"}
                
        except Exception as e:
            return {"resolved": False, "error": f"Conflict resolution error: {e}"}
    
    def _apply_conflict_resolution(self, source_path: Path, destination_path: Path, strategy) -> str:
        """Apply conflict resolution strategy and return final destination."""
        from ..conflict_resolution.enums import ResolutionStrategy
        
        if strategy == ResolutionStrategy.RENAME:
            # Generate unique name
            counter = 1
            base_name = destination_path.stem
            extension = destination_path.suffix
            parent = destination_path.parent
            
            while True:
                new_name = f"{base_name}_{counter}{extension}"
                new_destination = parent / new_name
                if not new_destination.exists():
                    return str(new_destination)
                counter += 1
                
        elif strategy == ResolutionStrategy.OVERWRITE:
            return str(destination_path)
            
        elif strategy == ResolutionStrategy.SKIP:
            # Don't move the file
            raise Exception("File skipped due to conflict")
            
        else:
            # Default to rename
            return self._apply_conflict_resolution(source_path, destination_path, ResolutionStrategy.RENAME)
    
    # Validation & Conflict Detection
    
    def validate_rule(self, rule: Rule) -> RuleValidationResult:
        """
        Validate a rule for correctness.
        
        Args:
            rule: Rule to validate
            
        Returns:
            RuleValidationResult with validation details
        """
        try:
            return self._validator.validate_rule(rule)
        except Exception as e:
            self._log_error(e, "validate_rule", rule_id=str(rule.id))
            result = RuleValidationResult(rule_id=rule.id, is_valid=False)
            result.add_error(f"Validation failed: {e}")
            return result
    
    def detect_rule_conflicts(self, rules: Optional[List[Rule]] = None) -> List[RuleConflictInfo]:
        """
        Detect conflicts between rules.
        
        Args:
            rules: Optional list of rules to check. If None, checks all rules.
            
        Returns:
            List of detected conflicts
        """
        try:
            if rules is None:
                rules = self._repository.list_rules()
            
            return self._validator.detect_rule_conflicts(rules)
            
        except Exception as e:
            self._log_error(e, "detect_rule_conflicts")
            return []
    
    def get_rules_by_pattern(self, pattern_id: UUID) -> List[Rule]:
        """
        Get all rules that use a specific pattern.
        
        Args:
            pattern_id: UUID of the pattern
            
        Returns:
            List of rules using the pattern
        """
        try:
            return self._repository.get_rules_by_pattern(pattern_id)
        except Exception as e:
            self._log_error(e, "get_rules_by_pattern", pattern_id=str(pattern_id))
            return []
    
    # Settings
    
    def set_default_error_handling(self, behavior: ErrorHandlingBehavior) -> None:
        """Set default error handling behavior for new rules."""
        self._default_error_handling = behavior
        self._logger.info(f"Set default error handling to: {behavior.value}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get service statistics."""
        try:
            repo_stats = self._repository.get_statistics()
            
            return {
                **repo_stats,
                'default_error_handling': self._default_error_handling.value,
                'service_status': 'active'
            }
            
        except Exception as e:
            self._log_error(e, "get_statistics")
            return {}
