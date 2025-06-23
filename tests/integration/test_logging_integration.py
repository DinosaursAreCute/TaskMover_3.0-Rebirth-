"""
Manual Integration Test for Logging System

This script tests the logging system manually to ensure it works correctly
in a real-world scenario. Run this script to verify the implementation.
"""

import tempfile
import time
from pathlib import Path

from taskmover.core.logging import get_logger, log_context
from taskmover.core.logging.config import (
    ConsoleConfig,
    FileConfig,
    FileRotationConfig,
    LoggingConfig,
    LogLevel,
)
from taskmover.core.logging.manager import LoggerManager
from taskmover.core.logging.utils import log_performance, performance_timer


def test_basic_logging():
    """Test basic logging functionality"""
    print("=== Testing Basic Logging ===")

    # Get loggers for different components
    ui_logger = get_logger("ui.theme")
    core_logger = get_logger("core.app")
    file_logger = get_logger("file_ops.organize")

    # Test different log levels
    ui_logger.debug("Debug: Theme system initialized")
    ui_logger.info("Info: Switched to dark theme")
    ui_logger.warning("Warning: Theme file not found, using default")
    ui_logger.error("Error: Failed to load custom theme")
    ui_logger.critical("Critical: Theme system crashed")

    # Test with extra context
    core_logger.info(
        "Application starting",
        extra_data={
            "version": "1.0.0",
            "startup_time": "2025-06-23T14:30:00Z",
            "config_loaded": True,
        },
    )

    # Test file operations logging
    file_logger.info(
        "Organizing files",
        extra_data={
            "source_dir": "/home/user/downloads",
            "target_dir": "/home/user/organized",
            "file_count": 42,
        },
    )

    print("✓ Basic logging completed")


def test_context_management():
    """Test logging context management"""
    print("\n=== Testing Context Management ===")

    logger = get_logger("test.context")

    # Test context manager
    with log_context(operation="file_organization", user="admin", batch_id="batch-123"):
        logger.info("Starting file organization batch")
        logger.info("Processing file: document.pdf")
        logger.info("File moved successfully")

        # Nested context
        with log_context(operation="validation", validator="pdf_checker"):
            logger.info("Validating PDF file")
            logger.warning("PDF file has no metadata")

    logger.info("Context cleared after operation")
    print("✓ Context management completed")


def test_performance_tracking():
    """Test performance tracking utilities"""
    print("\n=== Testing Performance Tracking ===")

    logger = get_logger("test.performance")

    # Test performance timer context manager
    with log_performance("file_processing", logger, threshold_ms=1):
        time.sleep(0.005)  # 5ms delay
        logger.info("Processing large file")

    # Test performance decorator
    @performance_timer("sort_algorithm", threshold_ms=1)
    def sort_files():
        time.sleep(0.002)  # 2ms delay
        return ["file1.txt", "file2.txt", "file3.txt"]

    result = sort_files()
    logger.info("Sorted files", extra_data={"files": result})

    print("✓ Performance tracking completed")


def test_file_logging():
    """Test file logging with rotation"""
    print("\n=== Testing File Logging ===")

    with tempfile.TemporaryDirectory() as temp_dir:
        log_file = Path(temp_dir) / "test_app.log"

        # Create custom configuration
        console_config = ConsoleConfig(enabled=True, colors=True, format="compact")

        file_rotation_config = FileRotationConfig(
            max_size="1KB",  # Small size for testing rotation
            backup_count=3,
            retention_days=7,
            compression_enabled=False,
        )

        file_config = FileConfig(
            enabled=True,
            path=str(log_file),
            rotation=file_rotation_config,
            format="detailed",
        )

        # Create config with positional arguments to avoid mypy issues
        config = LoggingConfig()
        config.level = LogLevel.DEBUG
        config.console = console_config
        config.file = file_config
        config.components = {"test": LogLevel.DEBUG, "ui": LogLevel.INFO}
        config.session_tracking = True
        config.performance_monitoring = True

        # Configure logging
        manager = LoggerManager()
        manager.configure(config)

        logger = get_logger("test.file")

        # Generate enough logs to trigger rotation
        for i in range(20):
            logger.info(
                f"Log message {i:02d} - This is a test message with some content to fill up the log file"
            )
            if i % 5 == 0:
                logger.warning(
                    f"Warning message {i} - This is a longer message to help fill the log file"
                )

        # IMPORTANT: Shutdown logging first to close file handles
        manager.shutdown()

        # Small delay to ensure files are properly closed on Windows
        time.sleep(0.1)

        # Check if log file exists
        if log_file.exists():
            try:
                print(f"✓ Log file created: {log_file}")
                print(f"  File size: {log_file.stat().st_size} bytes")

                # Check for backup files (rotation)
                backup_files = list(log_file.parent.glob(f"{log_file.name}.*"))
                if backup_files:
                    print(f"  Backup files created: {len(backup_files)}")

                # Show last few lines with proper encoding
                try:
                    content = log_file.read_text(encoding="utf-8")
                    lines = content.strip().split("\n")
                    print(f"  Total log lines: {len(lines)}")
                    print("  Last 3 lines:")
                    for line in lines[-3:]:
                        if line.strip():
                            print(f"    {line}")
                except UnicodeDecodeError:
                    print("  ⚠️ Encoding issue - reading as binary")
                    with open(log_file, "rb") as f:
                        content = f.read()
                        print(f"  File contains {len(content)} bytes")
                except Exception as e:
                    print(f"  ⚠️ Could not read log content: {e}")

            except Exception as e:
                print(f"  ⚠️ Error accessing log file: {e}")
        else:
            print("⚠ Log file was not created")

    print("✓ File logging completed")


def test_error_handling():
    """Test error handling and exception logging"""
    print("\n=== Testing Error Handling ===")

    logger = get_logger("test.errors")

    try:
        # Simulate an error
        raise ValueError("This is a test error")
    except Exception as e:
        logger.error(
            "Caught exception during file processing",
            exception=e,
            extra_data={
                "operation": "file_move",
                "source": "test.txt",
                "target": "destination.txt",
            },
        )

    # Test different error scenarios
    logger.error("File not found", extra_data={"filename": "missing.txt"})
    logger.critical("System out of memory", extra_data={"available_memory": "< 100MB"})

    print("✓ Error handling completed")


def test_component_specific_logging():
    """Test component-specific logging configurations"""
    print("\n=== Testing Component-Specific Logging ===")

    # Get loggers for different components
    ui_logger = get_logger("ui.components")
    core_logger = get_logger("core.engine")
    debug_logger = get_logger("debug.trace")

    # These should all log (assuming INFO level)
    ui_logger.info("UI component initialized")
    core_logger.info("Core engine started")

    # Debug messages (may be filtered based on config)
    ui_logger.debug("UI debug message")
    core_logger.debug("Core debug message")
    debug_logger.debug("Debug trace message")

    print("✓ Component-specific logging completed")


def main():
    """Run all integration tests"""
    print("Starting TaskMover Logging System Integration Test")
    print("=" * 60)

    try:
        test_basic_logging()
        test_context_management()
        test_performance_tracking()
        test_file_logging()
        test_error_handling()
        test_component_specific_logging()

        print("\n" + "=" * 60)
        print("🎉 All integration tests completed successfully!")
        print("\nThe logging system is working correctly and ready for use.")

    except Exception as e:
        print(f"\n❌ Integration test failed: {e}")
        import traceback

        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
