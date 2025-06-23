"""
Core Logging Interfaces

This module defines the contracts and abstractions for the TaskMover logging system.
All logging components implement these interfaces to ensure consistency and testability.
"""

from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from enum import IntEnum
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .config import LoggingConfig


class LogLevel(IntEnum):
    """Logging levels in order of severity"""

    DEBUG = 10
    INFO = 20
    WARNING = 30
    ERROR = 40
    CRITICAL = 50


@dataclass
class LogContext:
    """Context information for log entries"""

    session_id: str
    component: str
    operation_id: str | None = None
    user_id: str | None = None
    correlation_id: str | None = None
    extra_data: dict[str, Any] | None = None


@dataclass
class LogRecord:
    """Structured log record"""

    timestamp: datetime
    level: LogLevel
    component: str
    message: str
    context: LogContext | None = None
    exception: Exception | None = None
    extra_data: dict[str, Any] | None = None


class ILogger(ABC):
    """Abstract logger interface"""

    @abstractmethod
    def debug(self, message: str, **kwargs: Any) -> None:
        """Log debug message"""
        pass

    @abstractmethod
    def info(self, message: str, **kwargs: Any) -> None:
        """Log info message"""
        pass

    @abstractmethod
    def warning(self, message: str, **kwargs: Any) -> None:
        """Log warning message"""
        pass

    @abstractmethod
    def error(self, message: str, **kwargs: Any) -> None:
        """Log error message"""
        pass

    @abstractmethod
    def critical(self, message: str, **kwargs: Any) -> None:
        """Log critical message"""
        pass

    @abstractmethod
    def log(self, level: LogLevel, message: str, **kwargs: Any) -> None:
        """Log message at specified level"""
        pass

    @abstractmethod
    def is_enabled_for(self, level: LogLevel) -> bool:
        """Check if logger is enabled for level"""
        pass


class ILogFormatter(ABC):
    """Abstract log formatter interface"""

    @abstractmethod
    def format(self, record: LogRecord) -> str:
        """Format log record to string"""
        pass


class ILogHandler(ABC):
    """Abstract log handler interface"""

    @abstractmethod
    def handle(self, record: LogRecord) -> None:
        """Handle log record"""
        pass

    @abstractmethod
    def set_formatter(self, formatter: ILogFormatter) -> None:
        """Set log formatter"""
        pass

    @abstractmethod
    def set_level(self, level: LogLevel) -> None:
        """Set minimum log level"""
        pass

    @abstractmethod
    def close(self) -> None:
        """Close handler and release resources"""
        pass


class ILoggerManager(ABC):
    """Abstract logger manager interface"""

    @abstractmethod
    def get_logger(self, component: str) -> ILogger:
        """Get logger for component"""
        pass

    @abstractmethod
    def configure(self, config: "LoggingConfig") -> None:
        """Configure logging system"""
        pass

    @abstractmethod
    def shutdown(self) -> None:
        """Shutdown logging system"""
        pass

    @abstractmethod
    def set_context(self, context: LogContext) -> None:
        """Set logging context"""
        pass

    @abstractmethod
    def get_context(self) -> LogContext | None:
        """Get current logging context"""
        pass


class IPerformanceTracker(ABC):
    """Abstract performance tracking interface"""

    @abstractmethod
    def start_operation(self, operation_name: str) -> str:
        """Start tracking operation, returns operation ID"""
        pass

    @abstractmethod
    def end_operation(self, operation_id: str) -> float:
        """End tracking operation, returns duration in seconds"""
        pass

    @abstractmethod
    def log_performance(
        self, operation_name: str, duration: float, **kwargs: Any
    ) -> None:
        """Log performance metrics"""
        pass


class IContextManager(ABC):
    """Abstract context manager interface"""

    @abstractmethod
    def create_session(self) -> str:
        """Create new logging session"""
        pass

    @abstractmethod
    def get_session_id(self) -> str:
        """Get current session ID"""
        pass

    @abstractmethod
    def create_operation(self, operation_name: str) -> str:
        """Create operation context"""
        pass

    @abstractmethod
    def end_operation(self, operation_id: str) -> None:
        """End operation context"""
        pass


# Type aliases for convenience
LoggerFactory = Callable[[str], ILogger]
HandlerFactory = Callable[[], ILogHandler]
FormatterFactory = Callable[[], ILogFormatter]
