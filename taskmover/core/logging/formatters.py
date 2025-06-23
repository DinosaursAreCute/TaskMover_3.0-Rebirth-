"""
Log Formatters Implementation

Provides various formatters for different output formats including console
with colors, structured file output, JSON format, and component-specific formatting.
"""

import json
from abc import abstractmethod
from datetime import datetime
from typing import Any

from .exceptions import FormatterError
from .interfaces import ILogFormatter, LogLevel, LogRecord

try:
    import colorama
    from colorama import Back, Fore, Style

    colorama.init(autoreset=True)
    COLORAMA_AVAILABLE = True
except ImportError:
    COLORAMA_AVAILABLE = False

    # Fallback color constants
    class MockColorama:
        class Fore:
            RED = GREEN = YELLOW = BLUE = MAGENTA = CYAN = WHITE = RESET = ""

        class Back:
            RED = GREEN = YELLOW = BLUE = MAGENTA = CYAN = WHITE = RESET = ""

        class Style:
            BRIGHT = DIM = NORMAL = RESET_ALL = ""

    # Only define these if colorama is not available
    Fore = MockColorama.Fore  # type: ignore
    Back = MockColorama.Back  # type: ignore
    Style = MockColorama.Style  # type: ignore


class BaseFormatter(ILogFormatter):
    """Base formatter with common functionality"""

    def __init__(
        self,
        include_timestamp: bool = True,
        include_component: bool = True,
        include_thread: bool = False,
        timezone: str = "local",
    ):
        self.include_timestamp = include_timestamp
        self.include_component = include_component
        self.include_thread = include_thread
        self.timezone = timezone

    def format_timestamp(self, dt: datetime) -> str:
        """Format timestamp according to configuration"""
        if self.timezone == "utc":
            # Convert to UTC and format
            utc_time = dt.utctimetuple()
            return f"{utc_time.tm_year:04d}-{utc_time.tm_mon:02d}-{utc_time.tm_mday:02d}T{utc_time.tm_hour:02d}:{utc_time.tm_min:02d}:{utc_time.tm_sec:02d}Z"
        else:
            return dt.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]  # Trim to milliseconds

    def get_level_name(self, level: LogLevel) -> str:
        """Get string representation of log level"""
        return level.name

    @abstractmethod
    def format(self, record: LogRecord) -> str:
        """Format log record to string"""
        pass


class ConsoleFormatter(BaseFormatter):
    """Console formatter with optional colors and aligned column layout"""

    # Color mapping for log levels
    LEVEL_COLORS = {
        LogLevel.DEBUG: Fore.CYAN,
        LogLevel.INFO: Fore.GREEN,
        LogLevel.WARNING: Fore.YELLOW,
        LogLevel.ERROR: Fore.RED,
        LogLevel.CRITICAL: Fore.RED + Style.BRIGHT,
    }

    # Emoji mapping for log levels (optional)
    LEVEL_EMOJIS = {
        LogLevel.DEBUG: "🔍",
        LogLevel.INFO: "ℹ️",
        LogLevel.WARNING: "⚠️",
        LogLevel.ERROR: "❌",
        LogLevel.CRITICAL: "🚨",
    }

    # Column widths for alignment
    TIMESTAMP_WIDTH = 12  # HH:MM:SS.mmm
    LEVEL_WIDTH = 8  # CRITICAL is 8 chars
    COMPONENT_WIDTH = 20  # Most component names

    def __init__(
        self,
        use_colors: bool = True,
        use_emojis: bool = True,
        compact: bool = True,
        align_columns: bool = True,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.use_colors = use_colors and COLORAMA_AVAILABLE
        self.use_emojis = use_emojis
        self.compact = compact
        self.align_columns = align_columns

    def format(self, record: LogRecord) -> str:
        """Format record for console output with aligned columns"""
        try:
            if self.align_columns:
                return self._format_aligned(record)
            else:
                return self._format_simple(record)

        except Exception as e:
            raise FormatterError(
                f"Failed to format console record: {e}", component="console_formatter"
            ) from e

    def _format_aligned(self, record: LogRecord) -> str:
        """Format with aligned columns for better readability"""
        parts = []

        # Timestamp column
        if self.include_timestamp:
            timestamp = self.format_timestamp(record.timestamp)
            if self.compact:
                timestamp = timestamp.split()[1]  # Time only (HH:MM:SS.mmm)
            timestamp_part = f"[{timestamp}]".ljust(
                self.TIMESTAMP_WIDTH + 2
            )  # +2 for brackets
            parts.append(timestamp_part)

        # Level column with color and emoji
        level_name = self.get_level_name(record.level)
        level_display = ""

        if self.use_emojis:
            emoji = self.LEVEL_EMOJIS.get(record.level, "")
            if emoji:
                level_display = f"{emoji} "

        if self.use_colors:
            color = self.LEVEL_COLORS.get(record.level, "")
            level_colored = f"{color}{level_name}{Style.RESET_ALL}"
            # Calculate padding for colored text (color codes don't count toward width)
            level_display += level_colored
            level_padding = self.LEVEL_WIDTH - len(level_name)
        else:
            level_display += level_name
            level_padding = self.LEVEL_WIDTH - len(level_name)

        # Add padding for alignment
        level_part = level_display + (" " * max(0, level_padding))
        parts.append(level_part)

        # Component column
        if self.include_component:
            component = record.component.upper()
            if self.use_colors:
                component_colored = f"{Fore.MAGENTA}{component}{Style.RESET_ALL}"
                # Calculate padding for colored text
                component_padding = self.COMPONENT_WIDTH - len(component)
                component_part = component_colored + (" " * max(0, component_padding))
            else:
                component_part = component.ljust(self.COMPONENT_WIDTH)
            parts.append(component_part)

        # Message (no padding needed as it's the last column)
        message = record.message
        if self.use_colors and record.level in [LogLevel.ERROR, LogLevel.CRITICAL]:
            message = f"{Fore.RED}{message}{Style.RESET_ALL}"

        # Combine all parts
        prefix = " ".join(parts)
        result = f"{prefix} {message}"

        # Add context if available and not compact
        if not self.compact and record.context and record.context.extra_data:
            context_str = " ".join(
                [f"{k}={v}" for k, v in record.context.extra_data.items()]
            )
            result += f" | {context_str}"

        return result

    def _format_simple(self, record: LogRecord) -> str:
        """Format without column alignment (original behavior)"""
        parts = []

        # Timestamp
        if self.include_timestamp:
            timestamp = self.format_timestamp(record.timestamp)
            if self.compact:
                timestamp = timestamp.split()[1]  # Time only
            parts.append(f"[{timestamp}]")

        # Component
        if self.include_component:
            component = record.component.upper()
            if self.use_colors:
                component = f"{Fore.MAGENTA}{component}{Style.RESET_ALL}"
            parts.append(component)

        # Level with color and emoji
        level_name = self.get_level_name(record.level)
        if self.use_emojis:
            emoji = self.LEVEL_EMOJIS.get(record.level, "")
            level_display = f"{emoji} " if emoji else ""
        else:
            level_display = ""

        if self.use_colors:
            color = self.LEVEL_COLORS.get(record.level, "")
            level_display += f"{color}{level_name}{Style.RESET_ALL}"
        else:
            level_display += level_name

        parts.append(level_display)

        # Message
        message = record.message
        if self.use_colors and record.level in [LogLevel.ERROR, LogLevel.CRITICAL]:
            message = f"{Fore.RED}{message}{Style.RESET_ALL}"

        # Format final output
        if self.compact:
            prefix = " ".join(parts)
            return f"{prefix} {message}"
        else:
            # Detailed format
            result = " ".join(parts) + f" {message}"

            # Add context if available
            if record.context and record.context.extra_data:
                context_str = " ".join(
                    [f"{k}={v}" for k, v in record.context.extra_data.items()]
                )
                result += f" | {context_str}"

            return result


class FileFormatter(BaseFormatter):
    """File formatter with structured, detailed output"""

    def __init__(self, detailed: bool = True, include_context: bool = True, **kwargs):
        super().__init__(**kwargs)
        self.detailed = detailed
        self.include_context = include_context

    def format(self, record: LogRecord) -> str:
        """Format record for file output"""
        try:
            parts = []

            # Timestamp (always include for files)
            timestamp = self.format_timestamp(record.timestamp)
            parts.append(timestamp)

            # Level
            level_name = f"[{self.get_level_name(record.level)}]"
            parts.append(level_name)

            # Component
            component = f"[{record.component.upper()}]"
            parts.append(component)

            if self.detailed:
                # Context is available but doesn't have module attribute
                # Skip module info for now since it's not in LogContext
                pass

            # Message
            message = record.message

            # Build base line
            base_line = " ".join(parts) + f" {message}"

            # Add context information
            context_parts = []
            if record.context:
                if record.context.session_id:
                    context_parts.append(f"session={record.context.session_id}")
                if record.context.operation_id:
                    context_parts.append(f"operation={record.context.operation_id}")
                if record.context.user_id:
                    context_parts.append(f"user={record.context.user_id}")
                if self.include_context and record.context.extra_data:
                    for k, v in record.context.extra_data.items():
                        context_parts.append(f"{k}={v}")

            if context_parts:
                base_line += (
                    f" | {' '.join(context_parts)}"  # Add exception information
                )
            if record.exception:
                base_line += f" | exception={type(record.exception).__name__}: {record.exception}"

            return base_line

        except Exception as e:
            raise FormatterError(
                f"Failed to format file record: {e}", component="file_formatter"
            ) from e


class JSONFormatter(BaseFormatter):
    """JSON formatter for structured logging"""

    def __init__(self, pretty: bool = False, **kwargs):
        super().__init__(**kwargs)
        self.pretty = pretty

    def format(self, record: LogRecord) -> str:
        """Format record as JSON"""
        try:
            data: dict[str, Any] = {
                "timestamp": self.format_timestamp(record.timestamp),
                "level": self.get_level_name(record.level),
                "component": record.component,
                "message": record.message,
            }

            # Add context data
            if record.context:
                context_data = {}
                if record.context.session_id:
                    context_data["session_id"] = record.context.session_id
                if record.context.operation_id:
                    context_data["operation_id"] = record.context.operation_id
                if record.context.user_id:
                    context_data["user_id"] = record.context.user_id
                if record.context.correlation_id:
                    context_data["correlation_id"] = record.context.correlation_id
                if record.context.extra_data:
                    context_data.update(record.context.extra_data)

                if context_data:
                    data["context"] = context_data

            # Add exception data
            if record.exception:
                data["exception"] = {
                    "type": type(record.exception).__name__,
                    "message": str(record.exception),
                }  # Add extra data
            if record.extra_data:
                data["extra"] = record.extra_data

            if self.pretty:
                return json.dumps(data, indent=2, ensure_ascii=False)
            else:
                return json.dumps(data, ensure_ascii=False)

        except Exception as e:
            raise FormatterError(
                f"Failed to format JSON record: {e}", component="json_formatter"
            ) from e


class ComponentFormatter(BaseFormatter):
    """Component-specific formatter that adapts based on component type"""

    # Component-specific formatting rules
    COMPONENT_FORMATS: dict[str, dict[str, Any]] = {
        "ui": {"use_colors": True, "compact": True, "include_timestamp": False},
        "core": {"detailed": True, "include_context": True},
        "build": {"detailed": True, "include_timestamp": True},
        "test": {"compact": True, "use_colors": True},
        "performance": {"detailed": True, "include_context": True, "format": "json"},
    }

    def __init__(self, component: str | None = None, **kwargs):
        super().__init__(**kwargs)
        self.component = component
        self.settings: dict[str, Any] = {}  # Get component-specific settings
        if component:
            # Extract base component (e.g., "ui.theme" -> "ui")
            base_component = component.split(".")[0]
            component_settings = self.COMPONENT_FORMATS.get(base_component, {})
            self.settings = component_settings.copy()
        else:
            self.settings = {}

        # Create appropriate formatter based on component
        self._create_formatter()

    def _create_formatter(self):
        """Create appropriate formatter based on component settings"""
        if self.settings.get("format") == "json":
            self.formatter: ILogFormatter = JSONFormatter(**self.settings)
        elif "use_colors" in self.settings:
            self.formatter = ConsoleFormatter(**self.settings)
        else:
            self.formatter = FileFormatter(**self.settings)

    def format(self, record: LogRecord) -> str:
        """Format using component-specific formatter"""
        try:
            return self.formatter.format(record)

        except Exception as e:
            raise FormatterError(
                f"Failed to format component record: {e}",
                component=f"component_formatter:{self.component}",
            ) from e


class MinimalFormatter(BaseFormatter):
    """Minimal formatter for high-performance scenarios"""

    def format(self, record: LogRecord) -> str:
        """Format with minimal overhead"""
        try:
            level_char = record.level.name[0]  # D, I, W, E, C
            return f"{level_char}: {record.message}"
        except Exception as e:
            return f"E: Failed to format minimal record: {e}"


class DebugFormatter(BaseFormatter):
    """Debug formatter with maximum detail"""

    def format(self, record: LogRecord) -> str:
        """Format with maximum debug information"""
        try:
            lines = []

            # Header line
            timestamp = self.format_timestamp(record.timestamp)
            header = f"=== {timestamp} [{record.level.name}] {record.component} ==="
            lines.append(header)

            # Message
            lines.append(f"Message: {record.message}")

            # Context details
            if record.context:
                lines.append("Context:")
                if record.context.session_id:
                    lines.append(f"  Session: {record.context.session_id}")
                if record.context.operation_id:
                    lines.append(f"  Operation: {record.context.operation_id}")
                if record.context.user_id:
                    lines.append(f"  User: {record.context.user_id}")
                if record.context.extra_data:
                    lines.append("  Extra Data:")
                    for k, v in record.context.extra_data.items():
                        lines.append(f"    {k}: {v}")

            # Exception details
            if record.exception:
                lines.append(
                    f"Exception: {type(record.exception).__name__}: {record.exception}"
                )

            # Extra data
            if record.extra_data:
                lines.append("Extra:")
                for k, v in record.extra_data.items():
                    lines.append(f"  {k}: {v}")

            lines.append("=" * len(header))
            return "\n".join(lines)

        except Exception as e:
            raise FormatterError(
                f"Failed to format debug record: {e}", component="debug_formatter"
            ) from e


# Formatter factory for easy creation
def create_formatter(formatter_type: str = "console", **kwargs) -> ILogFormatter:
    """Factory function to create formatters"""
    formatters = {
        "console": ConsoleFormatter,
        "file": FileFormatter,
        "json": JSONFormatter,
        "component": ComponentFormatter,
        "minimal": MinimalFormatter,
        "debug": DebugFormatter,
    }

    formatter_class = formatters.get(formatter_type.lower())
    if not formatter_class:
        raise ValueError(f"Unknown formatter type: {formatter_type}")

    return formatter_class(**kwargs)
