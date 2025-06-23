"""
Logging System Exceptions

Custom exceptions for the TaskMover logging system to provide specific
error handling and diagnostics for logging operations.
"""

from typing import Any


class LoggingException(Exception):
    """Base exception for all logging-related errors"""

    def __init__(self, message: str, component: str | None = None, **context: Any):
        super().__init__(message)
        self.component = component
        self.context = context

    def __str__(self) -> str:
        base_msg = super().__str__()
        if self.component:
            return f"[{self.component}] {base_msg}"
        return base_msg


class ConfigurationError(LoggingException):
    """Raised when logging configuration is invalid or cannot be loaded"""

    pass


class HandlerError(LoggingException):
    """Raised when a log handler encounters an error"""

    pass


class FormatterError(LoggingException):
    """Raised when a log formatter encounters an error"""

    pass


class FileRotationError(HandlerError):
    """Raised when file rotation fails"""

    pass


class PermissionError(HandlerError):
    """Raised when insufficient permissions for logging operations"""

    pass


class DiskSpaceError(HandlerError):
    """Raised when insufficient disk space for logging"""

    pass


class CompressionError(HandlerError):
    """Raised when log file compression fails"""

    pass


class ContextError(LoggingException):
    """Raised when logging context operations fail"""

    pass


class SessionError(LoggingException):
    """Raised when session management fails"""

    pass


class PerformanceTrackingError(LoggingException):
    """Raised when performance tracking fails"""

    pass
