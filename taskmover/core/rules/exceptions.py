"""
Rule System Exceptions

Exception hierarchy for rule system operations.
"""

from typing import Optional, List
from uuid import UUID


class RuleSystemError(Exception):
    """Base exception for rule system errors."""
    
    def __init__(self, message: str, rule_id: Optional[UUID] = None):
        super().__init__(message)
        self.rule_id = rule_id


class RuleNotFoundError(RuleSystemError):
    """Raised when a rule cannot be found."""
    
    def __init__(self, rule_id: UUID):
        super().__init__(f"Rule {rule_id} not found", rule_id)


class RuleValidationError(RuleSystemError):
    """Raised when rule validation fails."""
    
    def __init__(self, message: str, rule_id: Optional[UUID] = None, errors: Optional[List[str]] = None):
        super().__init__(message, rule_id)
        self.errors = errors or []


class RuleExecutionError(RuleSystemError):
    """Raised when rule execution fails."""
    
    def __init__(self, message: str, rule_id: Optional[UUID] = None, failed_files: Optional[List[str]] = None):
        super().__init__(message, rule_id)
        self.failed_files = failed_files or []


class RuleConflictError(RuleSystemError):
    """Raised when rule conflicts cannot be resolved."""
    
    def __init__(self, message: str, conflicting_rules: Optional[List[UUID]] = None):
        super().__init__(message)
        self.conflicting_rules = conflicting_rules or []


class DestinationNotFoundError(RuleSystemError):
    """Raised when rule destination directory does not exist."""
    
    def __init__(self, destination_path: str, rule_id: Optional[UUID] = None):
        super().__init__(f"Destination directory not found: {destination_path}", rule_id)
        self.destination_path = destination_path
