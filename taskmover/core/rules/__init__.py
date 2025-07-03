"""
Rule System - Core API

File organization rules that use pattern matching to automatically
move files to designated destinations with conflict resolution.
"""

from .models import Rule, RuleExecutionResult, RuleConflictInfo, ErrorHandlingBehavior, RuleStatus, RuleValidationResult
from .service import RuleService
from .exceptions import RuleSystemError, RuleNotFoundError, RuleValidationError, RuleExecutionError

__all__ = [
    "Rule",
    "RuleExecutionResult", 
    "RuleConflictInfo",
    "ErrorHandlingBehavior",
    "RuleStatus",
    "RuleValidationResult",
    "RuleService",
    "RuleSystemError",
    "RuleNotFoundError", 
    "RuleValidationError",
    "RuleExecutionError"
]
