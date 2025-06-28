"""
Pattern System Interfaces

Abstract base classes and protocols defining the contracts for
the unified pattern system components.
"""

from abc import ABC, abstractmethod
from typing import Any, List, Optional, Protocol, Dict, Union, TYPE_CHECKING
from pathlib import Path
from datetime import datetime
from uuid import UUID

from .exceptions import PatternSystemError

# Forward declarations to avoid circular imports
if TYPE_CHECKING:
    from .models import (
        Pattern, ParsedPattern, ValidationResult, MatchResult
    )
    from .models.query_ast import QueryAST


class IPatternParser(Protocol):
    """Protocol for pattern parsing implementations."""
    
    def parse(self, user_input: str) -> "ParsedPattern":
        """Parse user input into a structured pattern representation."""
        ...
    
    def validate_syntax(self, user_input: str) -> "ValidationResult":
        """Validate pattern syntax without full parsing."""
        ...


class IPatternMatcher(Protocol):
    """Protocol for pattern matching implementations."""
    
    def match(self, pattern: "Pattern", file_paths: List[Path]) -> "MatchResult":
        """Execute pattern matching against file paths."""
        ...
    
    def match_single(self, pattern: "Pattern", file_path: Path) -> bool:
        """Check if a single file matches the pattern."""
        ...


class IPatternRepository(Protocol):
    """Protocol for pattern storage and retrieval."""
    
    def save(self, pattern: "Pattern") -> None:
        """Save a pattern to storage."""
        ...
    
    def get(self, pattern_id: UUID) -> Optional["Pattern"]:
        """Retrieve a pattern by ID."""
        ...
    
    def list_patterns(self, filters: Optional[Dict[str, Any]] = None) -> List["Pattern"]:
        """List patterns with optional filtering."""
        ...
    
    def delete(self, pattern_id: UUID) -> bool:
        """Delete a pattern by ID."""
        ...


class ICacheManager(Protocol):
    """Protocol for caching implementations."""
    
    def get(self, key: str) -> Optional[Any]:
        """Retrieve value from cache."""
        ...
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Store value in cache with optional TTL."""
        ...
    
    def invalidate(self, key: str) -> None:
        """Remove value from cache."""
        ...
    
    def clear(self) -> None:
        """Clear all cache entries."""
        ...


class ISuggestionEngine(Protocol):
    """Protocol for pattern suggestion implementations."""
    
    def suggest_patterns(self, workspace_path: Path, partial_input: str = "") -> List[Dict[str, Any]]:
        """Generate context-aware pattern suggestions."""
        ...
    
    def get_completions(self, partial_input: str) -> List[str]:
        """Get auto-completion suggestions for partial input."""
        ...


class IWorkspaceAnalyzer(Protocol):
    """Protocol for workspace analysis implementations."""
    
    def analyze(self, workspace_path: Path) -> Dict[str, Any]:
        """Analyze workspace and return file pattern insights."""
        ...
    
    def get_common_extensions(self, workspace_path: Path) -> List[str]:
        """Get most common file extensions in workspace."""
        ...


class ITokenResolver(Protocol):
    """Protocol for dynamic token resolution."""
    
    def resolve_tokens(self, pattern: str) -> str:
        """Resolve all dynamic tokens in a pattern."""
        ...
    
    def get_available_tokens(self) -> Dict[str, str]:
        """Get all available tokens and their descriptions."""
        ...


class IQueryExecutor(Protocol):
    """Protocol for query execution implementations."""
    
    def execute(self, query: "QueryAST", file_paths: List[Path]) -> List[Path]:
        """Execute a compiled query against file paths."""
        ...
    
    def optimize_query(self, query: "QueryAST") -> "QueryAST":
        """Optimize query for better performance."""
        ...


class IPatternValidator(Protocol):
    """Protocol for pattern validation implementations."""
    
    def validate(self, pattern: "Pattern") -> "ValidationResult":
        """Validate a complete pattern."""
        ...
    
    def validate_expression(self, expression: str) -> "ValidationResult":
        """Validate a pattern expression."""
        ...


class ISerializationProvider(Protocol):
    """Protocol for pattern serialization implementations."""
    
    def serialize(self, obj: Any) -> str:
        """Serialize object to string format."""
        ...
    
    def deserialize(self, data: str, target_type: type) -> Any:
        """Deserialize string data to target type."""
        ...


# Abstract base classes for concrete implementations

class BasePatternService(ABC):
    """Base class for pattern service implementations."""
    
    def __init__(self, logger_name: str = "pattern_service"):
        from taskmover.core.logging import get_logger
        self._logger = get_logger(logger_name)
    
    @abstractmethod
    def initialize(self) -> None:
        """Initialize the service."""
        pass
    
    @abstractmethod
    def shutdown(self) -> None:
        """Cleanup and shutdown the service."""
        pass


class BasePatternComponent(ABC):
    """Base class for all pattern system components."""
    
    def __init__(self, component_name: str):
        from taskmover.core.logging import get_logger
        self._logger = get_logger(f"patterns.{component_name}")
        self._component_name = component_name
        self._logger.debug(f"Initializing {component_name} component")
    
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
