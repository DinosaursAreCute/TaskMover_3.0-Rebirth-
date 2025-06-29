"""
Rule System Models

Core data models for rule management and execution.
"""

import shutil
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from uuid import UUID, uuid4


class ErrorHandlingBehavior(Enum):
    """How to handle errors during rule execution."""
    STOP_ON_FIRST_ERROR = "stop_on_first_error"
    CONTINUE_ON_RECOVERABLE = "continue_on_recoverable" 
    CONTINUE_ON_ALL = "continue_on_all"


class RuleStatus(Enum):
    """Rule execution status."""
    READY = "ready"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Rule:
    """
    A rule that moves files matching a pattern to a destination folder.
    
    Rules reference existing patterns and define where matching files
    should be moved with priority-based execution order.
    """
    id: UUID = field(default_factory=uuid4)
    name: str = ""
    description: str = ""
    
    # Pattern relationship
    pattern_id: UUID = field(default_factory=uuid4)
    
    # Action configuration  
    destination_path: Path = field(default_factory=lambda: Path())
    
    # Rule state
    is_enabled: bool = True
    priority: int = 0  # Higher = executes first
    
    # Error handling
    error_handling: ErrorHandlingBehavior = ErrorHandlingBehavior.CONTINUE_ON_RECOVERABLE
    
    # Metadata
    created_date: datetime = field(default_factory=datetime.utcnow)
    modified_date: datetime = field(default_factory=datetime.utcnow)
    author: str = "user"
    
    # Usage statistics
    last_executed: Optional[datetime] = None
    execution_count: int = 0
    files_processed: int = 0
    
    def __post_init__(self):
        """Validate rule after initialization."""
        if not self.name:
            self.name = f"Rule {str(self.id)[:8]}"
        
        # Ensure destination_path is Path object
        if isinstance(self.destination_path, str):
            self.destination_path = Path(self.destination_path)
    
    def update_execution_stats(self, files_processed: int = 0) -> None:
        """Update rule execution statistics."""
        self.last_executed = datetime.utcnow()
        self.execution_count += 1
        self.files_processed += files_processed
        self.modified_date = datetime.utcnow()
    
    def validate(self) -> List[str]:
        """Validate rule configuration and return any errors."""
        errors = []
        
        if not self.name.strip():
            errors.append("Rule name cannot be empty")
        
        if not self.pattern_id:
            errors.append("Rule must reference a pattern")
        
        if not self.destination_path:
            errors.append("Rule must have a destination path")
        
        # Check if destination exists (user requirement)
        if self.destination_path and not self.destination_path.exists():
            errors.append(f"Destination directory does not exist: {self.destination_path}")
        
        if not self.destination_path.is_dir() if self.destination_path.exists() else False:
            errors.append(f"Destination path is not a directory: {self.destination_path}")
        
        return errors


@dataclass
class RuleConflictInfo:
    """Information about rule conflicts."""
    rule_id: UUID
    conflicting_rules: List[UUID]
    conflict_type: str  # "same_pattern", "same_priority", "unreachable"
    severity: str  # "warning", "error"
    message: str


@dataclass
class FileOperationResult:
    """Result of a single file operation."""
    source_path: Path
    destination_path: Optional[Path] = None
    success: bool = False
    error_message: Optional[str] = None
    operation_type: str = "move"  # move, copy, rename
    
    def __post_init__(self):
        """Ensure paths are Path objects."""
        if isinstance(self.source_path, str):
            self.source_path = Path(self.source_path)
        if isinstance(self.destination_path, str):
            self.destination_path = Path(self.destination_path)


@dataclass
class RuleExecutionResult:
    """
    Result of executing a rule with detailed operation information.
    """
    rule_id: UUID
    rule_name: str
    status: RuleStatus
    
    # File operation results
    matched_files: List[Path] = field(default_factory=list)
    file_operations: List[FileOperationResult] = field(default_factory=list)
    
    # Statistics
    files_matched: int = 0
    files_moved: int = 0
    files_failed: int = 0
    conflicts_detected: int = 0
    conflicts_resolved: int = 0
    
    # Performance
    execution_time_ms: float = 0.0
    
    # Execution metadata
    dry_run: bool = False
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Error information
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Calculate derived statistics."""
        if not self.started_at:
            self.started_at = datetime.utcnow()
            
        # Calculate statistics from file operations
        self.files_matched = len(self.matched_files)
        self.files_moved = len([op for op in self.file_operations if op.success])
        self.files_failed = len([op for op in self.file_operations if not op.success])
    
    def add_file_operation(self, operation: FileOperationResult) -> None:
        """Add a file operation result and update statistics."""
        self.file_operations.append(operation)
        
        # Update counters
        if operation.success:
            self.files_moved += 1
        else:
            self.files_failed += 1
            if operation.error_message:
                self.errors.append(f"{operation.source_path}: {operation.error_message}")
    
    def add_error(self, error: str) -> None:
        """Add an error message."""
        self.errors.append(error)
        if self.status != RuleStatus.FAILED:
            self.status = RuleStatus.FAILED
    
    def add_warning(self, warning: str) -> None:
        """Add a warning message."""
        self.warnings.append(warning)
    
    def complete(self, success: bool = True) -> None:
        """Mark execution as completed."""
        self.completed_at = datetime.utcnow()
        if success and self.status != RuleStatus.FAILED:
            self.status = RuleStatus.COMPLETED
        elif not success:
            self.status = RuleStatus.FAILED
            
        # Calculate execution time
        if self.started_at and self.completed_at:
            delta = self.completed_at - self.started_at
            self.execution_time_ms = delta.total_seconds() * 1000
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate of file operations."""
        total_operations = len(self.file_operations)
        if total_operations == 0:
            return 1.0
        return self.files_moved / total_operations
    
    @property
    def summary(self) -> str:
        """Get a human-readable summary of the execution."""
        if self.dry_run:
            return f"DRY RUN: Would move {self.files_matched} files"
        else:
            return f"Moved {self.files_moved}/{self.files_matched} files ({self.files_failed} failed)"


@dataclass
class RuleValidationResult:
    """Result of rule validation."""
    rule_id: UUID
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    def add_error(self, error: str) -> None:
        """Add a validation error."""
        self.errors.append(error)
        self.is_valid = False
    
    def add_warning(self, warning: str) -> None:
        """Add a validation warning."""
        self.warnings.append(warning)
