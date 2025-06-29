"""
TaskMover - Intelligent File Organization System
================================================

A modern, pattern-based file organization system with AI-assisted development,
conflict resolution, and comprehensive UI components.
"""

__version__ = "1.0.0"
__author__ = "TaskMover Team"
__description__ = "Intelligent file organization system with pattern-based rules"

from .core.exceptions import TaskMoverError, PatternError, RuleError
from .ui.main_application import TaskMoverApplication

__all__ = [
    "TaskMoverError",
    "PatternError", 
    "RuleError",
    "TaskMoverApplication",
]
