"""
Logging Utilities

Provides utility functions and decorators for the TaskMover logging system
including performance tracking, context management, and convenience functions.
"""

import functools
import threading
import time
from collections.abc import Callable
from contextlib import contextmanager
from datetime import datetime
from typing import Any

from .interfaces import ILogger, LogLevel


class PerformanceTimer:
    """Context manager and decorator for performance timing"""

    def __init__(
        self,
        operation_name: str,
        logger: ILogger | None = None,
        threshold_ms: float = 100.0,
        log_level: LogLevel = LogLevel.DEBUG,
    ):
        self.operation_name = operation_name
        self.logger = logger
        self.threshold_ms = threshold_ms
        self.log_level = log_level
        self.start_time: float | None = None
        self.end_time: float | None = None

    def __enter__(self):
        self.start_time = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.perf_counter()
        if self.start_time is not None:
            duration_ms = (self.end_time - self.start_time) * 1000
        else:
            duration_ms = 0.0

        # Log if above threshold or if error occurred
        should_log = duration_ms >= self.threshold_ms or exc_type is not None

        if should_log and self.logger:
            level = LogLevel.WARNING if exc_type else self.log_level
            status = "failed" if exc_type else "completed"

            self.logger.log(
                level,
                f"Operation '{self.operation_name}' {status}",
                extra_data={
                    "duration_ms": round(duration_ms, 2),
                    "operation": self.operation_name,
                    "status": status,
                    "exception": str(exc_val) if exc_val else None,
                },
            )

    @property
    def duration_ms(self) -> float | None:
        """Get duration in milliseconds"""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time) * 1000
        return None


def performance_timer(
    operation_name: str | None = None,
    threshold_ms: float = 100.0,
    log_level: LogLevel = LogLevel.DEBUG,
):
    """Decorator for automatic performance timing"""

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Try to get logger from method context
            logger = None
            if args and hasattr(args[0], "logger"):
                logger = args[0].logger
            elif "logger" in kwargs:
                logger = kwargs.pop("logger")

            op_name = operation_name or f"{func.__module__}.{func.__qualname__}"

            with PerformanceTimer(op_name, logger, threshold_ms, log_level):
                return func(*args, **kwargs)

        return wrapper

    return decorator


def log_method_calls(
    logger: ILogger | None = None,
    include_args: bool = False,
    include_result: bool = False,
    log_level: LogLevel = LogLevel.DEBUG,
):
    """Decorator to log method entry and exit"""

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            method_logger = logger
            if not method_logger and args and hasattr(args[0], "logger"):
                method_logger = args[0].logger

            if not method_logger:
                return func(*args, **kwargs)

            func_name = f"{func.__module__}.{func.__qualname__}"

            # Log entry
            entry_data = {"method": func_name, "phase": "enter"}
            if include_args:
                entry_data["args"] = str(args[1:]) if args else ""  # Skip self
                entry_data["kwargs"] = str(kwargs)

            method_logger.log(log_level, f"Entering {func_name}", extra_data=entry_data)

            try:
                result = func(*args, **kwargs)

                # Log successful exit
                exit_data = {"method": func_name, "phase": "exit", "status": "success"}
                if include_result:
                    exit_data["result"] = str(result)[:200]  # Limit length

                method_logger.log(
                    log_level, f"Exiting {func_name}", extra_data=exit_data
                )
                return result

            except Exception as e:
                # Log exception exit
                error_data = {
                    "method": func_name,
                    "phase": "exit",
                    "status": "error",
                    "exception": str(e),
                }
                method_logger.log(
                    LogLevel.ERROR, f"Exception in {func_name}", extra_data=error_data
                )
                raise

        return wrapper

    return decorator


class LoggingContext:
    """Thread-local logging context manager"""

    _local = threading.local()

    @classmethod
    def set_context(cls, **context_data):
        """Set context data for current thread"""
        if not hasattr(cls._local, "context"):
            cls._local.context = {}
        cls._local.context.update(context_data)

    @classmethod
    def get_context(cls) -> dict[str, Any]:
        """Get context data for current thread"""
        return getattr(cls._local, "context", {}).copy()

    @classmethod
    def clear_context(cls):
        """Clear context data for current thread"""
        if hasattr(cls._local, "context"):
            cls._local.context.clear()

    @classmethod
    @contextmanager
    def context(cls, **context_data):
        """Context manager for temporary context"""
        # Save current context
        old_context = cls.get_context()

        try:
            # Set new context
            cls.set_context(**context_data)
            yield
        finally:
            # Restore old context
            cls._local.context = old_context


@contextmanager
def log_performance(
    operation_name: str,
    logger: ILogger | None = None,
    threshold_ms: float = 100.0,
    log_level: LogLevel = LogLevel.INFO,
):
    """Context manager for performance logging"""
    timer = PerformanceTimer(operation_name, logger, threshold_ms, log_level)
    with timer:
        yield timer


def format_bytes(size_bytes: int) -> str:
    """Format byte size into human readable format"""
    if size_bytes == 0:
        return "0 B"

    size_float = float(size_bytes)
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size_float < 1024:
            return f"{size_float:.1f} {unit}"
        size_float /= 1024

    return f"{size_float:.1f} PB"


def format_duration(seconds: float) -> str:
    """Format duration into human readable format"""
    if seconds < 1:
        return f"{seconds * 1000:.1f} ms"
    elif seconds < 60:
        return f"{seconds:.1f} s"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        secs = seconds % 60
        return f"{minutes}m {secs:.1f}s"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = seconds % 60
        return f"{hours}h {minutes}m {secs:.1f}s"


def sanitize_path(path: str) -> str:
    """Sanitize file path for logging (remove sensitive info)"""
    import os
    import re

    # Replace user home directory
    home_dir = os.path.expanduser("~")
    if path.startswith(home_dir):
        path = path.replace(home_dir, "~", 1)

    # Replace common sensitive patterns
    path = re.sub(r"[/\\]Users[/\\][^/\\]+", "/Users/***", path)
    path = re.sub(r"[/\\]home[/\\][^/\\]+", "/home/***", path)

    return path


def truncate_string(text: str, max_length: int = 200, suffix: str = "...") -> str:
    """Truncate string if too long"""
    if len(text) <= max_length:
        return text

    truncate_length = max_length - len(suffix)
    return text[:truncate_length] + suffix


def safe_str(obj: Any, max_length: int = 200) -> str:
    """Safely convert object to string for logging"""
    try:
        if obj is None:
            return "None"
        elif isinstance(obj, str):
            return truncate_string(obj, max_length)
        elif isinstance(obj, int | float | bool):
            return str(obj)
        elif isinstance(obj, list | tuple):
            if len(obj) > 10:
                preview = str(obj[:10])[:-1] + f", ... ({len(obj)} items)]"
            else:
                preview = str(obj)
            return truncate_string(preview, max_length)
        elif isinstance(obj, dict):
            if len(obj) > 10:
                preview_items = list(obj.items())[:10]
                preview = str(dict(preview_items))[:-1] + f", ... ({len(obj)} items)}}"
            else:
                preview = str(obj)
            return truncate_string(preview, max_length)
        else:
            # For other objects, use repr with type info
            type_name = type(obj).__name__
            try:
                obj_repr = repr(obj)
                return truncate_string(f"{type_name}({obj_repr})", max_length)
            except Exception:
                return f"{type_name}(<unprintable>)"
    except Exception:
        return f"<error converting {type(obj).__name__} to string>"


def get_caller_info(skip_frames: int = 2) -> dict[str, str]:
    """Get information about the calling function"""
    import inspect

    frame = None
    try:
        frame = inspect.currentframe()

        # Skip frames to get to the actual caller
        for _ in range(skip_frames):
            if frame is None:
                break
            frame = frame.f_back

        if frame is None:
            return {"module": "unknown", "function": "unknown", "line": "0"}

        code = frame.f_code
        return {
            "module": code.co_filename.split("/")[-1],
            "function": code.co_name,
            "line": str(frame.f_lineno),
        }
    except Exception:
        return {"module": "unknown", "function": "unknown", "line": "0"}
    finally:
        # Clean up frame reference
        if frame is not None:
            del frame


class RateLimiter:
    """Rate limiter for log messages to prevent spam"""

    def __init__(self, max_messages: int = 10, time_window: float = 60.0):
        self.max_messages = max_messages
        self.time_window = time_window
        self._messages: dict[str, list] = {}
        self._lock = threading.Lock()

    def should_log(self, message_key: str) -> bool:
        """Check if message should be logged based on rate limit"""
        now = time.time()

        with self._lock:
            if message_key not in self._messages:
                self._messages[message_key] = []

            # Clean old messages
            cutoff_time = now - self.time_window
            self._messages[message_key] = [
                t for t in self._messages[message_key] if t > cutoff_time
            ]

            # Check if under limit
            if len(self._messages[message_key]) < self.max_messages:
                self._messages[message_key].append(now)
                return True

            return False


class LogBuffer:
    """Buffer for collecting log messages"""

    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self._buffer: list[tuple[datetime, str]] = []
        self._lock = threading.Lock()

    def add(self, message: str, timestamp: datetime | None = None):
        """Add message to buffer"""
        if timestamp is None:
            timestamp = datetime.now()

        with self._lock:
            self._buffer.append((timestamp, message))

            # Trim if over size
            if len(self._buffer) > self.max_size:
                self._buffer = self._buffer[-self.max_size :]

    def get_messages(self, since: datetime | None = None) -> list:
        """Get messages from buffer, optionally since a timestamp"""
        with self._lock:
            if since is None:
                return self._buffer.copy()
            else:
                return [(ts, msg) for ts, msg in self._buffer if ts >= since]

    def clear(self):
        """Clear buffer"""
        with self._lock:
            self._buffer.clear()


# Global rate limiter instance
_global_rate_limiter = RateLimiter()


def rate_limited_log(
    logger: ILogger,
    level: LogLevel,
    message: str,
    rate_key: str | None = None,
    **kwargs,
):
    """Log message with rate limiting"""
    key = rate_key or message[:50]  # Use first 50 chars as key

    if _global_rate_limiter.should_log(key):
        logger.log(level, message, **kwargs)
    else:
        # Log a rate limit warning occasionally
        if _global_rate_limiter.should_log(f"rate_limit_warning_{key}"):
            logger.log(
                LogLevel.WARNING,
                f"Rate limiting active for: {message[:50]}...",
                extra_data={"rate_limited_message": key},
            )


# Export convenience functions
__all__ = [
    "PerformanceTimer",
    "performance_timer",
    "log_method_calls",
    "LoggingContext",
    "log_performance",
    "format_bytes",
    "format_duration",
    "sanitize_path",
    "truncate_string",
    "safe_str",
    "get_caller_info",
    "RateLimiter",
    "LogBuffer",
    "rate_limited_log",
]
