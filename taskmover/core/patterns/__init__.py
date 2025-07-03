"""
Pattern System Main API

Unified API for the TaskMover Pattern System providing high-level
operations and service orchestration.
"""

from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from uuid import UUID
import time

from .interfaces import BasePatternService
from .models import Pattern, PatternGroup, MatchResult, ValidationResult, ParsedPattern
from .exceptions import PatternSystemError, PatternNotFoundError

# Import concrete implementations
from .parsing.intelligent_parser import IntelligentPatternParser
from .parsing.token_resolver import TokenResolver
from .matching.unified_matcher import UnifiedPatternMatcher
from .storage.repository import PatternRepository
from .storage.cache_manager import MultiLevelCacheManager
from .suggestions.suggestion_engine import PatternSuggestionEngine, WorkspaceAnalyzer
from .validation.pattern_validator import PatternValidator
from ..conflict_resolution import ConflictManager


class PatternSystem(BasePatternService):
    """
    Main Pattern System API providing unified access to all pattern operations.
    
    This is the primary interface for pattern management, matching, and analysis
    in the TaskMover application.
    """
    
    def __init__(self, 
                 storage_path: Optional[Path] = None,
                 cache_settings: Optional[Dict[str, Any]] = None):
        # Initialize logging like BasePatternComponent
        from taskmover.core.logging import get_logger
        self._logger = get_logger("patterns.pattern_system")
        self._component_name = "pattern_system"
        
        super().__init__("pattern_system")
        
        # Configuration
        self._storage_path = storage_path or Path.cwd() / "patterns"
        self._cache_settings = cache_settings or {}
        
        # Core components (will be initialized in initialize())
        self._parser: Optional[IntelligentPatternParser] = None
        self._token_resolver: Optional[TokenResolver] = None
        self._matcher: Optional[UnifiedPatternMatcher] = None
        self._repository: Optional[PatternRepository] = None
        self._cache_manager: Optional[MultiLevelCacheManager] = None
        self._suggestion_engine: Optional[PatternSuggestionEngine] = None
        self._workspace_analyzer: Optional[WorkspaceAnalyzer] = None
        self._validator: Optional[PatternValidator] = None
        self._conflict_manager: Optional[ConflictManager] = None
        
        # State
        self._initialized = False
        
        self._logger.info("PatternSystem created")
    
    def _log_operation(self, operation: str, **kwargs) -> None:
        """Log an operation with context."""
        if kwargs:
            extra_info = ", ".join(f"{k}={v}" for k, v in kwargs.items())
            message = f"{self._component_name} operation: {operation} - {extra_info}"
        else:
            message = f"{self._component_name} operation: {operation}"
        self._logger.info(message)
    
    def _log_error(self, error: Exception, operation: str, **kwargs) -> None:
        """Log an error with context."""
        message = f"{self._component_name} error in {operation}: {error}"
        if kwargs:
            extra_info = ", ".join(f"{k}={v}" for k, v in kwargs.items())
            message += f" - {extra_info}"
        self._logger.error(message)
    
    def _log_performance(self, operation: str, duration_ms: float, **kwargs) -> None:
        """Log performance metrics."""
        message = f"{self._component_name} performance: {operation} took {duration_ms:.2f}ms"
        if kwargs:
            extra_info = ", ".join(f"{k}={v}" for k, v in kwargs.items())
            message += f" - {extra_info}"
        self._logger.info(message)
    
    def initialize(self) -> None:
        """Initialize all pattern system components."""
        try:
            self._log_operation("initialize_system")
            
            if self._initialized:
                self._logger.warning("Pattern system already initialized")
                return
            
            # Initialize components in dependency order
            self._initialize_cache_manager()
            self._initialize_conflict_manager()
            self._initialize_token_resolver()
            self._initialize_parser()
            self._initialize_repository()
            self._initialize_matcher()
            self._initialize_workspace_analyzer()
            self._initialize_suggestion_engine()
            self._initialize_validator()
            
            self._initialized = True
            
            self._logger.info("Pattern system initialized successfully")
            
        except Exception as e:
            self._log_error(e, "initialize_system")
            raise PatternSystemError(f"Failed to initialize pattern system: {e}")
    
    def shutdown(self) -> None:
        """Shutdown pattern system and cleanup resources."""
        try:
            self._log_operation("shutdown_system")
            
            if not self._initialized:
                return
            
            # Shutdown components in reverse order
            if self._cache_manager:
                self._cache_manager.shutdown()
            
            self._initialized = False
            
            self._logger.info("Pattern system shutdown complete")
            
        except Exception as e:
            self._log_error(e, "shutdown_system")
    
    # Pattern Management API
    
    def create_pattern(self, 
                      user_expression: str,
                      name: str = "",
                      description: str = "",
                      **kwargs) -> Pattern:
        """
        Create a new pattern from user expression.
        
        Args:
            user_expression: The pattern expression entered by user
            name: Optional pattern name
            description: Optional pattern description
            **kwargs: Additional pattern properties
            
        Returns:
            Created Pattern object
            
        Raises:
            PatternSystemError: If pattern creation fails
        """
        try:
            self._ensure_initialized()
            self._log_operation("create_pattern", expression=user_expression)
            
            # Parse the expression
            if not self._parser:
                raise PatternSystemError("Parser not initialized")
            parsed = self._parser.parse(user_expression)
            
            # Create pattern object
            pattern = Pattern(
                name=name or f"Pattern: {user_expression[:50]}",
                description=description,
                user_expression=user_expression,
                compiled_query=parsed.compiled_query,
                pattern_complexity=parsed.complexity,
                pattern_type=parsed.pattern_type,
                **kwargs
            )
            
            # Validate the pattern
            if not self._validator:
                raise PatternSystemError("Validator not initialized")
            validation_result = self._validator.validate(pattern)
            pattern.is_valid = validation_result.is_valid
            pattern.validation_errors = validation_result.errors
            
            # Save to repository
            if not self._repository:
                raise PatternSystemError("Repository not initialized")
            self._repository.save(pattern)
            
            self._logger.info(f"Created pattern: {pattern.name} ({pattern.id})")
            
            return pattern
            
        except Exception as e:
            self._log_error(e, "create_pattern", expression=user_expression)
            raise PatternSystemError(f"Failed to create pattern: {e}")
    
    def add_pattern(self, pattern: Pattern) -> Pattern:
        """
        Add an existing pattern to the system.
        
        Args:
            pattern: The pattern to add
            
        Returns:
            The added pattern
            
        Raises:
            PatternSystemError: If the operation fails
        """
        try:
            self._log_operation("add_pattern", pattern_id=str(pattern.id), name=pattern.name)
            
            if not self._initialized:
                self.initialize()
            
            # Validate the pattern
            if not self._validator:
                raise PatternSystemError("Validator not initialized")
            validation_result = self._validator.validate(pattern)
            pattern.is_valid = validation_result.is_valid
            pattern.validation_errors = validation_result.errors
            
            # Save to repository
            if not self._repository:
                raise PatternSystemError("Repository not initialized")
            self._repository.save(pattern)
            
            self._logger.info(f"Added pattern: {pattern.name} ({pattern.id})")
            
            return pattern
            
        except Exception as e:
            self._log_error(e, "add_pattern", pattern_id=str(pattern.id))
            raise PatternSystemError(f"Failed to add pattern: {e}")
    
    def get_pattern(self, pattern_id: Union[UUID, str]) -> Optional[Pattern]:
        """
        Retrieve a pattern by ID.
        
        Args:
            pattern_id: UUID or string ID of the pattern
            
        Returns:
            Pattern if found, None otherwise
        """
        try:
            self._ensure_initialized()
            
            if isinstance(pattern_id, str):
                pattern_id = UUID(pattern_id)
            
            return self._repository.get(pattern_id)
            
        except Exception as e:
            self._log_error(e, "get_pattern", pattern_id=str(pattern_id))
            return None
    
    def update_pattern(self, pattern: Pattern) -> None:
        """
        Update an existing pattern.
        
        Args:
            pattern: Pattern object to update
            
        Raises:
            PatternNotFoundError: If pattern doesn't exist
            PatternSystemError: If update fails
        """
        try:
            self._ensure_initialized()
            self._log_operation("update_pattern", pattern_id=str(pattern.id))
            
            # Check if pattern exists
            existing = self._repository.get(pattern.id)
            if not existing:
                raise PatternNotFoundError(f"Pattern {pattern.id} not found", str(pattern.id))
            
            # Re-validate if expression changed
            if pattern.user_expression != existing.user_expression:
                parsed = self._parser.parse(pattern.user_expression)
                pattern.compiled_query = parsed.compiled_query
                pattern.pattern_complexity = parsed.complexity
                pattern.pattern_type = parsed.pattern_type
                
                validation_result = self._validator.validate(pattern)
                pattern.is_valid = validation_result.is_valid
                pattern.validation_errors = validation_result.errors
            
            # Update in repository
            self._repository.save(pattern)
            
            # Clear cache for this pattern
            self._invalidate_pattern_cache(pattern)
            
            self._logger.info(f"Updated pattern: {pattern.name} ({pattern.id})")
            
        except PatternNotFoundError:
            raise
        except Exception as e:
            self._log_error(e, "update_pattern", pattern_id=str(pattern.id))
            raise PatternSystemError(f"Failed to update pattern: {e}")
    
    def delete_pattern(self, pattern_id: Union[UUID, str]) -> bool:
        """
        Delete a pattern.
        
        Args:
            pattern_id: UUID or string ID of the pattern
            
        Returns:
            True if pattern was deleted, False if not found
        """
        try:
            self._ensure_initialized()
            
            if isinstance(pattern_id, str):
                pattern_id = UUID(pattern_id)
            
            success = self._repository.delete(pattern_id)
            
            if success:
                self._logger.info(f"Deleted pattern: {pattern_id}")
            
            return success
            
        except Exception as e:
            self._log_error(e, "delete_pattern", pattern_id=str(pattern_id))
            return False
    
    def list_patterns(self, filters: Optional[Dict[str, Any]] = None) -> List[Pattern]:
        """
        List patterns with optional filtering.
        
        Args:
            filters: Optional filters to apply
            
        Returns:
            List of patterns matching filters
        """
        try:
            self._ensure_initialized()
            return self._repository.list_patterns(filters)
            
        except Exception as e:
            self._log_error(e, "list_patterns")
            return []
    
    def search_patterns(self, query: str) -> List[Pattern]:
        """
        Search patterns by text query.
        
        Args:
            query: Search query string
            
        Returns:
            List of patterns matching the query
        """
        try:
            self._ensure_initialized()
            return self._repository.search_patterns(query)
            
        except Exception as e:
            self._log_error(e, "search_patterns", query=query)
            return []
    
    # Pattern Matching API
    
    def match_pattern(self, 
                     pattern: Union[Pattern, str], 
                     file_paths: List[Path]) -> MatchResult:
        """
        Execute pattern matching against file paths.
        
        Args:
            pattern: Pattern object or expression string
            file_paths: List of file paths to match against
            
        Returns:
            MatchResult with matched files and metadata
        """
        try:
            self._ensure_initialized()
            
            # Convert string to pattern if needed
            if isinstance(pattern, str):
                parsed = self._parser.parse(pattern)
                pattern_obj = Pattern(
                    user_expression=pattern,
                    compiled_query=parsed.compiled_query,
                    pattern_complexity=parsed.complexity,
                    pattern_type=parsed.pattern_type
                )
            else:
                pattern_obj = pattern
            
            return self._matcher.match(pattern_obj, file_paths)
            
        except Exception as e:
            pattern_id = str(pattern.id) if isinstance(pattern, Pattern) else pattern
            self._log_error(e, "match_pattern", pattern_id=pattern_id)
            return MatchResult(matched_files=[], total_files_checked=len(file_paths), execution_time_ms=0.0, errors=[str(e)])
    
    def match_single_file(self, 
                         pattern: Union[Pattern, str], 
                         file_path: Path) -> bool:
        """
        Check if a single file matches a pattern.
        
        Args:
            pattern: Pattern object or pattern string
            file_path: Path to file to check
            
        Returns:
            True if file matches pattern
            
        Raises:
            PatternSystemError: If the operation fails
        """
        try:
            self._log_operation("match_single_file", 
                              pattern_id=str(pattern.id) if isinstance(pattern, Pattern) else pattern,
                              file_path=str(file_path))
            
            if not self._initialized:
                self.initialize()
            
            # Convert to MatchResult and check if file is in results
            result = self.match_pattern(pattern, [file_path])
            return len(result.matched_files) > 0
            
        except Exception as e:
            pattern_id = str(pattern.id) if isinstance(pattern, Pattern) else pattern
            self._log_error(e, "match_single_file", pattern_id=pattern_id, file_path=str(file_path))
            return False
    
    def match_files(self, file_paths: List[Path]) -> List[MatchResult]:
        """
        Match multiple files against all patterns in the system.
        
        Args:
            file_paths: List of file paths to match
            
        Returns:
            List of MatchResult objects for each matching pattern
            
        Raises:
            PatternSystemError: If the operation fails
        """
        try:
            self._log_operation("match_files", file_count=len(file_paths))
            
            if not self._initialized:
                self.initialize()
            
            # Get all active patterns
            patterns = self.list_patterns({"status": "active"})
            results = []
            
            # Match each pattern against the files
            for pattern in patterns:
                result = self.match_pattern(pattern, file_paths)
                if result.matched_files:  # Only include patterns that matched something
                    results.append(result)
            
            return results
            
        except Exception as e:
            self._log_error(e, "match_files", file_count=len(file_paths))
            return []
    
    # Validation API
    
    def validate_pattern(self, pattern: Pattern) -> ValidationResult:
        """
        Validate a pattern.
        
        Args:
            pattern: Pattern to validate
            
        Returns:
            ValidationResult with validation details
        """
        try:
            self._ensure_initialized()
            return self._validator.validate(pattern)
            
        except Exception as e:
            self._log_error(e, "validate_pattern", pattern_id=str(pattern.id))
            return ValidationResult(False, [f"Validation error: {e}"])
    
    def validate_expression(self, expression: str) -> ValidationResult:
        """
        Validate a pattern expression.
        
        Args:
            expression: Pattern expression to validate
            
        Returns:
            ValidationResult with validation details
        """
        try:
            self._ensure_initialized()
            return self._validator.validate_expression(expression)
            
        except Exception as e:
            self._log_error(e, "validate_expression", expression=expression)
            return ValidationResult(False, [f"Validation error: {e}"])
    
    # Suggestion API
    
    def get_pattern_suggestions(self, 
                               workspace_path: Path,
                               partial_input: str = "") -> List[Dict]:
        """
        Get pattern suggestions for a workspace.
        
        Args:
            workspace_path: Path to workspace to analyze
            partial_input: Optional partial user input
            
        Returns:
            List of pattern suggestions
        """
        try:
            self._ensure_initialized()
            return self._suggestion_engine.suggest_patterns(workspace_path, partial_input)
            
        except Exception as e:
            self._log_error(e, "get_pattern_suggestions", workspace_path=str(workspace_path))
            return []
    
    def get_completions(self, partial_input: str) -> List[str]:
        """
        Get auto-completion suggestions.
        
        Args:
            partial_input: Partial pattern input
            
        Returns:
            List of completion strings
        """
        try:
            self._ensure_initialized()
            return self._suggestion_engine.get_completions(partial_input)
            
        except Exception as e:
            self._log_error(e, "get_completions", partial_input=partial_input)
            return []
    
    def analyze_workspace(self, workspace_path: Path) -> Dict:
        """
        Analyze workspace structure and files.
        
        Args:
            workspace_path: Path to workspace to analyze
            
        Returns:
            Dictionary with workspace analysis results
        """
        try:
            self._ensure_initialized()
            return self._workspace_analyzer.analyze(workspace_path)
            
        except Exception as e:
            self._log_error(e, "analyze_workspace", workspace_path=str(workspace_path))
            return {}
    
    # System Management API
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get pattern system status and statistics."""
        try:
            status = {
                'initialized': self._initialized,
                'storage_path': str(self._storage_path),
                'components': {
                    'parser': self._parser is not None,
                    'matcher': self._matcher is not None,
                    'repository': self._repository is not None,
                    'cache_manager': self._cache_manager is not None,
                    'suggestion_engine': self._suggestion_engine is not None,
                    'validator': self._validator is not None
                }
            }
            
            if self._initialized:
                # Add repository statistics
                status['repository_stats'] = self._repository.get_statistics()
                
                # Add cache statistics
                if self._cache_manager:
                    status['cache_stats'] = self._cache_manager.get_stats()
            
            return status
            
        except Exception as e:
            self._log_error(e, "get_system_status")
            return {'error': str(e)}
    
    def clear_cache(self) -> None:
        """Clear all caches."""
        try:
            if self._cache_manager:
                self._cache_manager.clear()
            self._logger.info("Pattern system cache cleared")
            
        except Exception as e:
            self._log_error(e, "clear_cache")
    
    def backup_patterns(self) -> Optional[Path]:
        """Create a backup of all patterns."""
        try:
            self._ensure_initialized()
            return self._repository.backup()
            
        except Exception as e:
            self._log_error(e, "backup_patterns")
            return None
    
    def restore_patterns(self, backup_file: Path) -> bool:
        """Restore patterns from backup."""
        try:
            self._ensure_initialized()
            self._repository.restore(backup_file)
            self.clear_cache()  # Clear cache after restore
            return True
            
        except Exception as e:
            self._log_error(e, "restore_patterns", backup_file=str(backup_file))
            return False
    
    # Private helper methods
    
    def _ensure_initialized(self) -> None:
        """Ensure the system is initialized."""
        if not self._initialized:
            raise PatternSystemError("Pattern system not initialized. Call initialize() first.")
    
    def _initialize_cache_manager(self) -> None:
        """Initialize the cache manager."""
        try:
            cache_config = self._cache_settings.copy()
            cache_config.setdefault('max_memory_entries', 1000)
            cache_config.setdefault('default_ttl_seconds', 300)
            
            self._cache_manager = MultiLevelCacheManager(**cache_config)
        except Exception as e:
            raise PatternSystemError(f"Failed to initialize cache manager: {e}")
    
    def _initialize_conflict_manager(self) -> None:
        """Initialize the conflict resolution manager."""
        try:
            conflict_storage_path = self._storage_path / "conflicts"
            self._conflict_manager = ConflictManager(conflict_storage_path)
        except Exception as e:
            raise PatternSystemError(f"Failed to initialize conflict manager: {e}")
    
    def _initialize_token_resolver(self) -> None:
        """Initialize the token resolver."""
        try:
            self._token_resolver = TokenResolver()
        except Exception as e:
            raise PatternSystemError(f"Failed to initialize token resolver: {e}")
    
    def _initialize_parser(self) -> None:
        """Initialize the intelligent parser."""
        try:
            self._parser = IntelligentPatternParser(self._token_resolver)
        except Exception as e:
            raise PatternSystemError(f"Failed to initialize parser: {e}")
    
    def _initialize_repository(self) -> None:
        """Initialize the pattern repository."""
        try:
            self._repository = PatternRepository(self._storage_path)
        except Exception as e:
            raise PatternSystemError(f"Failed to initialize repository: {e}")
    
    def _initialize_matcher(self) -> None:
        """Initialize the unified matcher."""
        try:
            self._matcher = UnifiedPatternMatcher(
                cache_manager=self._cache_manager,
                conflict_manager=self._conflict_manager
            )
        except Exception as e:
            raise PatternSystemError(f"Failed to initialize matcher: {e}")
    
    def _initialize_workspace_analyzer(self) -> None:
        """Initialize the workspace analyzer."""
        try:
            self._workspace_analyzer = WorkspaceAnalyzer()
        except Exception as e:
            raise PatternSystemError(f"Failed to initialize workspace analyzer: {e}")
    
    def _initialize_suggestion_engine(self) -> None:
        """Initialize the suggestion engine."""
        try:
            self._suggestion_engine = PatternSuggestionEngine(
                workspace_analyzer=self._workspace_analyzer
            )
        except Exception as e:
            raise PatternSystemError(f"Failed to initialize suggestion engine: {e}")
    
    def _initialize_validator(self) -> None:
        """Initialize the pattern validator."""
        try:
            self._validator = PatternValidator(self._parser)
        except Exception as e:
            raise PatternSystemError(f"Failed to initialize validator: {e}")
    
    def _invalidate_pattern_cache(self, pattern: Pattern) -> None:
        """Invalidate cache entries related to a pattern."""
        if self._cache_manager:
            # In a real implementation, this would invalidate specific cache entries
            # For now, we'll clear the entire cache to be safe
            self._cache_manager.clear()
    
    # Conflict Resolution API Methods
    
    def set_conflict_resolution_preferences(self, scope: str, preferences: Dict[str, Any]) -> None:
        """Set conflict resolution preferences for a specific scope."""
        try:
            from ..conflict_resolution.enums import ConflictScope
            from ..conflict_resolution.models import ConflictPreferences
            
            scope_enum = ConflictScope(scope.lower())
            prefs = ConflictPreferences(scope=scope_enum, **preferences)
            
            if self._conflict_manager:
                self._conflict_manager.set_preferences(scope_enum, prefs)
            
        except Exception as e:
            self._log_error(e, "set_conflict_preferences", scope=scope)
            raise PatternSystemError(f"Failed to set conflict preferences: {e}")
    
    def detect_pattern_conflicts(self, patterns: List[Pattern], file_paths: List[Path]) -> Dict[str, Any]:
        """Detect conflicts between multiple patterns."""
        try:
            if not self._matcher:
                raise PatternSystemError("Pattern system not initialized")
            
            return self._matcher.handle_pattern_conflicts(patterns, file_paths)
            
        except Exception as e:
            self._log_error(e, "detect_pattern_conflicts")
            raise PatternSystemError(f"Failed to detect pattern conflicts: {e}")
    
    def get_conflict_statistics(self) -> Dict[str, Any]:
        """Get conflict resolution statistics."""
        try:
            if self._conflict_manager:
                return self._conflict_manager.get_conflict_statistics()
            else:
                return {"error": "Conflict manager not initialized"}
                
        except Exception as e:
            self._log_error(e, "get_conflict_statistics")
            return {"error": str(e)}


def create_pattern_system(storage_path: Optional[Path] = None, 
                         cache_settings: Optional[Dict[str, Any]] = None) -> PatternSystem:
    """
    Create and return a new PatternSystem instance.
    
    Args:
        storage_path: Optional storage path for patterns
        cache_settings: Optional cache configuration
        
    Returns:
        PatternSystem instance ready for initialization
    """
    return PatternSystem(storage_path, cache_settings)
