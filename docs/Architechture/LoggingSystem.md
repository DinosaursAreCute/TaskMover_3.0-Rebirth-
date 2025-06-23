# TaskMover Logging System Specification

## Overview

The TaskMover logging system provides comprehensive, configurable logging with multiple output formats, component-based filtering, and advanced features for debugging, monitoring, and user feedback.

## Architecture

```
LoggerManager (Singleton)
├── ConfigurationManager
│   ├── YAML Configuration Loading
│   ├── Environment Variable Overrides
│   └── Runtime Configuration Updates
├── LoggerFactory
│   ├── Component-based Logger Creation
│   ├── Logger Hierarchy Management
│   └── Custom Logger Configuration
├── HandlerRegistry
│   ├── ConsoleHandler (colored output)
│   ├── RotatingFileHandler (size/time-based)
│   ├── ComponentHandler (filtered output)
│   └── ExtensionHandlers (email, syslog, remote)
├── FormatterRegistry
│   ├── ConsoleFormatter (colored, compact)
│   ├── FileFormatter (structured, detailed)
│   ├── ComponentFormatter (component-specific)
│   └── JSONFormatter (structured data)
└── FilterManager
    ├── ComponentFilter (by component category)
    ├── LevelFilter (by log level)
    ├── RegexFilter (pattern matching)
    └── TimeFilter (time-based filtering)
```

## Configuration Specification

### Configuration File Structure
**Location**: `taskmover/core/logging_config.yml`

```yaml
logging:
  # Global settings
  level: INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL
  session_id: auto  # auto-generate or custom
  timezone: local  # local, utc, or specific timezone
  
  # Console output configuration
  console:
    enabled: true
    level: INFO  # Override global level for console
    colors: true  # Enable colored output
    format: compact  # compact, detailed, minimal, json
    include_timestamp: true
    include_component: true
    include_thread: false
    
  # File output configuration
  file:
    enabled: true
    level: DEBUG  # Override global level for file
    path: "logs/taskmover.log"
    format: detailed  # detailed, json, compact
    
    # Rotation settings
    rotation:
      type: size  # size, time, hybrid
      max_size: 10MB  # For size-based rotation
      max_files: 5    # Number of backup files to keep
      when: midnight  # For time-based: midnight, hourly, daily, weekly
      interval: 1     # Rotation interval
      
    # File management
    encoding: utf-8
    compression: gzip  # none, gzip, bz2
    auto_cleanup: true
    cleanup_days: 30  # Delete logs older than N days
    
  # Component-specific configuration
  components:
    ui:
      level: INFO
      file_suffix: "_ui"  # Optional separate file
      console: true
    core:
      level: DEBUG
      file_suffix: "_core"
    build:
      level: WARNING
      console: false  # Only to file
    tests:
      level: ERROR
      file_suffix: "_tests"
    config:
      level: INFO
    file_ops:
      level: DEBUG
      performance_logging: true
    pattern:
      level: DEBUG
    storage:
      level: WARNING
      
  # Performance logging
  performance:
    enabled: true
    threshold_ms: 100  # Log operations taking longer than this
    memory_tracking: true
    function_timing: true
    
  # Advanced features
  advanced:
    context_capture: true  # Capture additional context on errors
    stack_trace_limit: 10
    async_logging: false   # For high-performance scenarios
    buffer_size: 1000     # For async logging
    
  # Integration settings
  integration:
    ui_notifications: true     # Show critical errors as UI notifications
    build_integration: true    # Enhanced build logging
    test_integration: true     # Test execution logging
    
  # Development tools
  development:
    debug_mode: false         # Enable debug-specific features
    log_method_calls: false   # Log all method entry/exit
    log_variable_changes: false # Log variable state changes
    profiling: false          # Enable performance profiling
```

## Component Categories

### Primary Components
- **ui**: All UI-related operations
  - `ui.theme`: Theme management
  - `ui.components`: UI component operations
  - `ui.layout`: Layout and positioning
  - `ui.dialogs`: Dialog and modal operations
  - `ui.events`: Event handling
  
- **core**: Core application logic
  - `core.app`: Main application lifecycle
  - `core.config`: Configuration management
  - `core.startup`: Application startup
  - `core.shutdown`: Application shutdown
  
- **build**: Build and packaging operations
  - `build.pyinstaller`: PyInstaller operations
  - `build.spec`: Spec file processing
  - `build.assets`: Asset bundling
  - `build.validation`: Build validation
  
- **tests**: Testing framework
  - `tests.unit`: Unit test execution
  - `tests.integration`: Integration tests
  - `tests.ui`: UI testing
  - `tests.performance`: Performance tests
  
- **file_ops**: File organization operations
  - `file_ops.scan`: File scanning
  - `file_ops.move`: File moving operations
  - `file_ops.copy`: File copying operations
  - `file_ops.organize`: Organization logic
  
- **pattern**: Pattern matching and rules
  - `pattern.match`: Pattern matching
  - `pattern.validate`: Pattern validation
  - `pattern.compile`: Pattern compilation
  
- **storage**: Data persistence
  - `storage.config`: Configuration storage
  - `storage.rules`: Rule persistence
  - `storage.cache`: Caching operations

## Log Message Structure

### Standard Fields
```python
{
    "timestamp": "2025-06-23T14:23:45.123Z",      # ISO 8601 with milliseconds
    "level": "INFO",                               # Log level
    "component": "ui.theme",                       # Component identifier
    "module": "theme_manager",                     # Python module name
    "function": "set_theme_mode",                  # Function/method name
    "line": 45,                                   # Line number
    "thread": "MainThread",                       # Thread identifier
    "session": "abc123",                          # Session identifier
    "message": "Theme switched to dark mode",     # Primary message
    "context": {                                  # Additional context
        "previous_theme": "light",
        "trigger": "user_manual",
        "user_id": "anonymous"
    },
    "performance": {                              # Performance data (optional)
        "duration_ms": 15.2,
        "memory_mb": 45.6
    }
}
```

## Output Formats

### Console Format (Colored)
```
[14:23:45.123] UI.THEME ℹ️  Theme switched to dark mode (duration: 15ms)
[14:23:45.124] CORE.APP ⚠️  Configuration file not found, using defaults
[14:23:45.125] BUILD.EXE ❌ PyInstaller failed: Missing module 'taskmover.ui'
```

### File Format (Detailed)
```
2025-06-23T14:23:45.123Z [INFO] [UI.THEME] [theme_manager.py:45:set_theme_mode] Theme switched to dark mode | session=abc123 thread=MainThread context={"previous_theme": "light", "trigger": "user_manual"} performance={"duration_ms": 15.2}
```

### JSON Format (Structured)
```json
{
  "timestamp": "2025-06-23T14:23:45.123Z",
  "level": "INFO",
  "component": "ui.theme",
  "module": "theme_manager",
  "function": "set_theme_mode",
  "line": 45,
  "message": "Theme switched to dark mode",
  "context": {"previous_theme": "light", "trigger": "user_manual"},
  "performance": {"duration_ms": 15.2}
}
```

## API Design

### Basic Usage
```python
# Get logger for specific component
logger = get_logger('ui.theme')
logger.info("Theme changed", context={"theme": "dark"})
logger.error("Failed to load theme", exc_info=True)

# Component-specific loggers
ui_logger = get_component_logger('ui')
core_logger = get_component_logger('core')

# Performance logging
with log_performance("file_organization"):
    # Operation code here
    pass

# Contextual logging
with log_context(operation="startup", user="admin"):
    logger.info("Application starting")
    # All logs in this block include the context
```

### Advanced Usage
```python
# Custom formatters
logger.add_formatter(JSONFormatter())

# Conditional logging
logger.debug_if(condition, "Debug message")

# Batch logging for performance
with logger.batch_mode():
    for item in large_list:
        logger.debug(f"Processing {item}")

# Error aggregation
logger.aggregate_errors("operation_type", max_count=10)
```

## Performance Considerations

### Memory Management
- **Buffer Management**: Configurable buffer sizes for async logging
- **Memory Monitoring**: Track memory usage during logging operations
- **Cleanup Policies**: Automatic cleanup of old log entries in memory

### File Management
- **Rotation Policies**: Size-based, time-based, and hybrid rotation
- **Compression**: Automatic compression of rotated logs
- **Cleanup**: Automatic deletion of old log files
- **Lock Management**: Efficient file locking for concurrent access

### Performance Monitoring
- **Execution Timing**: Track time spent in logging operations
- **Throughput Monitoring**: Monitor log message throughput
- **Resource Usage**: Track CPU and memory usage for logging

## Integration Points

### UI Integration
- **Progress Indicators**: Integrate with UI progress bars
- **Error Notifications**: Show critical errors in UI
- **Debug Panels**: Optional debug information panels
- **Log Viewers**: Built-in log viewing capabilities

### Build System Integration
- **Build Progress**: Enhanced build process logging
- **Error Reporting**: Structured build error reporting
- **Asset Tracking**: Log asset bundling and processing
- **Validation Results**: Log build validation results

### Testing Integration
- **Test Execution**: Log test runs and results
- **Performance Tests**: Specialized performance logging
- **Coverage Reporting**: Integration with coverage tools
- **Failure Analysis**: Enhanced failure reporting

## Security and Privacy

### Data Protection
- **Sensitive Data Filtering**: Automatic filtering of sensitive information
- **Path Sanitization**: Clean file paths in logs
- **User Data Protection**: Anonymize user-specific data
- **Encryption Options**: Optional log file encryption

### Access Control
- **File Permissions**: Proper file permission management
- **Log Access Control**: Control access to log files
- **Audit Trails**: Maintain audit trails for log access
- **Secure Storage**: Secure storage options for sensitive logs

## Extensibility

### Plugin Architecture
- **Custom Handlers**: Support for custom log handlers
- **Custom Formatters**: Pluggable formatter system
- **Custom Filters**: User-defined filtering logic
- **Integration Hooks**: Hooks for external system integration

### Future Enhancements
- **Remote Logging**: Support for remote log aggregation
- **Real-time Monitoring**: Live log monitoring capabilities
- **Analytics Integration**: Integration with analytics platforms
- **Machine Learning**: AI-powered log analysis and insights

## Implementation Checklist

### Core Infrastructure
- [ ] LoggerManager singleton implementation
- [ ] ConfigurationManager with YAML support
- [ ] LoggerFactory with component hierarchy
- [ ] HandlerRegistry with multiple output types
- [ ] FormatterRegistry with multiple formats
- [ ] FilterManager with advanced filtering

### Configuration System
- [ ] YAML configuration loading
- [ ] Environment variable overrides
- [ ] Runtime configuration updates
- [ ] Configuration validation
- [ ] Default configuration generation

### Output Handlers
- [ ] Enhanced ConsoleHandler with colors
- [ ] RotatingFileHandler with size/time rotation
- [ ] ComponentHandler with filtering
- [ ] JSONFileHandler for structured output
- [ ] Performance logging handler

### Integration
- [ ] UI component integration
- [ ] Build system integration
- [ ] Test framework integration
- [ ] Error reporting integration
- [ ] Performance monitoring integration

### Advanced Features
- [ ] Context managers for operation tracking
- [ ] Performance metrics collection
- [ ] Memory usage monitoring
- [ ] Async logging support
- [ ] Log aggregation and analysis tools

This specification provides the foundation for a comprehensive, production-ready logging system that meets all requirements while maintaining flexibility for future enhancements.
