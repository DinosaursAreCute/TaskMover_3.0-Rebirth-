"""
TaskMover Core Module

This module provides the foundational components for the TaskMover application,
including dependency injection, logging, storage, and configuration management.
"""

from .exceptions import (
    TaskMoverException,
    ConfigurationException, 
    ServiceException,
    CircularDependencyException,
    StorageException,
    ValidationException,
    LoggingException,
    PatternException,
    RuleException,
    FileOperationException
)

__version__ = "1.0.0"

__all__ = [
    "TaskMoverException",
    "ConfigurationException",
    "ServiceException", 
    "CircularDependencyException",
    "StorageException",
    "ValidationException",
    "LoggingException",
    "PatternException",
    "RuleException",
    "FileOperationException",
]
