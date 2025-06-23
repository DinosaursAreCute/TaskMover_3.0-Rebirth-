"""
Logger Manager Implementation

Thread-safe singleton that manages loggers, configuration, and context for the entire application.
Provides centralized logging coordination and component-based logger creation.
"""

import threading
import uuid
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from .config import LoggingConfig, get_config
from .interfaces import (
    IContextManager,
    ILogger,
    ILoggerManager,
    ILogHandler,
    IPerformanceTracker,
    LogContext,
    LogLevel,
    LogRecord,
)


class PerformanceTracker(IPerformanceTracker):
    """Performance tracking implementation"""

    def __init__(self):
        self._operations: dict[str, datetime] = {}
        self._lock = threading.Lock()

    def start_operation(self, operation_name: str) -> str:
        """Start tracking operation"""
        operation_id = str(uuid.uuid4())
        with self._lock:
            self._operations[operation_id] = datetime.now()
        return operation_id

    def end_operation(self, operation_id: str) -> float:
        """End tracking operation"""
        end_time = datetime.now()
        with self._lock:
            start_time = self._operations.pop(operation_id, None)
            if start_time is None:
                return 0.0
            return (end_time - start_time).total_seconds()

    def log_performance(
        self, operation_name: str, duration: float, **kwargs: Any
    ) -> None:
        """Log performance metrics"""
        # This will be implemented when we have the full logger
        pass


class ContextManager(IContextManager):
    """Context management implementation"""

    def __init__(self):
        self._session_id = str(uuid.uuid4())
        self._operations: dict[str, str] = {}
        self._lock = threading.Lock()

    def create_session(self) -> str:
        """Create new logging session"""
        with self._lock:
            self._session_id = str(uuid.uuid4())
            return self._session_id

    def get_session_id(self) -> str:
        """Get current session ID"""
        return self._session_id

    def create_operation(self, operation_name: str) -> str:
        """Create operation context"""
        operation_id = str(uuid.uuid4())
        with self._lock:
            self._operations[operation_id] = operation_name
        return operation_id

    def end_operation(self, operation_id: str) -> None:
        """End operation context"""
        with self._lock:
            self._operations.pop(operation_id, None)


class ComponentLogger(ILogger):
    """Component-specific logger implementation"""

    def __init__(self, component: str, manager: "LoggerManager"):
        self.component = component
        self.manager = manager
        self._level = LogLevel.INFO

    def debug(self, message: str, **kwargs: Any) -> None:
        """Log debug message"""
        self.log(LogLevel.DEBUG, message, **kwargs)

    def info(self, message: str, **kwargs: Any) -> None:
        """Log info message"""
        self.log(LogLevel.INFO, message, **kwargs)

    def warning(self, message: str, **kwargs: Any) -> None:
        """Log warning message"""
        self.log(LogLevel.WARNING, message, **kwargs)

    def error(self, message: str, **kwargs: Any) -> None:
        """Log error message"""
        self.log(LogLevel.ERROR, message, **kwargs)

    def critical(self, message: str, **kwargs: Any) -> None:
        """Log critical message"""
        self.log(LogLevel.CRITICAL, message, **kwargs)

    def log(self, level: LogLevel, message: str, **kwargs: Any) -> None:
        """Log message at specified level"""
        if not self.is_enabled_for(level):
            return

        # Create log record
        record = LogRecord(
            timestamp=datetime.now(),
            level=level,
            component=self.component,
            message=message,
            context=self.manager.get_context(),
            exception=kwargs.get("exception"),
            extra_data=kwargs.get("extra_data"),
        )

        # Send to manager for handling
        self.manager._handle_record(record)

    def is_enabled_for(self, level: LogLevel) -> bool:
        """Check if logger is enabled for level"""
        component_level = self.manager._get_component_level(self.component)
        return level.value >= component_level.value

    def set_level(self, level: LogLevel) -> None:
        """Set logger level"""
        self._level = level


class LoggerManager(ILoggerManager):
    """Thread-safe singleton logger manager"""

    _instance: Optional["LoggerManager"] = None
    _lock = threading.Lock()

    def __new__(cls) -> "LoggerManager":
        """Singleton pattern with thread safety"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize logger manager (only once)"""
        # Initialize the _initialized attribute
        if not hasattr(self, "_initialized"):
            self._initialized = False

        if self._initialized:
            return

        self._loggers: dict[str, ComponentLogger] = {}
        self._handlers: set[ILogHandler] = set()
        self._config: LoggingConfig | None = None
        self._context: LogContext | None = None
        self._performance_tracker = PerformanceTracker()
        self._context_manager = ContextManager()
        self._logger_lock = threading.RLock()
        self._handler_lock = threading.Lock()
        self._initialized = True

        # Load initial configuration
        try:
            self.configure(get_config())
        except Exception as e:
            print(f"Warning: Failed to load logging configuration: {e}")

    def get_logger(self, component: str) -> ILogger:
        """Get logger for component"""
        with self._logger_lock:
            if component not in self._loggers:
                self._loggers[component] = ComponentLogger(component, self)
            return self._loggers[component]

    def configure(self, config: LoggingConfig) -> None:
        """Configure logging system"""
        self._config = config

        # Clear existing handlers
        with self._handler_lock:
            for handler in self._handlers:
                try:
                    handler.close()
                except Exception:
                    pass
            self._handlers.clear()

            # Import handlers locally to avoid circular imports
            from .handlers import (
                CleanupHandler,
                ColoredConsoleHandler,
                RotatingFileHandler,
            )

            # Create console handler if enabled
            if config.console.enabled:
                console_handler = ColoredConsoleHandler(
                    use_colors=config.console.colors,
                    use_emojis=True,
                    level=config.level,
                )
                self._handlers.add(console_handler)

            # Create file handler if enabled
            if config.file.enabled:
                # Parse max_size string to bytes
                max_size = self._parse_size_string(config.file.rotation.max_size)

                file_handler = RotatingFileHandler(
                    filename=config.file.path,
                    max_size=max_size,
                    backup_count=config.file.rotation.backup_count,
                    compression=config.file.rotation.compression_enabled,
                    level=config.level,
                )
                self._handlers.add(file_handler)

                # Add cleanup handler for log directory
                if config.file.rotation.retention_days > 0:
                    log_dir = str(Path(config.file.path).parent)
                    cleanup_handler = CleanupHandler(
                        log_directory=log_dir,
                        retention_days=config.file.rotation.retention_days,
                        level=LogLevel.CRITICAL,  # Only activate on critical logs
                    )
                    self._handlers.add(cleanup_handler)

            print(
                f"Logging configured: level={config.level.value}, "
                f"console={config.console.enabled}, file={config.file.enabled}"
            )

    def _parse_size_string(self, size_str: str) -> int:
        """Parse size string like '10MB' to bytes"""
        import re

        size_str = size_str.upper().strip()
        match = re.match(r"^(\d+(?:\.\d+)?)\s*([KMGT]?B?)$", size_str)

        if not match:
            return 10 * 1024 * 1024  # Default 10MB

        number, unit = match.groups()
        number = float(number)

        multipliers = {
            "B": 1,
            "KB": 1024,
            "MB": 1024**2,
            "GB": 1024**3,
            "TB": 1024**4,
        }

        return int(number * multipliers.get(unit, 1))

    def shutdown(self) -> None:
        """Shutdown logging system"""
        with self._handler_lock:
            for handler in self._handlers:
                try:
                    handler.close()
                except Exception:
                    pass
            self._handlers.clear()

        with self._logger_lock:
            self._loggers.clear()

    def set_context(self, context: LogContext | None) -> None:
        """Set logging context"""
        self._context = context

    def get_context(self) -> LogContext | None:
        """Get current logging context"""
        return self._context

    def create_session(self) -> str:
        """Create new logging session"""
        session_id = self._context_manager.create_session()
        self._context = LogContext(session_id=session_id, component="system")
        return session_id

    def add_handler(self, handler: ILogHandler) -> None:
        """Add log handler"""
        with self._handler_lock:
            self._handlers.add(handler)

    def remove_handler(self, handler: ILogHandler) -> None:
        """Remove log handler"""
        with self._handler_lock:
            self._handlers.discard(handler)
            try:
                handler.close()
            except Exception:
                pass

    def _handle_record(self, record: LogRecord) -> None:
        """Handle log record by sending to all handlers"""
        with self._handler_lock:
            for handler in self._handlers:
                try:
                    handler.handle(record)
                except Exception as e:
                    # Prevent logging errors from breaking the application
                    print(f"Handler error: {e}")

    def _get_component_level(self, component: str) -> LogLevel:
        """Get effective log level for component"""
        if self._config and component in self._config.components:
            return self._config.components[component]
        return self._config.level if self._config else LogLevel.INFO

    # Performance tracking methods
    def start_operation(self, operation_name: str) -> str:
        """Start performance tracking for operation"""
        return self._performance_tracker.start_operation(operation_name)

    def end_operation(self, operation_id: str) -> float:
        """End performance tracking"""
        duration = self._performance_tracker.end_operation(operation_id)
        if self._config and self._config.performance_monitoring:
            self._performance_tracker.log_performance(
                "operation", duration, operation_id=operation_id
            )
        return duration


# Global logger manager instance
_manager: LoggerManager | None = None


def get_logger(component: str) -> ILogger:
    """Get logger for component (convenience function)"""
    global _manager
    if _manager is None:
        _manager = LoggerManager()
    return _manager.get_logger(component)


def get_component_logger(component: str) -> ILogger:
    """Get component logger (alias for get_logger)"""
    return get_logger(component)


@contextmanager
def log_context(
    session_id: str | None = None, operation_id: str | None = None, **kwargs
):
    """Context manager for logging context"""
    global _manager
    if _manager is None:
        _manager = LoggerManager()

    # Create context
    context = LogContext(
        session_id=session_id or _manager._context_manager.get_session_id(),
        component=kwargs.get("component", "system"),
        operation_id=operation_id,
        user_id=kwargs.get("user_id"),
        correlation_id=kwargs.get("correlation_id"),
        extra_data=kwargs.get("extra_data"),
    )

    # Store previous context
    previous_context = _manager.get_context()

    try:
        # Set new context
        _manager.set_context(context)
        yield _manager
    finally:
        # Restore previous context
        _manager.set_context(previous_context)
