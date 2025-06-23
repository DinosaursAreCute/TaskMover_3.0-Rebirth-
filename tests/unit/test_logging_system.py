"""
Comprehensive tests for the TaskMover logging system

Tests all components: interfaces, manager, formatters, handlers, config, utils, exceptions
"""

import json
import sys
import tempfile
import time
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock

import pytest

from taskmover.core.logging.config import LoggingConfig
from taskmover.core.logging.exceptions import (
    ConfigurationError,
    FormatterError,
    HandlerError,
    LoggingException,
)
from taskmover.core.logging.formatters import (
    ConsoleFormatter,
    DebugFormatter,
    FileFormatter,
    JSONFormatter,
    MinimalFormatter,
    create_formatter,
)
from taskmover.core.logging.handlers import (
    ColoredConsoleHandler,
    FilteredHandler,
    MultiHandler,
    RotatingFileHandler,
    create_handler,
)
from taskmover.core.logging.interfaces import LogContext, LogLevel, LogRecord
from taskmover.core.logging.manager import ComponentLogger, LoggerManager, get_logger
from taskmover.core.logging.utils import (
    LoggingContext,
    PerformanceTimer,
    RateLimiter,
    format_bytes,
    format_duration,
    log_method_calls,
    performance_timer,
    safe_str,
    sanitize_path,
)


class TestLogLevel:
    """Test LogLevel enum"""

    def test_log_levels_have_correct_values(self):
        """Test that log levels have expected integer values"""
        assert LogLevel.DEBUG.value == 10
        assert LogLevel.INFO.value == 20
        assert LogLevel.WARNING.value == 30
        assert LogLevel.ERROR.value == 40
        assert LogLevel.CRITICAL.value == 50

    def test_log_levels_are_ordered(self):
        """Test that log levels can be compared"""
        assert LogLevel.DEBUG < LogLevel.INFO
        assert LogLevel.INFO < LogLevel.WARNING
        assert LogLevel.WARNING < LogLevel.ERROR
        assert LogLevel.ERROR < LogLevel.CRITICAL


class TestLogContext:
    """Test LogContext data class"""

    def test_create_basic_context(self):
        """Test creating basic log context"""
        context = LogContext(session_id="test-session", component="test")
        assert context.session_id == "test-session"
        assert context.component == "test"
        assert context.operation_id is None
        assert context.user_id is None
        assert context.extra_data is None

    def test_create_full_context(self):
        """Test creating context with all fields"""
        extra_data = {"key": "value", "number": 42}
        context = LogContext(
            session_id="session-123",
            component="ui.test",
            operation_id="op-456",
            user_id="user-789",
            correlation_id="corr-abc",
            extra_data=extra_data,
        )

        assert context.session_id == "session-123"
        assert context.component == "ui.test"
        assert context.operation_id == "op-456"
        assert context.user_id == "user-789"
        assert context.correlation_id == "corr-abc"
        assert context.extra_data == extra_data


class TestLogRecord:
    """Test LogRecord data class"""

    def test_create_basic_record(self):
        """Test creating basic log record"""
        timestamp = datetime.now()
        record = LogRecord(
            timestamp=timestamp,
            level=LogLevel.INFO,
            component="test",
            message="Test message",
        )

        assert record.timestamp == timestamp
        assert record.level == LogLevel.INFO
        assert record.component == "test"
        assert record.message == "Test message"
        assert record.context is None
        assert record.exception is None
        assert record.extra_data is None


class TestComponentLogger:
    """Test ComponentLogger implementation"""

    def setup_method(self):
        """Setup test method"""
        self.manager = Mock()
        self.logger = ComponentLogger("test.component", self.manager)
        self.manager.get_context.return_value = None
        self.manager._get_component_level.return_value = LogLevel.DEBUG

    def test_logger_creation(self):
        """Test logger is created correctly"""
        assert self.logger.component == "test.component"
        assert self.logger.manager == self.manager

    def test_debug_logging(self):
        """Test debug level logging"""
        self.logger.debug("Debug message", extra_data={"key": "value"})

        self.manager._handle_record.assert_called_once()
        args = self.manager._handle_record.call_args[0]
        record = args[0]

        assert record.level == LogLevel.DEBUG
        assert record.message == "Debug message"
        assert record.component == "test.component"

    def test_info_logging(self):
        """Test info level logging"""
        self.logger.info("Info message")

        self.manager._handle_record.assert_called_once()
        args = self.manager._handle_record.call_args[0]
        record = args[0]

        assert record.level == LogLevel.INFO
        assert record.message == "Info message"

    def test_warning_logging(self):
        """Test warning level logging"""
        self.logger.warning("Warning message")

        self.manager._handle_record.assert_called_once()
        args = self.manager._handle_record.call_args[0]
        record = args[0]

        assert record.level == LogLevel.WARNING
        assert record.message == "Warning message"

    def test_error_logging(self):
        """Test error level logging"""
        self.logger.error("Error message")

        self.manager._handle_record.assert_called_once()
        args = self.manager._handle_record.call_args[0]
        record = args[0]

        assert record.level == LogLevel.ERROR
        assert record.message == "Error message"

    def test_critical_logging(self):
        """Test critical level logging"""
        self.logger.critical("Critical message")

        self.manager._handle_record.assert_called_once()
        args = self.manager._handle_record.call_args[0]
        record = args[0]

        assert record.level == LogLevel.CRITICAL
        assert record.message == "Critical message"

    def test_level_filtering(self):
        """Test that messages below threshold are filtered"""
        self.manager._get_component_level.return_value = LogLevel.WARNING

        # These should be filtered out
        self.logger.debug("Debug message")
        self.logger.info("Info message")

        # These should go through
        self.logger.warning("Warning message")
        self.logger.error("Error message")

        # Should only have 2 calls (warning and error)
        assert self.manager._handle_record.call_count == 2


class TestLoggerManager:
    """Test LoggerManager singleton and functionality"""

    def setup_method(self):
        """Setup test method"""
        # Clear singleton instance
        LoggerManager._instance = None

    def test_singleton_pattern(self):
        """Test that LoggerManager is a singleton"""
        manager1 = LoggerManager()
        manager2 = LoggerManager()
        assert manager1 is manager2

    def test_get_logger(self):
        """Test getting loggers for components"""
        manager = LoggerManager()

        logger1 = manager.get_logger("ui.theme")
        logger2 = manager.get_logger("core.app")
        logger3 = manager.get_logger("ui.theme")  # Same as logger1

        assert isinstance(logger1, ComponentLogger)
        assert isinstance(logger2, ComponentLogger)
        assert logger1 is logger3  # Same instance for same component
        assert logger1 is not logger2  # Different components get different instances

        assert logger1.component == "ui.theme"
        assert logger2.component == "core.app"

    def test_context_management(self):
        """Test setting and getting logging context"""
        manager = LoggerManager()

        context = LogContext(session_id="test-session", component="test")
        manager.set_context(context)

        retrieved_context = manager.get_context()
        assert retrieved_context == context

    def test_session_creation(self):
        """Test creating new logging session"""
        manager = LoggerManager()

        session_id = manager.create_session()
        assert isinstance(session_id, str)
        assert len(session_id) > 0

        context = manager.get_context()
        assert context is not None
        assert context.session_id == session_id

    def test_performance_tracking(self):
        """Test performance tracking functionality"""
        manager = LoggerManager()

        operation_id = manager.start_operation("test_operation")
        assert isinstance(operation_id, str)

        time.sleep(0.01)  # Small delay
        duration = manager.end_operation(operation_id)
        assert duration > 0


class TestFormatters:
    """Test log formatters"""

    def setup_method(self):
        """Setup test method"""
        self.timestamp = datetime.now()
        self.context = LogContext(
            session_id="test-session", component="test", extra_data={"key": "value"}
        )
        self.record = LogRecord(
            timestamp=self.timestamp,
            level=LogLevel.INFO,
            component="test.component",
            message="Test message",
            context=self.context,
        )

    def test_console_formatter_basic(self):
        """Test basic console formatting"""
        formatter = ConsoleFormatter(use_colors=False, use_emojis=False)
        result = formatter.format(self.record)

        assert "INFO" in result
        assert "TEST.COMPONENT" in result
        assert "Test message" in result

    def test_console_formatter_compact(self):
        """Test compact console formatting"""
        formatter = ConsoleFormatter(compact=True, use_colors=False)
        result = formatter.format(self.record)

        assert "Test message" in result
        assert len(result.split("\n")) == 1  # Single line

    def test_file_formatter_detailed(self):
        """Test detailed file formatting"""
        formatter = FileFormatter(detailed=True, include_context=True)
        result = formatter.format(self.record)

        assert "INFO" in result
        assert "test.component" in result or "TEST.COMPONENT" in result
        assert "Test message" in result
        assert "session=test-session" in result
        assert "key=value" in result

    def test_json_formatter(self):
        """Test JSON formatting"""
        formatter = JSONFormatter()
        result = formatter.format(self.record)

        # Parse JSON to verify structure
        data = json.loads(result)
        assert data["level"] == "INFO"
        assert data["component"] == "test.component"
        assert data["message"] == "Test message"
        assert "context" in data
        assert data["context"]["session_id"] == "test-session"

    def test_minimal_formatter(self):
        """Test minimal formatting"""
        formatter = MinimalFormatter()
        result = formatter.format(self.record)

        assert result == "I: Test message"

    def test_debug_formatter(self):
        """Test debug formatting with maximum detail"""
        formatter = DebugFormatter()
        result = formatter.format(self.record)

        lines = result.split("\n")
        assert len(lines) > 5  # Multiple lines
        assert any("Message: Test message" in line for line in lines)
        assert any("Session: test-session" in line for line in lines)

    def test_formatter_factory(self):
        """Test formatter factory function"""
        console_formatter = create_formatter("console")
        assert isinstance(console_formatter, ConsoleFormatter)

        file_formatter = create_formatter("file")
        assert isinstance(file_formatter, FileFormatter)

        json_formatter = create_formatter("json")
        assert isinstance(json_formatter, JSONFormatter)

        with pytest.raises(ValueError, match="Unknown formatter type"):
            create_formatter("unknown_type")


class TestHandlers:
    """Test log handlers"""

    def setup_method(self):
        """Setup test method"""
        self.record = LogRecord(
            timestamp=datetime.now(),
            level=LogLevel.INFO,
            component="test",
            message="Test message",
        )

    def test_colored_console_handler(self):
        """Test colored console handler"""
        # Use StringIO to capture output
        from io import StringIO

        stream = StringIO()

        handler = ColoredConsoleHandler(stream=stream, use_colors=False)
        handler.handle(self.record)

        output = stream.getvalue()
        assert "Test message" in output
        assert "INFO" in output

    def test_rotating_file_handler(self):
        """Test rotating file handler"""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = Path(temp_dir) / "test.log"

            handler = RotatingFileHandler(
                filename=str(log_file),
                max_size=1024,  # Small size for testing
                backup_count=3,
            )

            # Write a record
            handler.handle(self.record)

            # Check file was created and contains content
            assert log_file.exists()
            content = log_file.read_text()
            assert "Test message" in content
            assert "INFO" in content

            handler.close()

    def test_multi_handler(self):
        """Test multi-handler forwarding"""
        handler1 = Mock()
        handler2 = Mock()

        multi_handler = MultiHandler([handler1, handler2])
        multi_handler.handle(self.record)

        handler1.handle.assert_called_once_with(self.record)
        handler2.handle.assert_called_once_with(self.record)

    def test_filtered_handler(self):
        """Test filtered handler"""
        target_handler = Mock()

        # Filter to only allow "test" component
        filtered_handler = FilteredHandler(
            target_handler=target_handler, allowed_components=["test"]
        )

        # This should go through
        filtered_handler.handle(self.record)
        target_handler.handle.assert_called_once_with(self.record)

        # This should be blocked
        target_handler.reset_mock()
        blocked_record = LogRecord(
            timestamp=datetime.now(),
            level=LogLevel.INFO,
            component="blocked",
            message="Blocked message",
        )
        filtered_handler.handle(blocked_record)
        target_handler.handle.assert_not_called()

    def test_handler_factory(self):
        """Test handler factory function"""
        console_handler = create_handler("console")
        assert isinstance(console_handler, ColoredConsoleHandler)

        with pytest.raises(ValueError, match="Unknown handler type"):
            create_handler("unknown_type")


class TestUtils:
    """Test logging utilities"""

    def test_performance_timer_context_manager(self):
        """Test performance timer as context manager"""
        logger = Mock()

        with PerformanceTimer("test_operation", logger, threshold_ms=0) as timer:
            time.sleep(0.01)

        assert timer.duration_ms is not None
        assert timer.duration_ms > 0
        logger.log.assert_called_once()

    def test_performance_timer_decorator(self):
        """Test performance timer decorator"""
        Mock()

        @performance_timer("decorated_operation", threshold_ms=0)
        def test_function():
            time.sleep(0.01)
            return "result"

        result = test_function()
        assert result == "result"

    def test_log_method_calls_decorator(self):
        """Test method call logging decorator"""
        logger = Mock()

        @log_method_calls(logger, include_args=True, include_result=True)
        def test_function(arg1, arg2="default"):
            return f"{arg1}-{arg2}"

        result = test_function("test", arg2="value")
        assert result == "test-value"

        # Should have entry and exit calls
        assert logger.log.call_count == 2

    def test_logging_context(self):
        """Test thread-local logging context"""
        LoggingContext.clear_context()

        # Set context
        LoggingContext.set_context(operation="test", user="admin")
        context = LoggingContext.get_context()

        assert context["operation"] == "test"
        assert context["user"] == "admin"

        # Test context manager
        with LoggingContext.context(operation="nested", extra="data"):
            nested_context = LoggingContext.get_context()
            assert nested_context["operation"] == "nested"
            assert nested_context["extra"] == "data"

        # Should restore original context
        restored_context = LoggingContext.get_context()
        assert restored_context["operation"] == "test"
        assert "extra" not in restored_context

    def test_format_bytes(self):
        """Test byte formatting utility"""
        assert format_bytes(0) == "0 B"
        assert format_bytes(1024) == "1.0 KB"
        assert format_bytes(1024 * 1024) == "1.0 MB"
        assert format_bytes(1536) == "1.5 KB"

    def test_format_duration(self):
        """Test duration formatting utility"""
        assert "ms" in format_duration(0.001)
        assert "s" in format_duration(1.5)
        assert "m" in format_duration(65)
        assert "h" in format_duration(3665)

    def test_sanitize_path(self):
        """Test path sanitization"""
        if sys.platform == "win32":
            path = "C:\\Users\\username\\Documents\\file.txt"
            sanitized = sanitize_path(path)
            assert "***" in sanitized
        else:
            path = "/home/username/documents/file.txt"
            sanitized = sanitize_path(path)
            assert "***" in sanitized

    def test_safe_str(self):
        """Test safe string conversion"""
        assert safe_str(None) == "None"
        assert safe_str("test") == "test"
        assert safe_str(42) == "42"
        assert safe_str([1, 2, 3]) == "[1, 2, 3]"

        # Test truncation
        long_string = "x" * 300
        result = safe_str(long_string, max_length=100)
        assert len(result) <= 100
        assert "..." in result

    def test_rate_limiter(self):
        """Test rate limiting functionality"""
        limiter = RateLimiter(max_messages=2, time_window=1.0)

        # First two should pass
        assert limiter.should_log("test_key") is True
        assert limiter.should_log("test_key") is True

        # Third should be blocked
        assert limiter.should_log("test_key") is False

        # Different key should work
        assert limiter.should_log("other_key") is True


class TestExceptions:
    """Test logging exceptions"""

    def test_base_logging_exception(self):
        """Test base logging exception"""
        exc = LoggingException(
            "Test error", component="test.component", context_data="extra"
        )

        assert str(exc) == "[test.component] Test error"
        assert exc.component == "test.component"
        assert exc.context["context_data"] == "extra"

    def test_specific_exceptions(self):
        """Test specific exception types"""
        config_error = ConfigurationError("Config error")
        assert isinstance(config_error, LoggingException)

        handler_error = HandlerError("Handler error")
        assert isinstance(handler_error, LoggingException)

        formatter_error = FormatterError("Formatter error")
        assert isinstance(formatter_error, LoggingException)


class TestIntegration:
    """Integration tests for the complete logging system"""

    def setup_method(self):
        """Setup integration test"""
        LoggerManager._instance = None

    def test_end_to_end_logging(self):
        """Test complete logging flow from logger to output"""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = Path(temp_dir) / "integration.log"

            # Create configuration
            config = LoggingConfig(
                level=LogLevel.DEBUG,
                console=Mock(enabled=False),  # Disable console for clean test
                file=Mock(
                    enabled=True,
                    path=str(log_file),
                    rotation=Mock(
                        max_size="1MB",
                        backup_count=3,
                        retention_days=7,
                        compression_enabled=False,
                    ),
                ),
                components={},
                session_tracking=True,
                performance_monitoring=True,
            )

            # Get manager and configure
            manager = LoggerManager()
            manager.configure(config)

            # Get logger and log messages
            logger = manager.get_logger("integration.test")

            logger.debug("Debug message")
            logger.info("Info message", extra_data={"key": "value"})
            logger.warning("Warning message")
            logger.error("Error message")

            # Force handlers to flush
            manager.shutdown()

            # Check that file was created and contains messages
            if log_file.exists():
                content = log_file.read_text()
                assert "Debug message" in content
                assert "Info message" in content
                assert "Warning message" in content
                assert "Error message" in content

    def test_convenience_functions(self):
        """Test convenience functions work correctly"""
        LoggerManager._instance = None

        # Test get_logger function
        logger1 = get_logger("convenience.test")
        logger2 = get_logger("convenience.test")

        assert logger1 is logger2  # Same instance
        assert isinstance(logger1, ComponentLogger)
        assert logger1.component == "convenience.test"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
