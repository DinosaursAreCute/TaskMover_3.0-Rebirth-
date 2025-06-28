"""
Pattern System Exceptions

Comprehensive exception hierarchy for the unified pattern system,
providing detailed error information for debugging and user feedback.
"""

from typing import Any, Optional


class PatternSystemError(Exception):
    """Base exception for all pattern system errors."""
    
    def __init__(self, message: str, component: str = "pattern_system", **kwargs):
        super().__init__(message)
        self.message = message
        self.component = component
        self.extra_data = kwargs


class PatternValidationError(PatternSystemError):
    """Raised when pattern validation fails."""
    
    def __init__(self, message: str, pattern: str, validation_errors: list[str], **kwargs):
        super().__init__(message, component="pattern_validator", **kwargs)
        self.pattern = pattern
        self.validation_errors = validation_errors


class PatternParsingError(PatternSystemError):
    """Raised when pattern parsing fails."""
    
    def __init__(self, message: str, user_input: str, position: Optional[int] = None, **kwargs):
        super().__init__(message, component="pattern_parser", **kwargs)
        self.user_input = user_input
        self.position = position


class QuerySyntaxError(PatternParsingError):
    """Raised when SQL-like query syntax is invalid."""
    
    def __init__(self, message: str, query: str, position: Optional[int] = None, **kwargs):
        super().__init__(message, query, position, component="query_parser", **kwargs)
        self.query = query


class TokenResolutionError(PatternParsingError):
    """Raised when dynamic token resolution fails."""
    
    def __init__(self, message: str, token: str, pattern: str, **kwargs):
        super().__init__(message, pattern, component="token_resolver", **kwargs)
        self.token = token


class PatternMatchingError(PatternSystemError):
    """Raised when pattern matching execution fails."""
    
    def __init__(self, message: str, pattern_id: str, **kwargs):
        super().__init__(message, component="pattern_matcher", **kwargs)
        self.pattern_id = pattern_id


class CacheError(PatternSystemError):
    """Raised when cache operations fail."""
    
    def __init__(self, message: str, cache_key: Optional[str] = None, **kwargs):
        super().__init__(message, component="cache_manager", **kwargs)
        self.cache_key = cache_key


class PatternRepositoryError(PatternSystemError):
    """Raised when pattern repository operations fail."""
    
    def __init__(self, message: str, operation: str, pattern_id: Optional[str] = None, **kwargs):
        super().__init__(message, component="pattern_repository", **kwargs)
        self.operation = operation
        self.pattern_id = pattern_id


class SerializationError(PatternSystemError):
    """Raised when pattern serialization/deserialization fails."""
    
    def __init__(self, message: str, data_type: str, **kwargs):
        super().__init__(message, component="pattern_serializer", **kwargs)
        self.data_type = data_type


class WorkspaceAnalysisError(PatternSystemError):
    """Raised when workspace analysis fails."""
    
    def __init__(self, message: str, workspace_path: str, **kwargs):
        super().__init__(message, component="workspace_analyzer", **kwargs)
        self.workspace_path = workspace_path


class SuggestionEngineError(PatternSystemError):
    """Raised when suggestion engine operations fail."""
    
    def __init__(self, message: str, suggestion_type: str, **kwargs):
        super().__init__(message, component="suggestion_engine", **kwargs)
        self.suggestion_type = suggestion_type


class PatternGroupError(PatternSystemError):
    """Raised when pattern group operations fail."""
    
    def __init__(self, message: str, group_id: Optional[str] = None, **kwargs):
        super().__init__(message, component="pattern_group", **kwargs)
        self.group_id = group_id


class PerformanceError(PatternSystemError):
    """Raised when performance constraints are violated."""
    
    def __init__(self, message: str, metric: str, threshold: Any, actual: Any, **kwargs):
        super().__init__(message, component="performance_analyzer", **kwargs)
        self.metric = metric
        self.threshold = threshold
        self.actual = actual


class PatternNotFoundError(PatternSystemError):
    """Raised when a requested pattern cannot be found."""
    
    def __init__(self, message: str, pattern_id: str, **kwargs):
        super().__init__(message, component="pattern_repository", **kwargs)
        self.pattern_id = pattern_id


class PatternParseError(PatternParsingError):
    """Raised when pattern parsing fails completely."""
    pass


class PatternSyntaxError(PatternParsingError):
    """Raised when pattern has invalid syntax."""
    pass


class PatternMatchError(PatternSystemError):
    """Raised when pattern matching fails."""
    
    def __init__(self, message: str, pattern_id: str, **kwargs):
        super().__init__(message, component="pattern_matcher", **kwargs)
        self.pattern_id = pattern_id


class PatternStorageError(PatternSystemError):
    """Raised when pattern storage operations fail."""
    
    def __init__(self, message: str, operation: str, **kwargs):
        super().__init__(message, component="pattern_storage", **kwargs)
        self.operation = operation


class QueryExecutionError(PatternSystemError):
    """Raised when query execution fails."""
    
    def __init__(self, message: str, query: str, **kwargs):
        super().__init__(message, component="query_executor", **kwargs)
        self.query = query


class SuggestionError(PatternSystemError):
    """Raised when suggestion generation fails."""
    
    def __init__(self, message: str, workspace_path: str, **kwargs):
        super().__init__(message, component="suggestion_engine", **kwargs)
        self.workspace_path = workspace_path


class ValidationError(PatternSystemError):
    """Raised when validation operations fail."""
    
    def __init__(self, message: str, target: str, **kwargs):
        super().__init__(message, component="pattern_validator", **kwargs)
        self.target = target
