# TaskMover 3.0 Scripts Documentation

This document provides a comprehensive list of all scripts in the TaskMover 3.0 repository and their functions.

## Quick Reference Summary

| Script Type | Count | Main Purpose |
|-------------|-------|--------------|
| **Batch Files (.bat)** | 4 | Windows automation and setup |
| **Python Scripts (.py)** | 110+ | Core application, UI, tests, and utilities |
| **Main Entry Points** | 2 | Application launching (`__main__.py`, batch launchers) |
| **Test Scripts** | 25+ | Unit, integration, and UI testing |
| **UI Components** | 20+ | User interface components and widgets |
| **Core System Scripts** | 40+ | Business logic, patterns, rules, logging |
| **Example/Demo Scripts** | 5 | UI component demonstrations |
| **GitHub Automation** | 1 | Issue creation from checklists |

### Key Entry Points
- **Main Application**: `python -m taskmover` or `taskmover/__main__.py`
- **Development Setup**: `setup_dev_env.bat`
- **Testing**: `run_tests.bat` or `run_tests.py`
- **UI Testing**: `launch_test_gui.bat`
- **Workspace Cleanup**: `cleanup_workspace.bat`

## Table of Contents

1. [Root Level Scripts](#root-level-scripts)
2. [Main Application Scripts](#main-application-scripts)
3. [Core System Scripts](#core-system-scripts)
4. [UI Component Scripts](#ui-component-scripts)
5. [Test Scripts](#test-scripts)
6. [Example and Demo Scripts](#example-and-demo-scripts)
7. [GitHub Automation Scripts](#github-automation-scripts)
8. [Configuration Scripts](#configuration-scripts)

---

## Root Level Scripts

### Batch Files (.bat)

#### `cleanup_workspace.bat`
- **Purpose**: Cleans up the workspace by removing temporary files and artifacts
- **Function**: Maintains a clean development environment
- **Usage**: Run manually to clean workspace before commits or builds

#### `launch_test_gui.bat`
- **Purpose**: Interactive launcher for GUI test runners
- **Function**: Provides a menu-driven interface to select between:
  - Modern Test Runner (Recommended)
  - Simple Test Runner
- **Usage**: Double-click to launch or run from command line
- **Dependencies**: Requires Python and test GUI components

#### `run_tests.bat`
- **Purpose**: Comprehensive test suite launcher with multiple options
- **Function**: Provides menu-driven interface for:
  - Running all tests (console)
  - Launching GUI test runner with dark mode
  - Running specific test suites (unit, integration, UI)
  - Generating test reports
  - Quick import testing
- **Usage**: Primary entry point for testing workflows
- **Dependencies**: Python, pytest, test modules

#### `setup_dev_env.bat`
- **Purpose**: Development environment setup and initialization
- **Function**: 
  - Checks Python 3.11+ installation
  - Installs and configures Poetry
  - Sets up virtual environment
  - Installs dependencies
  - Creates project structure
  - Configures pre-commit hooks
  - Generates configuration files (.gitignore, pytest.ini, pre-commit config)
- **Usage**: First-time setup for new developers
- **Dependencies**: Python 3.11+, internet access for Poetry installation

### Python Scripts

#### `run_tests.py`
- **Purpose**: Comprehensive Python test runner with GUI and console support
- **Function**:
  - Runs test suites (unit, integration, UI tests)
  - Supports both console and GUI modes
  - Generates detailed test reports
  - Provides timeout management for tests
  - Loads test configuration from JSON
- **Usage**: `python run_tests.py [--gui|--suite <name>|--verbose|--report <file>]`
- **Dependencies**: unittest, subprocess, tkinter (for GUI)

---

## Main Application Scripts

#### `taskmover/__main__.py`
- **Purpose**: Main application entry point
- **Function**: 
  - Initializes and launches the TaskMover application
  - Handles import errors gracefully
  - Provides error handling for startup issues
- **Usage**: `python -m taskmover` or direct execution
- **Dependencies**: taskmover.ui.main_application

#### `taskmover/__init__.py`
- **Purpose**: Package initialization
- **Function**: Defines the TaskMover package structure and imports

---

## Core System Scripts

### Dependency Injection System
- **Location**: `taskmover/core/di/`
- **Purpose**: Provides dependency injection framework
- **Scripts**:
  - `container.py`: DI container implementation
  - `decorators.py`: Injection decorators
  - `interfaces.py`: DI interface definitions

### Logging System
- **Location**: `taskmover/core/logging/`
- **Purpose**: Comprehensive logging framework
- **Scripts**:
  - `manager.py`: Logging manager and configuration
  - `handlers.py`: Custom log handlers
  - `formatters.py`: Log formatting utilities
  - `config.py`: Logging configuration management
  - `exceptions.py`: Logging-specific exceptions
  - `interfaces.py`: Logging interface definitions
  - `utils.py`: Logging utility functions

### Pattern System
- **Location**: `taskmover/core/patterns/`
- **Purpose**: File pattern matching and processing
- **Scripts**:
  - `matching/unified_matcher.py`: Unified pattern matching engine
  - `models/query_ast.py`: Abstract syntax tree for queries
  - `models/query_ast_simple.py`: Simplified query AST
  - `parsing/intelligent_parser.py`: Smart pattern parser
  - `parsing/token_resolver.py`: Token resolution utilities
  - `storage/cache_manager.py`: Pattern cache management
  - `storage/repository.py`: Pattern storage repository
  - `suggestions/engine.py`: Pattern suggestion engine

### Rule System
- **Location**: `taskmover/core/rules/`
- **Purpose**: Rule definition and execution engine
- **Scripts**:
  - `engine.py`: Rule execution engine
  - `manager.py`: Rule management system
  - `models.py`: Rule data models
  - `serializers.py`: Rule serialization
  - `storage/repository.py`: Rule storage system
  - `storage/cache_manager.py`: Rule caching
  - `validation/validator.py`: Rule validation
  - `validation/schema.py`: Rule schema definitions

### Settings System
- **Location**: `taskmover/core/settings/`
- **Purpose**: Application configuration management
- **Scripts**:
  - `manager.py`: Settings management
  - `definitions.py`: Setting definitions
  - `serializers.py`: Settings serialization
  - `storage.py`: Settings storage backend
  - `validator.py`: Settings validation

### Conflict Resolution
- **Location**: `taskmover/core/conflict_resolution/`
- **Purpose**: File operation conflict handling
- **Scripts**:
  - `manager.py`: Conflict management
  - `resolver.py`: Conflict resolution logic
  - `strategies.py`: Resolution strategies
  - `models.py`: Conflict data models
  - `enums.py`: Conflict-related enumerations

### File Operations
- **Location**: `taskmover/core/file_operations/`
- **Purpose**: File system operations and management
- **Scripts**:
  - `manager.py`: File operation manager

---

## UI Component Scripts

### Main UI Components
- **Location**: `taskmover/ui/`

#### Core UI Scripts
- `main_application.py`: Main application window and controller
- `theme_manager.py`: UI theme and styling management
- `base_component.py`: Base class for UI components
- `layout_manager.py`: Layout management utilities

#### Specialized Components
- `input_components.py`: Input form components (text fields, dropdowns, etc.)
- `additional_input_components.py`: Extended input components
- `display_components.py`: Data display components
- `specialized_display_components.py`: Specialized display widgets
- `data_display_components.py`: Data visualization components
- `dialog_components.py`: Dialog and modal components
- `layout_components.py`: Layout and container components
- `navigation_components.py`: Navigation and menu components

#### Feature-Specific Components
- `file_organization_components.py`: File management UI components
- `pattern_management_components.py`: Pattern editing and management UI
- `rule_management_components.py`: Rule creation and editing UI
- `ruleset_management_components.py`: Ruleset management interface
- `execution_components.py`: Task execution and monitoring UI
- `history_components.py`: Operation history and logging UI
- `advanced_ui_features.py`: Advanced UI features and widgets

#### Testing and Development
- `component_tester.py`: UI component testing utilities
- `demo_gallery.py`: Component demonstration gallery
- `launch_gallery.py`: Gallery launcher script
- `doc_generator.py`: UI documentation generator
- `phase7_implementation.py`: Phase 7 UI implementation features

---

## Test Scripts

### Main Test Files
- **Location**: `tests/`

#### Core Test Files
- `test_app.py`: Main application testing
- `test_ui.py`: UI component testing
- `test_gui_runner.py`: GUI test runner implementation
- `test_utils.py`: Testing utilities and helpers
- `conftest.py`: Pytest configuration and fixtures

#### Unit Tests
- **Location**: `tests/unit/`
- `test_ui_imports.py`: UI import validation tests
- `test_theme_manager.py`: Theme manager unit tests
- `test_base_components.py`: Base component testing
- `test_core_exceptions.py`: Core exception handling tests
- `test_di_container.py`: Dependency injection container tests
- `test_logging_system.py`: Logging system unit tests
- `test_pattern_system.py`: Pattern system unit tests
- `test_rule_system.py`: Rule system unit tests

#### Integration Tests
- **Location**: `tests/integration/`
- `simple_test.py`: Basic integration test
- `test_conflict_resolution.py`: Conflict resolution integration tests
- `test_logging_integration.py`: Logging system integration tests
- `test_pattern_integration.py`: Pattern system integration tests
- `test_ui_integration.py`: UI integration tests

#### Test Infrastructure
- `tests/__init__.py`: Test package initialization
- `tests/fixtures/__init__.py`: Test fixtures
- `tests/manual/__init__.py`: Manual test cases
- `tests/performance/__init__.py`: Performance test framework

---

## Example and Demo Scripts

### UI Component Examples
- **Location**: `docs/ui_components/examples/`

#### `basic_form.py`
- **Purpose**: Demonstrates basic form components and layout
- **Function**: Shows usage of:
  - Custom labels and buttons
  - Entry fields with placeholder support
  - Basic form validation
- **Usage**: Run as standalone demo or reference for UI development

#### `layout_demo.py`
- **Purpose**: Demonstrates layout components and containers
- **Function**: Shows usage of:
  - Tab containers
  - Accordion panels
  - Card layouts
  - Panel components
- **Usage**: Layout design reference and testing

#### `data_display.py`
- **Purpose**: Data visualization component examples
- **Function**: Demonstrates data presentation widgets
- **Usage**: Reference for displaying structured data

#### `dialog_examples.py`
- **Purpose**: Dialog and modal component demonstrations
- **Function**: Shows various dialog types and interactions
- **Usage**: Reference for dialog implementation

#### `advanced_features.py`
- **Purpose**: Advanced UI feature demonstrations
- **Function**: Showcases complex UI interactions and components
- **Usage**: Reference for advanced UI development

---

## GitHub Automation Scripts

### `.github/scripts/checklist_to_issue.py`
- **Purpose**: Automatically creates GitHub issues from documentation checklists
- **Function**:
  - Scans `docs/Architecture/` directory for markdown files
  - Extracts unchecked checklist items (`- [ ] task`)
  - Creates GitHub issues using the GitHub API
  - Prevents duplicate issue creation
- **Usage**: Automated via GitHub Actions or manual execution
- **Dependencies**: `requests` library, GitHub token, repository access
- **Environment Variables**: `GITHUB_REPOSITORY`, `GITHUB_TOKEN`

---

## Configuration Scripts

### Package Initialization Scripts
- Various `__init__.py` files throughout the project that define package structure and imports
- **Locations**: 
  - `scripts/__init__.py`: Scripts package initialization
  - All module directories contain `__init__.py` for proper Python package structure

### Configuration Files (Non-Python)
While not Python scripts, these are important configuration files:
- `pyproject.toml`: Poetry project configuration
- `pytest.ini`: Test configuration
- `logging_config.yml`: Logging configuration
- `.pre-commit-config.yaml`: Pre-commit hook configuration

---

## Usage Guidelines

### For Developers
1. **First-time setup**: Run `setup_dev_env.bat` to initialize development environment
2. **Testing**: Use `run_tests.bat` for comprehensive testing or `python run_tests.py` for specific test suites
3. **UI Development**: Reference example scripts in `docs/ui_components/examples/`
4. **Component Testing**: Use `taskmover/ui/component_tester.py` for UI component validation

### For Users
1. **Main Application**: Run `python -m taskmover` to start the application
2. **Quick Testing**: Use the quick import test option in `run_tests.bat`

### For Maintenance
1. **Workspace Cleanup**: Run `cleanup_workspace.bat` regularly
2. **Test Validation**: Use GUI test runners for interactive testing
3. **Documentation**: Use `doc_generator.py` for UI component documentation

---

## Dependencies and Requirements

### Core Dependencies
- **Python 3.11+**: Required for all Python scripts
- **Poetry**: Dependency management (installed by setup script)
- **tkinter**: GUI framework (usually included with Python)
- **pytest**: Testing framework
- **PyYAML**: Configuration file parsing
- **colorama**: Console color output
- **ttkbootstrap**: Enhanced tkinter styling

### Development Dependencies
- **black**: Code formatting
- **mypy**: Type checking
- **ruff**: Code linting
- **pre-commit**: Git hook management
- **pytest plugins**: Testing extensions

### Optional Dependencies
- **requests**: GitHub API integration
- **sphinx**: Documentation generation

---

*This documentation is automatically generated and maintained. Last updated: [Current Date]*