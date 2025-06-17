# TaskMover Architecture Overview

## System Architecture

TaskMover Redesigned follows a modular, layered architecture that separates concerns and promotes maintainability.

### High-Level Architecture

```
┌─────────────────────────────────────────────┐
│                 User Interface               │
│             (tkinter + ttkbootstrap)         │
├─────────────────────────────────────────────┤
│                UI Components                 │
│    (Dialogs, Windows, Forms, Controls)      │
├─────────────────────────────────────────────┤
│               Application Layer              │
│           (Main App, Event Handling)        │
├─────────────────────────────────────────────┤
│                 Core Logic                   │
│    (Rules, Config, File Operations)         │
├─────────────────────────────────────────────┤
│               Utilities & Utils             │
│    (Window Management, File Helpers)        │
└─────────────────────────────────────────────┘
```

## Package Structure

```
taskmover_redesign/
├── __init__.py              # Package initialization
├── __main__.py              # Entry point
├── app.py                   # Main application class
├── core/                    # Core business logic
│   ├── __init__.py
│   ├── config.py           # Configuration management
│   ├── file_operations.py  # File organization logic
│   ├── rules.py            # Rule management
│   └── utils.py            # Utility functions
├── ui/                     # User interface components
│   ├── __init__.py
│   ├── components.py       # Base UI components
│   ├── rule_components.py  # Rule-specific UI
│   └── settings_components.py # Settings dialogs
└── tests/                  # Test suite
    ├── __init__.py
    ├── run_tests.py
    └── test_*.py           # Test modules
```

## Core Components

### Configuration Management (`core/config.py`)

**ConfigManager Class**
- Centralized configuration handling
- YAML-based settings and rules storage
- Automatic backup and recovery
- Default configuration creation

**Key Features:**
- Thread-safe configuration access
- Validation and error handling
- Backward compatibility support
- Configuration migration support

### Rule Management (`core/rules.py`)

**RuleManager Class**
- Rule creation, modification, and deletion
- Priority-based rule sorting
- Pattern matching logic
- Rule validation and testing

**Rule Structure:**
```python
{
    "rule_id": {
        "name": "Rule Name",
        "patterns": ["*.txt", "*.doc"],
        "path": "Documents/Text Files",
        "active": True,
        "priority": 1
    }
}
```

### File Operations (`core/file_operations.py`)

**FileOrganizer Class**
- Safe file movement and copying
- Conflict resolution
- Progress tracking
- Rollback capabilities

**Safety Features:**
- Pre-operation validation
- Atomic operations where possible
- Comprehensive logging
- Error recovery mechanisms

### Window Management (`core/utils.py`)

**Enhanced Window System**
- Proportional window sizing
- Multi-monitor support
- Screen-aware positioning
- Responsive design principles

**New Features:**
- `center_window()` - Screen-centered positioning
- `center_window_on_parent()` - Parent-relative positioning
- `calculate_proportional_size()` - Dynamic sizing
- Screen boundary detection

## UI Architecture

### Component Hierarchy

```
TaskMoverApp (Main Window)
├── MenuBar
├── ToolBar
├── MainFrame
│   ├── RuleListFrame
│   │   ├── RuleListWidget
│   │   └── RuleControls
│   ├── PreviewFrame
│   └── StatusBar
└── Dialogs
    ├── SettingsDialog
    ├── RuleEditorDialog
    ├── ProgressDialog
    └── ConfirmDialog
```

### Dialog System

**SimpleDialog Base Class**
- Standardized dialog creation
- Proportional sizing support
- Consistent button layouts
- Parent-relative positioning

**Specialized Dialogs:**
- **SettingsDialog** - Application configuration
- **RuleEditorDialog** - Rule creation/editing
- **ProgressDialog** - Operation progress tracking
- **ConfirmDialog** - User confirmations

## Data Flow

### Configuration Flow
```
User Action → UI Component → Application Layer → ConfigManager → YAML Files
```

### Rule Processing Flow
```
File Detection → Rule Matching → Priority Sorting → Action Execution → Result Logging
```

### UI Update Flow
```
Data Change → Event Notification → UI Refresh → User Feedback
```

## Key Design Patterns

### 1. **Model-View Pattern**
- Core logic separated from UI
- Clean interfaces between layers
- Testable business logic

### 2. **Observer Pattern**
- Event-driven UI updates
- Loose coupling between components
- Reactive user interface

### 3. **Command Pattern**
- Undoable operations
- Operation queuing
- Progress tracking

### 4. **Factory Pattern**
- Dialog creation
- Component instantiation
- Configuration loading

## Error Handling Strategy

### Graceful Degradation
- Non-critical failures don't crash the app
- Fallback configurations available
- User-friendly error messages

### Logging Strategy
- Comprehensive operation logging
- Configurable log levels
- Separate log files for different components

### Recovery Mechanisms
- Automatic configuration backup
- Safe mode operation
- Manual recovery options

## Performance Considerations

### Efficient File Operations
- Lazy loading of file lists
- Batch operations where possible
- Progress feedback for long operations

### Memory Management
- Proper resource cleanup
- Efficient data structures
- Memory leak prevention

### UI Responsiveness
- Background processing for heavy operations
- Progressive UI updates
- Cancelable long-running tasks

## Security Considerations

### File Safety
- Path validation and sanitization
- Permission checking before operations
- Sandbox-like operation boundaries

### Configuration Security
- Input validation for all settings
- Safe default configurations
- Protection against malicious rules

## Extensibility Points

### Plugin Architecture (Future)
- Rule engine extensions
- Custom file operations
- UI theme system
- Additional file format support

### Configuration Extensions
- Custom rule types
- Advanced pattern matching
- Integration with external tools

## Testing Strategy

### Unit Testing
- Core logic components
- Utility functions
- Configuration management

### Integration Testing
- End-to-end workflows
- UI component interactions
- File operation validation

### Visual Testing
- Window positioning verification
- Proportional sizing validation
- Multi-monitor compatibility

---

This architecture provides a solid foundation for the current TaskMover functionality while allowing for future expansion and enhancement.
