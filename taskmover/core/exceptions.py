"""
Core TaskMover Exceptions

This module defines the exception hierarchy for the TaskMover application.
All custom exceptions inherit from TaskMoverException for consistent error handling.
"""


class TaskMoverException(Exception):
    """Base exception for all TaskMover-specific errors"""

    def __init__(self, message: str, inner_exception: Exception | None = None):
        super().__init__(message)
        self.message = message
        self.inner_exception = inner_exception

    def __str__(self) -> str:
        if self.inner_exception:
            return f"{self.message} (Inner: {self.inner_exception})"
        return self.message


class ConfigurationException(TaskMoverException):
    """Raised when configuration loading or validation fails"""

    pass


class ServiceException(TaskMoverException):
    """Raised when dependency injection service operations fail"""

    pass


class CircularDependencyException(ServiceException):
    """Raised when circular dependency is detected in DI container"""

    pass


class StorageException(TaskMoverException):
    """Raised when storage operations fail"""

    pass


class ValidationException(TaskMoverException):
    """Raised when data validation fails"""

    pass


class LoggingException(TaskMoverException):
    """Raised when logging operations fail"""

    pass


class PatternException(TaskMoverException):
    """Raised when pattern operations fail"""

    pass


class RuleException(TaskMoverException):
    """Raised when rule operations fail"""

    pass


class FileOperationException(TaskMoverException):
    """Raised when file operations fail"""

    pass

# Legacy exception aliases for backward compatibility
TaskMoverError = TaskMoverException


class PatternError(TaskMoverException):
    """Raised when pattern operations fail"""
    pass


class RuleError(TaskMoverException):
    """Raised when rule operations fail"""
    pass


class FileOperationError(TaskMoverException):
    """Raised when file operations fail"""
    pass


class ConflictResolutionError(TaskMoverException):
    """Raised when file conflict resolution fails"""
    pass
