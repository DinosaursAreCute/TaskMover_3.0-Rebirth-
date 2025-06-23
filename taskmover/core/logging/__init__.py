"""
TaskMover Core Logging System

This package provides a comprehensive logging system with:
- Configurable log levels and component filtering
- Multiple output handlers (console with colors, rotating files)
- Automatic log cleanup and rotation
- Performance monitoring and context tracking
- Easy integration with existing TaskMover components

Usage:
    from taskmover.core.logging import get_logger

    logger = get_logger('ui.theme')
    logger.info("Theme changed to dark mode", context={"user": "manual"})
"""

from .config import LoggingConfig
from .formatters import ComponentFormatter, ConsoleFormatter, FileFormatter
from .handlers import CleanupHandler, ColoredConsoleHandler, RotatingFileHandler
from .manager import LoggerManager, get_component_logger, get_logger, log_context

__all__ = [
    "LoggerManager",
    "get_logger",
    "get_component_logger",
    "log_context",
    "LoggingConfig",
    "ConsoleFormatter",
    "FileFormatter",
    "ComponentFormatter",
    "ColoredConsoleHandler",
    "RotatingFileHandler",
    "CleanupHandler",
]

__version__ = "1.0.0"
