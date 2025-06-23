"""
TaskMover Logging System Demonstration

This script demonstrates the capabilities of the TaskMover logging system
including different formatters, handlers, context management, and performance tracking.
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


def demonstrate_basic_logging():
    """Demonstrate basic logging functionality"""
    print("\n🚀 === BASIC LOGGING DEMONSTRATION ===")

    # Get loggers for different components
    ui_logger = get_logger("ui.theme")
    core_logger = get_logger("core.application")
    file_logger = get_logger("file_ops.organizer")

    print("\n📝 Logging at different levels:")

    # UI Theme logging
    ui_logger.debug("🔍 Debug: Theme system initializing...")
    ui_logger.info("ℹ️ Info: Successfully switched to dark theme")
    ui_logger.warning("⚠️ Warning: Custom theme file not found, using default")
    ui_logger.error("❌ Error: Failed to load theme configuration")

    # Core application logging
    core_logger.info(
        "🎯 Application startup sequence initiated",
        extra_data={
            "version": "1.0.0",
            "build": "2025.06.23",
            "startup_time": time.time(),
        },
    )

    # File operations logging
    file_logger.info(
        "📁 File organization started",
        extra_data={
            "source_directory": "/Users/example/Downloads",
            "rules_applied": 5,
            "files_to_process": 127,
        },
    )


def demonstrate_context_management():
    """Demonstrate logging context management"""
    print("\n🎯 === CONTEXT MANAGEMENT DEMONSTRATION ===")

    logger = get_logger("demo.context")

    print("\n🔗 Using logging context for operation tracking:")

    # Demonstrate context manager
    with log_context(
        operation="file_batch_organization",
        user="demo_user",
        batch_id="batch_20250623_001",
        source_count=50,
    ):
        logger.info("📦 Starting batch file organization")
        logger.info("🔍 Scanning source directory")
        logger.info("📋 Applied rules: extension_sort, date_organization")

        # Nested operation context
        with log_context(operation="pdf_processing", validator="adobe_preflight"):
            logger.info("📄 Processing PDF files")
            logger.warning("⚠️ PDF/A compliance issue detected")
            logger.info("✅ PDF processing completed")

        logger.info("✅ Batch organization completed successfully")

    logger.info("🧹 Operation context cleared")


def demonstrate_performance_tracking():
    """Demonstrate performance tracking"""
    print("\n⚡ === PERFORMANCE TRACKING DEMONSTRATION ===")

    logger = get_logger("demo.performance")

    print("\n⏱️ Performance timing with context manager:")

    # Performance timing context manager
    with log_performance("large_file_processing", logger, threshold_ms=10):
        time.sleep(0.05)  # Simulate 50ms operation
        logger.info("🗂️ Processing large document archive")

    print("\n🎯 Performance timing with decorator:")

    # Performance timing decorator
    @performance_timer("file_sorting_algorithm", threshold_ms=1)
    def sort_files_by_date():
        """Simulate file sorting operation"""
        time.sleep(0.02)  # Simulate 20ms operation
        files = [f"document_{i:03d}.pdf" for i in range(1, 26)]
        return sorted(files)

    sorted_files = sort_files_by_date()
    logger.info(
        "📊 File sorting completed",
        extra_data={
            "files_sorted": len(sorted_files),
            "algorithm": "date_modified_desc",
        },
    )


def demonstrate_error_handling():
    """Demonstrate error handling and exception logging"""
    print("\n🚨 === ERROR HANDLING DEMONSTRATION ===")

    logger = get_logger("demo.errors")

    print("\n❌ Simulating various error scenarios:")

    # Simulate file operation error
    try:
        raise FileNotFoundError("Source file 'important_document.pdf' not found")
    except Exception as e:
        logger.error(
            "📁 File operation failed",
            exception=e,
            extra_data={
                "operation": "copy_file",
                "source": "important_document.pdf",
                "destination": "/backup/documents/",
                "retry_count": 3,
            },
        )

    # Simulate permission error
    logger.error(
        "🔒 Permission denied",
        extra_data={
            "operation": "create_directory",
            "path": "/restricted/system_files/",
            "required_permission": "write",
            "current_user": "demo_user",
        },
    )

    # Simulate critical system error
    logger.critical(
        "💥 Critical system error detected",
        extra_data={
            "error_type": "memory_exhaustion",
            "available_memory": "< 100MB",
            "process_count": 156,
            "action_taken": "emergency_cleanup",
        },
    )


def demonstrate_file_logging():
    """Demonstrate file logging with rotation"""
    print("\n📄 === FILE LOGGING DEMONSTRATION ===")

    print("\n💾 Setting up file logging with rotation...")

    with tempfile.TemporaryDirectory() as temp_dir:
        log_file = Path(temp_dir) / "demo_application.log"

        # Create custom configuration for demonstration
        config = LoggingConfig(
            level=LogLevel.DEBUG,
            console=ConsoleConfig(enabled=True, colors=True, format="compact"),
            file=FileConfig(
                enabled=True,
                path=str(log_file),
                rotation=FileRotationConfig(
                    max_size="2KB",  # Very small for demo rotation
                    backup_count=3,
                    retention_days=1,
                    compression_enabled=False,  # Disabled for easy viewing
                ),
                format="detailed",
            ),
            components={"demo": LogLevel.DEBUG},
            session_tracking=True,
            performance_monitoring=True,
        )

        # Configure logging manager
        manager = LoggerManager()
        manager.configure(config)

        logger = get_logger("demo.file_logging")

        # Generate logs to trigger rotation
        print("📝 Generating log entries to demonstrate rotation...")
        for i in range(15):
            logger.info(
                f"📋 Log entry {i+1:02d}: Processing item batch with detailed information about the operation",
                extra_data={
                    "batch_number": i + 1,
                    "items_processed": (i + 1) * 10,
                    "status": "active",
                },
            )

            if (i + 1) % 5 == 0:
                logger.warning(
                    f"⚠️ Checkpoint {i+1}: Memory usage increasing",
                    extra_data={"memory_usage_mb": 150 + (i * 10), "threshold_mb": 500},
                )

        # IMPORTANT: Shutdown logging first to close file handles
        print("🔒 Shutting down logging system...")
        manager.shutdown()

        # Small delay to ensure files are properly closed on Windows
        time.sleep(0.1)

        # Show file system results
        print("\n📊 File logging results:")
        print(f"   Log file: {log_file}")

        if log_file.exists():
            try:
                file_size = log_file.stat().st_size
                print(f"   File size: {file_size} bytes")

                # Check for rotated files
                backup_files = list(log_file.parent.glob(f"{log_file.name}.*"))
                print(f"   Backup files created: {len(backup_files)}")

                for backup in sorted(backup_files):
                    try:
                        backup_size = backup.stat().st_size
                        print(f"     {backup.name}: {backup_size} bytes")
                    except Exception as e:
                        print(f"     {backup.name}: <size unavailable - {e}>")

                # Show last few lines of current log with proper encoding
                try:
                    content = log_file.read_text(encoding="utf-8")
                    lines = content.strip().split("\n")
                    print(f"   Total lines in current log: {len(lines)}")
                    print("   📄 Last 3 log entries:")
                    for line in lines[-3:]:
                        if line.strip():
                            print(f"     {line}")
                except UnicodeDecodeError:
                    # Fallback to binary read if UTF-8 fails
                    print("   📄 Log content (binary mode due to encoding issues):")
                    with open(log_file, "rb") as f:
                        content = f.read()
                        print(f"     File contains {len(content)} bytes")
                except Exception as e:
                    print(f"   ⚠️ Could not read log content: {e}")

            except Exception as e:
                print(f"   ⚠️ Error accessing log file: {e}")
        else:
            print("   ⚠️ Log file was not created")


def demonstrate_component_filtering():
    """Demonstrate component-specific log filtering"""
    print("\n🏷️ === COMPONENT FILTERING DEMONSTRATION ===")

    print("\n🎯 Different components with different log levels:")

    # Get loggers for different components
    ui_logger = get_logger("ui.components")
    core_logger = get_logger("core.engine")
    debug_logger = get_logger("debug.trace")
    build_logger = get_logger("build.assets")

    # UI component messages (typically INFO+)
    ui_logger.debug("🔍 UI Debug: Button hover state changed")  # May be filtered
    ui_logger.info("ℹ️ UI Info: Modal dialog opened")
    ui_logger.warning("⚠️ UI Warning: Accessibility issue detected")

    # Core engine messages (typically INFO+)
    core_logger.debug("🔍 Core Debug: Internal state updated")  # May be filtered
    core_logger.info("ℹ️ Core Info: Task engine started")
    core_logger.error("❌ Core Error: Task execution failed")

    # Debug component (typically DEBUG+)
    debug_logger.debug("🔍 Debug Trace: Variable state dump")
    debug_logger.info("ℹ️ Debug Info: Breakpoint reached")

    # Build component (typically WARNING+ only)
    build_logger.debug("🔍 Build Debug: Asset hashing")  # Likely filtered
    build_logger.info("ℹ️ Build Info: Compiling assets")  # Likely filtered
    build_logger.warning("⚠️ Build Warning: Asset size large")
    build_logger.error("❌ Build Error: Asset compilation failed")


def main():
    """Run all demonstrations"""
    print("🎉 TaskMover Logging System Demonstration")
    print("=" * 65)
    print("This demo shows the comprehensive logging capabilities of TaskMover")

    try:
        demonstrate_basic_logging()
        demonstrate_context_management()
        demonstrate_performance_tracking()
        demonstrate_error_handling()
        demonstrate_file_logging()
        demonstrate_component_filtering()

        print("\n" + "=" * 65)
        print("🏆 Demonstration completed successfully!")
        print("\n✨ The TaskMover logging system provides:")
        print("   • 📊 Multiple output formats (console, file, JSON)")
        print("   • 🎨 Colored console output with emojis")
        print("   • 🔄 Automatic log rotation and cleanup")
        print("   • 🎯 Component-based filtering")
        print("   • 🔗 Context management for operation tracking")
        print("   • ⚡ Performance monitoring and timing")
        print("   • 🚨 Comprehensive error handling")
        print("   • 🛡️ Thread-safe singleton architecture")
        print("   • ⚙️ Configurable via YAML files")
        print("\n🚀 Ready for production use in TaskMover!")

    except Exception as e:
        print(f"\n💥 Demonstration failed: {e}")
        import traceback

        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
