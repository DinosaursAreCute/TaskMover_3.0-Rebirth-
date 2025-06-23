"""
Quick validation script to test the logging system fixes
"""

import tempfile
import time
from pathlib import Path

from taskmover.core.logging import get_logger
from taskmover.core.logging.config import (
    ConsoleConfig,
    FileConfig,
    FileRotationConfig,
    LoggingConfig,
    LogLevel,
)
from taskmover.core.logging.manager import LoggerManager


def test_file_handling_fix():
    """Test that file handling issues are fixed"""
    print("Testing file handling fixes...")

    with tempfile.TemporaryDirectory() as temp_dir:
        log_file = Path(temp_dir) / "test.log"

        # Create simple config
        console_config = ConsoleConfig(enabled=True, colors=True, format="compact")
        file_rotation_config = FileRotationConfig(
            max_size="500B", backup_count=2, compression_enabled=False
        )
        file_config = FileConfig(
            enabled=True,
            path=str(log_file),
            rotation=file_rotation_config,
            format="detailed",
        )

        config = LoggingConfig()
        config.level = LogLevel.DEBUG
        config.console = console_config
        config.file = file_config
        config.components = {"test": LogLevel.DEBUG}
        config.session_tracking = True
        config.performance_monitoring = True

        # Configure logging
        manager = LoggerManager()
        manager.configure(config)

        logger = get_logger("test.validation")

        # Generate some logs
        for i in range(5):
            logger.info(f"Test log message {i+1} with some content to fill the file")

        # Properly shutdown BEFORE trying to read files
        print("Shutting down logging system...")
        manager.shutdown()

        # Give Windows time to release file handles
        time.sleep(0.1)

        # Now try to read the file
        if log_file.exists():
            try:
                content = log_file.read_text(encoding="utf-8")
                lines = content.strip().split("\n")
                print(f"✅ Successfully read log file: {len(lines)} lines")
                print(f"✅ File size: {log_file.stat().st_size} bytes")

                # Check for backup files
                backup_files = list(log_file.parent.glob(f"{log_file.name}.*"))
                if backup_files:
                    print(f"✅ Backup files created: {len(backup_files)}")

                print("✅ File handling test PASSED")
                return True

            except Exception as e:
                print(f"❌ Failed to read log file: {e}")
                return False
        else:
            print("❌ Log file was not created")
            return False


if __name__ == "__main__":
    print("🧪 TaskMover Logging System - File Handling Validation")
    print("=" * 60)

    try:
        success = test_file_handling_fix()
        if success:
            print("\n🎉 All fixes validated successfully!")
            print("The logging system file handling issues have been resolved.")
        else:
            print("\n❌ Some issues remain - please review the output above.")
            exit(1)
    except Exception as e:
        print(f"\n💥 Validation failed: {e}")
        import traceback

        traceback.print_exc()
        exit(1)
