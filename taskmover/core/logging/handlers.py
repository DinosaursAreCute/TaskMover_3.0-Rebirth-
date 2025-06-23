"""
Log Handlers Implementation

Provides various handlers for different output destinations including console
with colors, rotating files with cleanup, and async handlers for performance.
"""

import gzip
import os
import sys
import threading
import time
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path
from queue import Empty, Queue
from typing import TextIO

from .exceptions import (
    CompressionError,
    FileRotationError,
    HandlerError,
    PermissionError,
)
from .formatters import ConsoleFormatter, FileFormatter, create_formatter
from .interfaces import ILogFormatter, ILogHandler, LogLevel, LogRecord


class BaseHandler(ILogHandler):
    """Base handler with common functionality"""

    def __init__(
        self, level: LogLevel = LogLevel.INFO, formatter: ILogFormatter | None = None
    ):
        self.level = level
        self.formatter = formatter or create_formatter("console")
        self._lock = threading.Lock()
        self._closed = False

    def handle(self, record: LogRecord) -> None:
        """Handle log record if level is appropriate"""
        if self._closed or record.level.value < self.level.value:
            return

        try:
            with self._lock:
                if not self._closed:
                    self._emit(record)
        except Exception as e:
            # Prevent handler errors from breaking the application
            self._handle_error(record, e)

    def _emit(self, record: LogRecord) -> None:
        """Emit log record - to be implemented by subclasses"""
        raise NotImplementedError("Subclasses must implement _emit")

    def _handle_error(self, record: LogRecord | None, error: Exception) -> None:
        """Handle errors that occur during logging"""
        try:
            # Try to write error to stderr
            error_msg = f"Logging error in {self.__class__.__name__}: {error}\n"
            sys.stderr.write(error_msg)
            sys.stderr.flush()
        except Exception:
            pass  # If even stderr fails, give up

    def set_formatter(self, formatter: ILogFormatter) -> None:
        """Set log formatter"""
        with self._lock:
            self.formatter = formatter

    def set_level(self, level: LogLevel) -> None:
        """Set minimum log level"""
        with self._lock:
            self.level = level

    def close(self) -> None:
        """Close handler and release resources"""
        with self._lock:
            self._closed = True


class ColoredConsoleHandler(BaseHandler):
    """Console handler with colored output and thread safety"""

    def __init__(
        self,
        stream: TextIO | None = None,
        use_colors: bool = True,
        use_emojis: bool = True,
        **kwargs,
    ):
        # Default to stdout
        self.stream = stream or sys.stdout

        # Auto-detect color support
        if use_colors:
            use_colors = self._supports_color()

        # Create console formatter
        formatter = ConsoleFormatter(
            use_colors=use_colors,
            use_emojis=use_emojis,
            compact=True,
            include_timestamp=True,
            include_component=True,
        )

        super().__init__(formatter=formatter, **kwargs)
        self.use_colors = use_colors

    def _supports_color(self) -> bool:
        """Check if terminal supports colors"""
        # Check common color environment variables
        if os.getenv("NO_COLOR"):
            return False

        if os.getenv("FORCE_COLOR"):
            return True

        # Check if stream is a TTY
        if hasattr(self.stream, "isatty") and self.stream.isatty():
            # Check terminal type
            term = os.getenv("TERM", "").lower()
            if any(x in term for x in ["color", "256", "xterm", "screen"]):
                return True

        return False

    def _emit(self, record: LogRecord) -> None:
        """Emit record to console"""
        try:
            message = self.formatter.format(record)
            self.stream.write(message + "\n")
            self.stream.flush()

        except Exception as e:
            raise HandlerError(
                f"Failed to write to console: {e}", component="console_handler"
            ) from e


class RotatingFileHandler(BaseHandler):
    """File handler with size and time-based rotation"""

    def __init__(
        self,
        filename: str,
        max_size: int = 10 * 1024 * 1024,  # 10MB
        backup_count: int = 5,
        rotation_time: str | None = None,
        compression: bool = True,
        encoding: str = "utf-8",
        **kwargs,
    ):
        self.filename = Path(filename)
        self.max_size = max_size
        self.backup_count = backup_count
        self.rotation_time = rotation_time  # 'midnight', 'hourly', etc.
        self.compression = compression
        self.encoding = encoding

        # Create directory if it doesn't exist
        self.filename.parent.mkdir(parents=True, exist_ok=True)

        # Current file handle
        self._file: TextIO | None = None
        self._current_size = 0
        self._last_rotation = datetime.now()

        # Create file formatter
        formatter = FileFormatter(
            detailed=True,
            include_context=True,
            include_timestamp=True,
            include_component=True,
        )

        super().__init__(formatter=formatter, **kwargs)  # Open initial file
        self._open_file()

    def _open_file(self) -> None:
        """Open log file for writing"""
        try:
            self._file = open(self.filename, "a", encoding=self.encoding)
            if self.filename.exists():
                self._current_size = self.filename.stat().st_size
            else:
                self._current_size = 0

        except PermissionError as e:
            raise PermissionError(
                f"Cannot open log file {self.filename}: {e}", component="file_handler"
            ) from e

    def _emit(self, record: LogRecord) -> None:
        """Emit record to file with rotation check"""
        try:
            # Check if rotation is needed
            if self._should_rotate():
                self._rotate()

            # Write to file
            if self._file:
                message = self.formatter.format(record)
                line = message + "\n"
                self._file.write(line)
                self._file.flush()
                self._current_size += len(line.encode(self.encoding))

        except Exception as e:
            raise HandlerError(
                f"Failed to write to file: {e}", component="file_handler"
            ) from e

    def _should_rotate(self) -> bool:
        """Check if file should be rotated"""
        # Size-based rotation
        if self._current_size >= self.max_size:
            return True

        # Time-based rotation
        if self.rotation_time:
            now = datetime.now()
            if self.rotation_time == "midnight":
                return now.date() > self._last_rotation.date()
            elif self.rotation_time == "hourly":
                return now.hour != self._last_rotation.hour

        return False

    def _rotate(self) -> None:
        """Rotate log files"""
        try:
            if self._file:
                self._file.close()
                self._file = None

            # Rename existing backup files
            for i in range(self.backup_count - 1, 0, -1):
                old_backup = self._get_backup_filename(i)
                new_backup = self._get_backup_filename(i + 1)

                if old_backup.exists():
                    if new_backup.exists():
                        new_backup.unlink()
                    old_backup.rename(new_backup)

            # Move current file to .1 backup
            if self.filename.exists():
                backup_file = self._get_backup_filename(1)
                if backup_file.exists():
                    backup_file.unlink()
                self.filename.rename(backup_file)

                # Compress backup if enabled
                if self.compression:
                    self._compress_file(backup_file)  # Open new file
            self._open_file()
            self._last_rotation = datetime.now()

        except Exception as e:
            raise FileRotationError(
                f"Failed to rotate log file: {e}", component="file_handler"
            ) from e

    def _get_backup_filename(self, index: int) -> Path:
        """Get backup filename for given index"""
        if self.compression:
            return self.filename.parent / f"{self.filename.name}.{index}.gz"
        else:
            return self.filename.parent / f"{self.filename.name}.{index}"

    def _compress_file(self, file_path: Path) -> None:
        """Compress log file using gzip"""
        try:
            compressed_path = file_path.with_suffix(file_path.suffix + ".gz")

            with open(file_path, "rb") as f_in:
                with gzip.open(compressed_path, "wb") as f_out:
                    f_out.writelines(f_in)  # Remove uncompressed file
            file_path.unlink()

        except Exception as e:
            raise CompressionError(
                f"Failed to compress {file_path}: {e}", component="file_handler"
            ) from e

    def close(self) -> None:
        """Close file handler"""
        super().close()
        if self._file:
            self._file.close()
            self._file = None


class AsyncHandler(BaseHandler):
    """Asynchronous handler for high-performance logging"""

    def __init__(
        self,
        target_handler: ILogHandler,
        queue_size: int = 1000,
        flush_interval: float = 1.0,
        **kwargs,
    ):
        super().__init__(**kwargs)

        self.target_handler = target_handler
        self.queue_size = queue_size
        self.flush_interval = flush_interval

        # Create queue and worker thread
        self._queue: Queue = Queue(maxsize=queue_size)
        self._worker_thread: threading.Thread | None = None
        self._shutdown_event = threading.Event()
        self._executor = ThreadPoolExecutor(
            max_workers=1, thread_name_prefix="async_logger"
        )

        # Start worker
        self._start_worker()

    def _start_worker(self) -> None:
        """Start background worker thread"""
        self._worker_thread = threading.Thread(
            target=self._worker_loop, name="AsyncLoggerWorker", daemon=True
        )
        self._worker_thread.start()

    def _worker_loop(self) -> None:
        """Background worker loop"""
        records_to_flush = []
        last_flush = time.time()

        while not self._shutdown_event.is_set():
            try:
                # Try to get record with timeout
                try:
                    record = self._queue.get(timeout=0.1)
                    if record is None:  # Shutdown signal
                        break
                    records_to_flush.append(record)
                except Empty:
                    pass

                # Flush if interval elapsed or queue is full
                now = time.time()
                if (
                    now - last_flush >= self.flush_interval
                    or len(records_to_flush) >= 100
                ):
                    self._flush_records(records_to_flush)
                    records_to_flush.clear()
                    last_flush = now

            except Exception as e:
                self._handle_error(None, e)  # Flush remaining records on shutdown
        if records_to_flush:
            self._flush_records(records_to_flush)

    def _flush_records(self, records: list[LogRecord]) -> None:
        """Flush accumulated records to target handler"""
        for record in records:
            try:
                self.target_handler.handle(record)
            except Exception as e:
                self._handle_error(record, e)

    def _emit(self, record: LogRecord) -> None:
        """Add record to async queue"""
        try:
            self._queue.put_nowait(record)

        except Exception:
            # Queue is full, handle synchronously as fallback
            try:
                self.target_handler.handle(record)
            except Exception as e:
                self._handle_error(record, e)

    def close(self) -> None:
        """Close async handler"""
        super().close()

        # Signal shutdown
        self._shutdown_event.set()

        # Put shutdown sentinel
        try:
            self._queue.put_nowait(None)
        except Exception:
            pass

        # Wait for worker to finish
        if self._worker_thread and self._worker_thread.is_alive():
            self._worker_thread.join(timeout=5.0)

        # Shutdown executor
        self._executor.shutdown(wait=True)

        # Close target handler
        if self.target_handler:
            self.target_handler.close()


class CleanupHandler(BaseHandler):
    """Handler that performs automatic log cleanup"""

    def __init__(
        self,
        log_directory: str,
        retention_days: int = 30,
        max_total_size: int | None = None,
        cleanup_interval: int = 24 * 3600,
        **kwargs,
    ):
        super().__init__(**kwargs)

        self.log_directory = Path(log_directory)
        self.retention_days = retention_days
        self.max_total_size = max_total_size  # In bytes
        self.cleanup_interval = cleanup_interval  # In seconds

        self._last_cleanup: float = 0.0

        # Ensure directory exists
        self.log_directory.mkdir(parents=True, exist_ok=True)

    def _emit(self, record: LogRecord) -> None:
        """Check if cleanup is needed"""
        now = time.time()
        if now - self._last_cleanup >= self.cleanup_interval:
            self._cleanup_logs()
            self._last_cleanup = now

    def _cleanup_logs(self) -> None:
        """Perform log cleanup"""
        try:
            self._cleanup_old_files()
            if self.max_total_size:
                self._cleanup_size_limit()
        except Exception as e:
            self._handle_error(None, e)

    def _cleanup_old_files(self) -> None:
        """Remove files older than retention period"""
        cutoff_time = time.time() - (self.retention_days * 24 * 3600)

        for log_file in self.log_directory.glob("*.log*"):
            try:
                if log_file.stat().st_mtime < cutoff_time:
                    log_file.unlink()
            except Exception as e:
                self._handle_error(None, e)

    def _cleanup_size_limit(self) -> None:
        """Remove oldest files if total size exceeds limit"""
        log_files = list(self.log_directory.glob("*.log*"))

        # Sort by modification time (oldest first)
        log_files.sort(key=lambda f: f.stat().st_mtime)

        total_size = sum(
            f.stat().st_size for f in log_files
        )  # Remove oldest files until under limit
        while (
            self.max_total_size is not None
            and total_size > self.max_total_size
            and log_files
        ):
            oldest_file = log_files.pop(0)
            try:
                file_size = oldest_file.stat().st_size
                oldest_file.unlink()
                total_size -= file_size
            except Exception as e:
                self._handle_error(None, e)


class MultiHandler(BaseHandler):
    """Handler that forwards to multiple sub-handlers"""

    def __init__(self, handlers: list[ILogHandler], **kwargs):
        super().__init__(**kwargs)
        self.handlers = handlers.copy()

    def _emit(self, record: LogRecord) -> None:
        """Emit to all handlers"""
        for handler in self.handlers:
            try:
                handler.handle(record)
            except Exception as e:
                self._handle_error(record, e)

    def add_handler(self, handler: ILogHandler) -> None:
        """Add handler"""
        with self._lock:
            if handler not in self.handlers:
                self.handlers.append(handler)

    def remove_handler(self, handler: ILogHandler) -> None:
        """Remove handler"""
        with self._lock:
            if handler in self.handlers:
                self.handlers.remove(handler)

    def close(self) -> None:
        """Close all handlers"""
        super().close()
        for handler in self.handlers:
            try:
                handler.close()
            except Exception:
                pass


class FilteredHandler(BaseHandler):
    """Handler that filters records based on component or custom criteria"""

    def __init__(
        self,
        target_handler: ILogHandler,
        allowed_components: list[str] | None = None,
        blocked_components: list[str] | None = None,
        custom_filter: Callable[[LogRecord], bool] | None = None,
        **kwargs,
    ):
        super().__init__(**kwargs)

        self.target_handler = target_handler
        self.allowed_components = set(allowed_components or [])
        self.blocked_components = set(blocked_components or [])
        self.custom_filter = custom_filter

    def _emit(self, record: LogRecord) -> None:
        """Emit if record passes filters"""
        # Check component filters
        if self.allowed_components and record.component not in self.allowed_components:
            return

        if self.blocked_components and record.component in self.blocked_components:
            return

        # Check custom filter
        if self.custom_filter and not self.custom_filter(record):
            return

        # Forward to target handler
        self.target_handler.handle(record)

    def close(self) -> None:
        """Close filtered handler"""
        super().close()
        if self.target_handler:
            self.target_handler.close()


# Handler factory for easy creation
def create_handler(handler_type: str = "console", **kwargs) -> ILogHandler:
    """Factory function to create handlers"""
    handlers = {
        "console": ColoredConsoleHandler,
        "file": RotatingFileHandler,
        "async": AsyncHandler,
        "cleanup": CleanupHandler,
        "multi": MultiHandler,
        "filtered": FilteredHandler,
    }

    handler_class = handlers.get(handler_type.lower())
    if not handler_class:
        raise ValueError(f"Unknown handler type: {handler_type}")

    return handler_class(**kwargs)
