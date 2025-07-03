"""
File Operations Manager
======================

Core implementation of file operations with detailed logging,
progress tracking, and error handling.
"""

import asyncio
import shutil
import os
from pathlib import Path
from typing import Dict, List, Optional, Any, AsyncIterator
from uuid import uuid4
from datetime import datetime
import time
import hashlib
from concurrent.futures import ThreadPoolExecutor

from ..logging import get_logger
from . import (
    IFileOperationManager, IFileOperationProvider, IBackupManager,
    OperationType, OperationStatus, OperationResult, OperationProgress,
    ConflictResolution
)


class FileOperationManager(IFileOperationManager):
    """
    Main file operations manager implementing asynchronous file operations
    with progress tracking and detailed logging.
    """
    
    def __init__(self, 
                 provider: Optional[IFileOperationProvider] = None,
                 backup_manager: Optional[IBackupManager] = None,
                 max_workers: int = 4):
        self._logger = get_logger("file_operations.manager")
        self._provider = provider or LocalFileOperationProvider()
        self._backup_manager = backup_manager
        self._max_workers = max_workers
        self._executor = ThreadPoolExecutor(max_workers=max_workers)
        
        # Operation tracking
        self._operations: Dict[str, OperationResult] = {}
        self._progress_callbacks: Dict[str, List[asyncio.Queue]] = {}
        self._operation_locks: Dict[str, asyncio.Lock] = {}
        
        self._logger.info(f"FileOperationManager initialized with {max_workers} workers")
    
    async def execute_operation(self, 
                              operation_type: OperationType,
                              source: Path, 
                              destination: Optional[Path] = None,
                              options: Optional[Dict[str, Any]] = None) -> str:
        """Execute a single file operation."""
        operation_id = str(uuid4())
        options = options or {}
        
        self._logger.info(
            f"Starting {operation_type.value} operation",
            extra={
                "operation_id": operation_id,
                "source": str(source),
                "destination": str(destination) if destination else None,
                "options": options
            }
        )
        
        # Initialize operation tracking
        self._operations[operation_id] = OperationResult(
            operation_id=operation_id,
            operation_type=operation_type,
            source_path=source,
            destination_path=destination,
            status=OperationStatus.PENDING,
            success=False
        )
        self._progress_callbacks[operation_id] = []
        self._operation_locks[operation_id] = asyncio.Lock()
        
        # Execute operation asynchronously
        asyncio.create_task(self._execute_operation_internal(operation_id, options))
        
        return operation_id
    
    async def _execute_operation_internal(self, operation_id: str, options: Dict[str, Any]):
        """Internal method to execute operation with error handling."""
        operation = self._operations[operation_id]
        start_time = time.time()
        
        try:
            async with self._operation_locks[operation_id]:
                # Update status to in progress
                operation.status = OperationStatus.IN_PROGRESS
                await self._notify_progress(operation_id, 0, 0)
                
                # Create backup if enabled
                if options.get('create_backup', False) and self._backup_manager:
                    if operation.source_path and operation.source_path.exists():
                        backup_path = await self._backup_manager.create_backup(operation.source_path)
                        operation.metadata['backup_path'] = str(backup_path)
                        self._logger.debug(f"Created backup at {backup_path}", extra={"operation_id": operation_id})
                
                # Execute the actual operation
                if operation.operation_type == OperationType.COPY:
                    result = await self._provider.copy_file(
                        operation.source_path, 
                        operation.destination_path,
                        preserve_metadata=options.get('preserve_metadata', True)
                    )
                elif operation.operation_type == OperationType.MOVE:
                    result = await self._provider.move_file(
                        operation.source_path,
                        operation.destination_path
                    )
                elif operation.operation_type == OperationType.DELETE:
                    result = await self._provider.delete_file(
                        operation.source_path,
                        use_recycle_bin=options.get('use_recycle_bin', True)
                    )
                else:
                    raise ValueError(f"Unsupported operation type: {operation.operation_type}")
                
                # Update operation with result
                operation.status = result.status
                operation.success = result.success
                operation.error_message = result.error_message
                operation.bytes_processed = result.bytes_processed
                operation.duration_seconds = time.time() - start_time
                
                if result.metadata:
                    operation.metadata.update(result.metadata)
                
                self._logger.info(
                    f"Operation {operation.operation_type.value} completed",
                    extra={
                        "operation_id": operation_id,
                        "success": operation.success,
                        "duration": operation.duration_seconds,
                        "bytes_processed": operation.bytes_processed
                    }
                )
                
                # Final progress notification
                await self._notify_progress(operation_id, operation.bytes_processed, operation.bytes_processed)
                
        except Exception as e:
            operation.status = OperationStatus.FAILED
            operation.success = False
            operation.error_message = str(e)
            operation.duration_seconds = time.time() - start_time
            
            self._logger.error(
                f"Operation {operation.operation_type.value} failed: {e}",
                extra={
                    "operation_id": operation_id,
                    "error": str(e),
                    "duration": operation.duration_seconds
                }
            )
        
        finally:
            # Cleanup progress callbacks
            if operation_id in self._progress_callbacks:
                for queue in self._progress_callbacks[operation_id]:
                    try:
                        queue.put_nowait(None)  # Signal completion
                    except asyncio.QueueFull:
                        pass
                del self._progress_callbacks[operation_id]
            
            if operation_id in self._operation_locks:
                del self._operation_locks[operation_id]
    
    async def execute_batch(self, operations: List[Dict[str, Any]]) -> List[str]:
        """Execute multiple file operations in batch."""
        self._logger.info(f"Starting batch operation with {len(operations)} operations")
        
        operation_ids = []
        for op_data in operations:
            operation_id = await self.execute_operation(
                operation_type=OperationType(op_data['type']),
                source=Path(op_data['source']),
                destination=Path(op_data['destination']) if op_data.get('destination') else None,
                options=op_data.get('options', {})
            )
            operation_ids.append(operation_id)
        
        return operation_ids
    
    async def get_operation_status(self, operation_id: str) -> OperationStatus:
        """Get the status of an operation."""
        if operation_id not in self._operations:
            raise ValueError(f"Operation {operation_id} not found")
        
        return self._operations[operation_id].status
    
    async def get_operation_result(self, operation_id: str) -> Optional[OperationResult]:
        """Get the result of a completed operation."""
        return self._operations.get(operation_id)
    
    async def cancel_operation(self, operation_id: str) -> bool:
        """Cancel a pending or in-progress operation."""
        if operation_id not in self._operations:
            return False
        
        operation = self._operations[operation_id]
        if operation.status in [OperationStatus.COMPLETED, OperationStatus.FAILED, OperationStatus.CANCELLED]:
            return False
        
        operation.status = OperationStatus.CANCELLED
        operation.success = False
        operation.error_message = "Operation cancelled by user"
        
        self._logger.info(f"Operation {operation_id} cancelled", extra={"operation_id": operation_id})
        return True
    
    async def subscribe_to_progress(self, operation_id: str) -> AsyncIterator[OperationProgress]:
        """Subscribe to progress updates for an operation."""
        if operation_id not in self._operations:
            raise ValueError(f"Operation {operation_id} not found")
        
        progress_queue = asyncio.Queue(maxsize=100)
        self._progress_callbacks[operation_id].append(progress_queue)
        
        try:
            while True:
                progress = await progress_queue.get()
                if progress is None:  # Completion signal
                    break
                yield progress
        except asyncio.CancelledError:
            # Remove callback on cancellation
            if operation_id in self._progress_callbacks:
                try:
                    self._progress_callbacks[operation_id].remove(progress_queue)
                except ValueError:
                    pass
            raise
    
    async def _notify_progress(self, operation_id: str, processed_bytes: int, total_bytes: int):
        """Notify all subscribers of progress update."""
        if operation_id not in self._progress_callbacks:
            return
        
        operation = self._operations[operation_id]
        current_time = time.time()
        
        # Calculate speed (simplified)
        speed = processed_bytes / max(operation.duration_seconds, 0.001)
        eta = (total_bytes - processed_bytes) / max(speed, 1)
        
        progress = OperationProgress(
            operation_id=operation_id,
            total_bytes=total_bytes,
            processed_bytes=processed_bytes,
            current_file=operation.source_path,
            files_processed=1 if processed_bytes > 0 else 0,
            total_files=1,
            speed_bytes_per_second=speed,
            estimated_time_remaining=eta
        )
        
        for queue in self._progress_callbacks[operation_id]:
            try:
                queue.put_nowait(progress)
            except asyncio.QueueFull:
                # Skip if queue is full
                pass


class LocalFileOperationProvider(IFileOperationProvider):
    """Local file system operation provider."""
    
    def __init__(self):
        self._logger = get_logger("file_operations.local_provider")
    
    async def copy_file(self, source: Path, destination: Path, 
                       preserve_metadata: bool = True) -> OperationResult:
        """Copy a single file using asyncio."""
        operation_id = str(uuid4())
        start_time = time.time()
        
        try:
            self._logger.debug(f"Copying file {source} to {destination}", extra={"operation_id": operation_id})
            
            # Ensure destination directory exists
            destination.parent.mkdir(parents=True, exist_ok=True)
            
            # Get file size for progress tracking
            file_size = source.stat().st_size
            
            # Use asyncio to run blocking operation in thread pool
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, shutil.copy2 if preserve_metadata else shutil.copy, 
                                     str(source), str(destination))
            
            duration = time.time() - start_time
            
            self._logger.info(
                f"File copied successfully in {duration:.2f}s",
                extra={
                    "operation_id": operation_id,
                    "source": str(source),
                    "destination": str(destination),
                    "size_bytes": file_size,
                    "duration": duration
                }
            )
            
            return OperationResult(
                operation_id=operation_id,
                operation_type=OperationType.COPY,
                source_path=source,
                destination_path=destination,
                status=OperationStatus.COMPLETED,
                success=True,
                bytes_processed=file_size,
                duration_seconds=duration
            )
            
        except Exception as e:
            duration = time.time() - start_time
            
            self._logger.error(
                f"Failed to copy file: {e}",
                extra={
                    "operation_id": operation_id,
                    "source": str(source),
                    "destination": str(destination),
                    "error": str(e),
                    "duration": duration
                }
            )
            
            return OperationResult(
                operation_id=operation_id,
                operation_type=OperationType.COPY,
                source_path=source,
                destination_path=destination,
                status=OperationStatus.FAILED,
                success=False,
                error_message=str(e),
                duration_seconds=duration
            )
    
    async def move_file(self, source: Path, destination: Path) -> OperationResult:
        """Move a single file."""
        operation_id = str(uuid4())
        start_time = time.time()
        
        try:
            self._logger.debug(f"Moving file {source} to {destination}", extra={"operation_id": operation_id})
            
            # Ensure destination directory exists
            destination.parent.mkdir(parents=True, exist_ok=True)
            
            # Get file size for tracking
            file_size = source.stat().st_size
            
            # Use asyncio to run blocking operation
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, shutil.move, str(source), str(destination))
            
            duration = time.time() - start_time
            
            self._logger.info(
                f"File moved successfully in {duration:.2f}s",
                extra={
                    "operation_id": operation_id,
                    "source": str(source),
                    "destination": str(destination),
                    "size_bytes": file_size,
                    "duration": duration
                }
            )
            
            return OperationResult(
                operation_id=operation_id,
                operation_type=OperationType.MOVE,
                source_path=source,
                destination_path=destination,
                status=OperationStatus.COMPLETED,
                success=True,
                bytes_processed=file_size,
                duration_seconds=duration
            )
            
        except Exception as e:
            duration = time.time() - start_time
            
            self._logger.error(
                f"Failed to move file: {e}",
                extra={
                    "operation_id": operation_id,
                    "source": str(source),
                    "destination": str(destination),
                    "error": str(e),
                    "duration": duration
                }
            )
            
            return OperationResult(
                operation_id=operation_id,
                operation_type=OperationType.MOVE,
                source_path=source,
                destination_path=destination,
                status=OperationStatus.FAILED,
                success=False,
                error_message=str(e),
                duration_seconds=duration
            )
    
    async def delete_file(self, file_path: Path, use_recycle_bin: bool = True) -> OperationResult:
        """Delete a single file."""
        operation_id = str(uuid4())
        start_time = time.time()
        
        try:
            self._logger.debug(f"Deleting file {file_path}", extra={"operation_id": operation_id})
            
            file_size = file_path.stat().st_size if file_path.exists() else 0
            
            if use_recycle_bin:
                # Try to use system recycle bin (platform-specific)
                try:
                    import send2trash
                    loop = asyncio.get_event_loop()
                    await loop.run_in_executor(None, send2trash.send2trash, str(file_path))
                except ImportError:
                    # Fallback to regular deletion
                    self._logger.warning("send2trash not available, using regular deletion")
                    loop = asyncio.get_event_loop()
                    await loop.run_in_executor(None, file_path.unlink)
            else:
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(None, file_path.unlink)
            
            duration = time.time() - start_time
            
            self._logger.info(
                f"File deleted successfully in {duration:.2f}s",
                extra={
                    "operation_id": operation_id,
                    "file_path": str(file_path),
                    "size_bytes": file_size,
                    "use_recycle_bin": use_recycle_bin,
                    "duration": duration
                }
            )
            
            return OperationResult(
                operation_id=operation_id,
                operation_type=OperationType.DELETE,
                source_path=file_path,
                destination_path=None,
                status=OperationStatus.COMPLETED,
                success=True,
                bytes_processed=file_size,
                duration_seconds=duration
            )
            
        except Exception as e:
            duration = time.time() - start_time
            
            self._logger.error(
                f"Failed to delete file: {e}",
                extra={
                    "operation_id": operation_id,
                    "file_path": str(file_path),
                    "error": str(e),
                    "duration": duration
                }
            )
            
            return OperationResult(
                operation_id=operation_id,
                operation_type=OperationType.DELETE,
                source_path=file_path,
                destination_path=None,
                status=OperationStatus.FAILED,
                success=False,
                error_message=str(e),
                duration_seconds=duration
            )
    
    async def create_directory(self, directory_path: Path, parents: bool = True) -> OperationResult:
        """Create a directory."""
        operation_id = str(uuid4())
        start_time = time.time()
        
        try:
            self._logger.debug(f"Creating directory {directory_path}", extra={"operation_id": operation_id})
            
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, directory_path.mkdir, parents, True)
            
            duration = time.time() - start_time
            
            self._logger.info(
                f"Directory created successfully in {duration:.2f}s",
                extra={
                    "operation_id": operation_id,
                    "directory_path": str(directory_path),
                    "duration": duration
                }
            )
            
            return OperationResult(
                operation_id=operation_id,
                operation_type=OperationType.CREATE,
                source_path=None,
                destination_path=directory_path,
                status=OperationStatus.COMPLETED,
                success=True,
                duration_seconds=duration
            )
            
        except Exception as e:
            duration = time.time() - start_time
            
            self._logger.error(
                f"Failed to create directory: {e}",
                extra={
                    "operation_id": operation_id,
                    "directory_path": str(directory_path),
                    "error": str(e),
                    "duration": duration
                }
            )
            
            return OperationResult(
                operation_id=operation_id,
                operation_type=OperationType.CREATE,
                source_path=None,
                destination_path=directory_path,
                status=OperationStatus.FAILED,
                success=False,
                error_message=str(e),
                duration_seconds=duration
            )
    
    async def get_file_info(self, file_path: Path) -> Dict[str, Any]:
        """Get file metadata and information."""
        try:
            stat = file_path.stat()
            return {
                "size_bytes": stat.st_size,
                "modified_time": datetime.fromtimestamp(stat.st_mtime),
                "created_time": datetime.fromtimestamp(stat.st_ctime),
                "accessed_time": datetime.fromtimestamp(stat.st_atime),
                "is_file": file_path.is_file(),
                "is_directory": file_path.is_dir(),
                "permissions": oct(stat.st_mode)[-3:],
                "exists": file_path.exists()
            }
        except Exception as e:
            self._logger.error(f"Failed to get file info for {file_path}: {e}")
            return {"exists": False, "error": str(e)}


__all__ = ["FileOperationManager", "LocalFileOperationProvider"]
