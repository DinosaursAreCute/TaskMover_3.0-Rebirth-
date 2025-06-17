# Testing Guide

## Overview

TaskMover includes a comprehensive testing suite designed to ensure reliability, maintainability, and quality across all components.

## Test Structure

### Test Organization
```
taskmover_redesign/tests/
├── __init__.py                    # Test package initialization
├── README.md                      # Test documentation
├── run_tests.py                   # Universal test runner
├── test_comprehensive.py          # Core functionality tests
├── test_window_management.py      # Window and UI tests
├── test_proportional_windows.py   # Interactive visual tests
├── test_imports.py                # Import validation
├── test_integration.py            # End-to-end tests
└── test_final_verification.py     # Final system validation
```

## Running Tests

### Quick Start
```bash
# Navigate to tests directory
cd taskmover_redesign/tests

# Run all tests
python run_tests.py

# Run specific test file
python test_comprehensive.py

# Interactive visual test
python test_proportional_windows.py
```

### Test Runner Options
```bash
# Run with verbose output
python run_tests.py --verbose

# Run specific test class
python run_tests.py test_comprehensive.TestConfigManager

# Run with coverage reporting
python run_tests.py --coverage
```

## Test Categories

### Unit Tests (`test_comprehensive.py`)

**Configuration Management Tests**
- Config file creation and loading
- Settings validation and persistence
- Error handling and recovery
- Backup and restore functionality

**Rule Management Tests**
- Rule creation, modification, deletion
- Pattern matching validation
- Priority sorting and conflict resolution
- Rule import/export functionality

**File Operations Tests**
- Safe file movement and copying
- Conflict resolution strategies
- Progress tracking and cancellation
- Rollback and recovery mechanisms

**Utility Function Tests**
- Safe filename generation
- Path validation and sanitization
- Helper function validation

### Window Management Tests (`test_window_management.py`)

**Proportional Sizing Tests**
- Screen dimension detection
- Proportional size calculation
- Minimum and maximum size constraints
- Multi-monitor compatibility

**Positioning Tests**
- Screen-centered positioning
- Parent-relative positioning
- Edge detection and boundary constraints
- Off-screen window recovery

**UI Integration Tests**
- Dialog creation with proportional sizing
- Window state persistence
- Theme compatibility
- Accessibility features

### Integration Tests (`test_integration.py`)

**End-to-End Workflows**
- Complete file organization process
- Settings modification and application
- Rule creation and execution
- Error scenarios and recovery

**Component Integration**
- UI to backend communication
- Configuration system integration
- File system interaction
- Event handling and notifications

### Visual Tests (`test_proportional_windows.py`)

**Interactive Testing**
- Visual verification of window positioning
- Manual testing of proportional sizing
- Multi-monitor behavior validation
- User experience verification

## Test Environment Setup

### Dependencies
The test suite requires:
- Python 3.8+
- unittest (standard library)
- tempfile (for temporary test directories)
- mock (for component isolation)
- tkinter (for UI testing)

### Isolation Strategy
Tests are designed to be completely isolated:
- **Temporary directories** for file operations
- **Mock objects** for external dependencies
- **No real file modifications** during testing
- **Clean state** between test runs

### Safety Measures
- All tests use temporary, isolated environments
- No modification of actual user files or settings
- Automatic cleanup after test completion
- Safe fallbacks for test failures

## Writing New Tests

### Test Naming Convention
- Test files: `test_<component>.py`
- Test classes: `Test<ComponentName>`
- Test methods: `test_<specific_behavior>`

### Example Test Structure
```python
import unittest
import tempfile
import os

class TestNewFeature(unittest.TestCase):
    """Test the new feature functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        # Additional setup
    
    def tearDown(self):
        """Clean up test environment."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_specific_behavior(self):
        """Test specific behavior of the feature."""
        # Arrange
        # Act
        # Assert
        pass
```

### Test Guidelines
1. **One concept per test** - Each test should verify one specific behavior
2. **Clear naming** - Test names should describe what is being tested
3. **Proper setup/teardown** - Always clean up test resources
4. **Assertions** - Use specific assertions that provide clear failure messages
5. **Documentation** - Include docstrings explaining test purpose

## Mock Usage

### Common Mock Patterns
```python
from unittest.mock import Mock, patch

# Mock file system operations
@patch('os.path.exists')
def test_file_check(self, mock_exists):
    mock_exists.return_value = True
    # Test code

# Mock window operations
def test_window_positioning(self):
    mock_window = Mock()
    mock_window.winfo_screenwidth.return_value = 1920
    mock_window.winfo_screenheight.return_value = 1080
    # Test code
```

### When to Use Mocks
- External file system operations
- Network or database connections
- GUI components (when testing logic only)
- Time-dependent operations
- Resource-intensive operations

## Continuous Integration

### Automated Testing
Tests are designed to run in automated environments:
- No GUI dependencies for core tests
- Cross-platform compatibility
- Reasonable execution time
- Clear pass/fail criteria

### Test Reports
The test runner provides:
- **Summary statistics** - Tests run, passed, failed, skipped
- **Detailed failure information** - Stack traces and error messages
- **Coverage information** - Code coverage statistics
- **Performance metrics** - Test execution times

## Debugging Tests

### Running Individual Tests
```bash
# Run specific test method
python -m unittest test_comprehensive.TestConfigManager.test_rules_save_and_load

# Run with debugging output
python test_comprehensive.py --debug

# Run single test with verbose output
python -m unittest -v test_comprehensive.TestConfigManager
```

### Common Debugging Techniques
1. **Print statements** in test methods for debugging
2. **Breakpoints** using pdb or IDE debugger
3. **Temporary files** inspection during test execution
4. **Mock introspection** to verify mock calls
5. **Error log analysis** for complex failures

## Performance Testing

### Test Performance Guidelines
- Tests should complete within reasonable time (< 30 seconds total)
- Individual tests should be fast (< 1 second each)
- Heavy operations should be mocked or minimized
- Resource cleanup should be efficient

### Performance Monitoring
```python
import time

def test_performance_critical_operation(self):
    """Test that operation completes within acceptable time."""
    start_time = time.time()
    
    # Operation to test
    result = some_operation()
    
    end_time = time.time()
    execution_time = end_time - start_time
    
    self.assertLess(execution_time, 1.0, "Operation took too long")
```

## Test Coverage

### Coverage Goals
- **Core modules**: 90%+ coverage
- **UI components**: 70%+ coverage (GUI testing limitations)
- **Utility functions**: 95%+ coverage
- **Integration paths**: Key workflows covered

### Measuring Coverage
```bash
# Install coverage tool
pip install coverage

# Run tests with coverage
coverage run run_tests.py
coverage report
coverage html  # Generate HTML report
```

## Best Practices

### Test Design
1. **Test behavior, not implementation** - Focus on what the code should do
2. **Use descriptive test names** - Anyone should understand what is being tested
3. **Keep tests simple** - Complex tests are hard to debug and maintain
4. **Test edge cases** - Include boundary conditions and error scenarios
5. **Maintain test independence** - Tests should not depend on each other

### Test Maintenance
1. **Update tests with code changes** - Keep tests synchronized with implementation
2. **Regular test review** - Periodically review test effectiveness
3. **Refactor test code** - Apply same quality standards as production code
4. **Remove obsolete tests** - Clean up tests for removed functionality
5. **Document test rationale** - Explain why specific tests exist

### Error Handling in Tests
```python
def test_error_handling(self):
    """Test that errors are handled gracefully."""
    with self.assertRaises(SpecificException):
        operation_that_should_fail()
    
    # Or test error recovery
    result = operation_with_fallback()
    self.assertTrue(result.success)
    self.assertIsNotNone(result.fallback_used)
```

## Troubleshooting

### Common Test Issues

**Tests failing on CI but passing locally:**
- Check for platform-specific behavior
- Verify environment variables and paths
- Look for timing-dependent issues

**Mock-related failures:**
- Verify mock setup and expectations
- Check that mocks are applied in correct scope
- Ensure mock cleanup between tests

**File system test issues:**
- Check temporary directory cleanup
- Verify file permissions
- Look for path separator issues across platforms

### Getting Help
- Check test output for specific error messages
- Review similar existing tests for patterns
- Consult the [CONTRIBUTING.md](../CONTRIBUTING.md) for development guidelines
- Create issues for persistent test problems

---

This testing guide provides the foundation for maintaining and expanding TaskMover's test coverage while ensuring code quality and reliability.
