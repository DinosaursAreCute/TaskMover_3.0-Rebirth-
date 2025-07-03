"""
File Operations Interfaces
=========================

Core interfaces for file system operations, providing a clean abstraction
layer over file system interactions with support for different backends.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import List, Dict, Any, Optional, Union, AsyncIterator
from datetime import datetime
import asyncio


class OperationType(Enum):
    """Types of file operations."""
    COPY = "copy"
    MOVE = "move"
    DELETE = "delete"
    RENAME = "rename"
    CREATE = "create"
    MODIFY = "modify"


class OperationStatus(Enum):
    """Status of file operations."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    SKIPPED = "skipped"


class ConflictResolution(Enum):
    """How to handle file conflicts."""
    SKIP = "skip"
    OVERWRITE = "overwrite"
    RENAME = "rename"
    PROMPT = "prompt"
    MERGE = "merge"


@dataclass
class OperationResult:
    """Result of a file operation."""
    operation_id: str
    operation_type: OperationType
    source_path: Optional[Path]
    destination_path: Optional[Path]
    status: OperationStatus
    success: bool
    error_message: Optional[str] = None
    bytes_processed: int = 0
    duration_seconds: float = 0.0
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class OperationProgress:
    """Progress information for file operations."""
    operation_id: str
    total_bytes: int
    processed_bytes: int
    current_file: Optional[Path]
    files_processed: int
    total_files: int
    speed_bytes_per_second: float
    estimated_time_remaining: float
    
    @property
    def progress_percentage(self) -> float:
        """Calculate progress percentage."""
        if self.total_bytes == 0:
            return 0.0
        return (self.processed_bytes / self.total_bytes) * 100.0


class IFileOperationProvider(ABC):
    """Interface for file operation providers."""
    
    @abstractmethod
    async def copy_file(self, source: Path, destination: Path, 
                       preserve_metadata: bool = True) -> OperationResult:
        """Copy a single file."""
        pass
    
    @abstractmethod
    async def move_file(self, source: Path, destination: Path) -> OperationResult:
        """Move a single file."""
        pass
    
    @abstractmethod
    async def delete_file(self, file_path: Path, use_recycle_bin: bool = True) -> OperationResult:
        """Delete a single file."""
        pass
    
    @abstractmethod
    async def create_directory(self, directory_path: Path, parents: bool = True) -> OperationResult:
        """Create a directory."""
        pass
    
    @abstractmethod
    async def get_file_info(self, file_path: Path) -> Dict[str, Any]:
        """Get file metadata and information."""
        pass


class IFileOperationManager(ABC):
    """Interface for managing file operations."""
    
    @abstractmethod
    async def execute_operation(self, operation_type: OperationType, 
                              source: Path, destination: Optional[Path] = None,
                              options: Optional[Dict[str, Any]] = None) -> str:
        """Execute a single file operation and return operation ID."""
        pass
    
    @abstractmethod
    async def execute_batch(self, operations: List[Dict[str, Any]]) -> List[str]:
        """Execute multiple file operations in batch."""
        pass
    
    @abstractmethod
    async def get_operation_status(self, operation_id: str) -> OperationStatus:
        """Get the status of an operation."""
        pass
    
    @abstractmethod
    async def get_operation_result(self, operation_id: str) -> Optional[OperationResult]:
        """Get the result of a completed operation."""
        pass
    
    @abstractmethod
    async def cancel_operation(self, operation_id: str) -> bool:
        """Cancel a pending or in-progress operation."""
        pass
    
    @abstractmethod
    def subscribe_to_progress(self, operation_id: str) -> AsyncIterator[OperationProgress]:
        """Subscribe to progress updates for an operation."""
        pass


class IFileSystemMonitor(ABC):
    """Interface for monitoring file system changes."""
    
    @abstractmethod
    async def start_monitoring(self, paths: List[Path], 
                             recursive: bool = True) -> None:
        """Start monitoring file system changes."""
        pass
    
    @abstractmethod
    async def stop_monitoring(self) -> None:
        """Stop monitoring file system changes."""
        pass
    
    @abstractmethod
    def subscribe_to_changes(self) -> AsyncIterator[Dict[str, Any]]:
        """Subscribe to file system change events."""
        pass


class IBackupManager(ABC):
    """Interface for managing file backups before operations."""
    
    @abstractmethod
    async def create_backup(self, file_path: Path) -> Path:
        """Create a backup of a file before operation."""
        pass
    
    @abstractmethod
    async def restore_backup(self, backup_path: Path, original_path: Path) -> bool:
        """Restore a file from backup."""
        pass
    
    @abstractmethod
    async def cleanup_backups(self, older_than_days: int = 30) -> int:
        """Clean up old backup files."""
        pass


__all__ = [
    "OperationType",
    "OperationStatus", 
    "ConflictResolution",
    "OperationResult",
    "OperationProgress",
    "IFileOperationProvider",
    "IFileOperationManager",
    "IFileSystemMonitor",
    "IBackupManager",
]
