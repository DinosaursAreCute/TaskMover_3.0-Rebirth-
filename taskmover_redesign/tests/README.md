# TaskMover Redesigned - Test Suite

This directory contains the comprehensive test suite for TaskMover Redesigned.

## Test Files

- **`test_comprehensive.py`** - Core functionality tests (config, rules, file operations)
- **`test_window_management.py`** - Window sizing and positioning tests  
- **`test_proportional_windows.py`** - Interactive test for proportional window sizing
- **`test_imports.py`** - Import validation tests
- **`test_integration.py`** - Integration tests
- **`test_final_verification.py`** - Final verification tests
- **`run_tests.py`** - Test runner script

## Running Tests

### Run All Tests
```bash
cd taskmover_redesign/tests
python run_tests.py
```

### Run Specific Test
```bash
python run_tests.py test_comprehensive
```

### Run Individual Test Files
```bash
python test_comprehensive.py
python test_window_management.py
```

### Interactive Window Test
```bash
python test_proportional_windows.py
```

## Test Coverage

The test suite covers:

✅ **Configuration Management**
- Config file creation and loading
- Settings validation and persistence
- Rule management

✅ **File Operations**  
- File organization logic
- Rule matching and application
- Safe file operations

✅ **Window Management**
- Proportional window sizing
- Screen-aware positioning
- Multi-monitor support

✅ **UI Components**
- Dialog creation and sizing
- Component integration
- Theme application

✅ **Import Validation**
- Module import verification
- Dependency checking
- API compatibility

## Test Environment

Tests use temporary directories and mock objects to avoid affecting the actual application or file system. All tests are designed to be:

- **Isolated** - Each test runs independently
- **Repeatable** - Tests produce consistent results
- **Fast** - Tests complete quickly
- **Safe** - No modification of real files or settings

## Contributing

When adding new features:

1. Add corresponding tests to the appropriate test file
2. Ensure all tests pass before submitting changes
3. Follow the existing test patterns and naming conventions
4. Update this README if adding new test files
