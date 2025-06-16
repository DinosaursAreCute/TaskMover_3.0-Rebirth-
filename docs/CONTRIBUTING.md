# Contributing to TaskMover

Thank you for your interest in contributing to TaskMover! This guide will help you get started with development, testing, and submitting contributions.

## 🚀 Quick Start for Contributors

### Prerequisites

- **Python 3.11+** (recommended: Python 3.12)
- **Git** for version control
- **IDE/Editor** (VS Code recommended)
- **Virtual environment** (venv or conda)

### Development Setup

1. **Fork and Clone**
   ```bash
   # Fork the repository on GitHub first
   git clone https://github.com/yourusername/TaskMover.git
   cd TaskMover
   ```

2. **Set Up Environment**
   ```bash
   # Create virtual environment
   python -m venv taskmover-dev
   source taskmover-dev/bin/activate  # Windows: taskmover-dev\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # If available
   ```

3. **Verify Setup**
   ```bash
   # Run tests to ensure everything works
   cd taskmover_redesign
   python tests/test_imports.py
   python tests/test_integration.py
   python tests/test_final_verification.py
   
   # Launch app to test GUI
   python -m taskmover_redesign
   ```

## 📁 Project Structure

Understanding the codebase structure will help you contribute effectively:

```
TaskMover/
├── taskmover_redesign/          # 🚀 Main Application Package
│   ├── core/                    # 🧠 Business Logic
│   │   ├── config.py           # Configuration management
│   │   ├── rules.py            # Rule engine and processing
│   │   ├── file_operations.py  # File system operations
│   │   └── utils.py            # Utility functions
│   ├── ui/                     # 🎨 User Interface
│   │   ├── components.py       # Base UI components
│   │   ├── rule_components.py  # Rule management UI
│   │   └── settings_components.py # Settings dialogs
│   ├── tests/                  # 🧪 Test Suite
│   │   ├── test_imports.py     # Import validation
│   │   ├── test_integration.py # Integration tests
│   │   └── test_final_verification.py # End-to-end tests
│   ├── __init__.py             # Package initialization
│   ├── __main__.py             # CLI entry point
│   └── app.py                  # Main application class
├── docs/                       # 📚 Documentation
├── legacy/                     # 🗄️ Legacy code (v2.x)
├── README.md                   # Project overview
├── CHANGELOG.md               # Version history
└── requirements.txt           # Dependencies
```

## 🛠️ Development Guidelines

### Code Style

We follow Python best practices and PEP 8:

- **Line length**: Maximum 100 characters
- **Type hints**: Required for all functions and methods
- **Docstrings**: Google-style docstrings for all public APIs
- **Naming**: Clear, descriptive variable and function names
- **Comments**: Explain why, not what

### Example Code Style

```python
from typing import List, Optional, Dict, Any
from pathlib import Path

class RuleManager:
    """Manages file organization rules and their execution.
    
    This class provides methods for creating, editing, and executing
    file organization rules with proper error handling and logging.
    """
    
    def __init__(self, config_path: Path) -> None:
        """Initialize the rule manager.
        
        Args:
            config_path: Path to the configuration directory.
        """
        self.config_path = config_path
        self.rules: List[Dict[str, Any]] = []
    
    def create_rule(
        self, 
        name: str, 
        patterns: List[str], 
        destination: str,
        active: bool = True
    ) -> Optional[str]:
        """Create a new file organization rule.
        
        Args:
            name: Human-readable name for the rule.
            patterns: List of file patterns to match.
            destination: Target directory for matched files.
            active: Whether the rule should be active by default.
            
        Returns:
            Rule ID if successful, None if failed.
            
        Raises:
            ValueError: If required parameters are invalid.
        """
        if not name or not patterns:
            raise ValueError("Name and patterns are required")
        
        # Implementation here
        return rule_id
```

### Testing Requirements

All contributions must include appropriate tests:

#### Test Types

1. **Unit Tests**: Test individual functions and methods
2. **Integration Tests**: Test component interactions
3. **UI Tests**: Test user interface components
4. **End-to-End Tests**: Test complete workflows

#### Running Tests

```bash
# Run all tests
cd taskmover_redesign
python -m pytest tests/ -v

# Run specific test files
python tests/test_imports.py
python tests/test_integration.py
python tests/test_final_verification.py

# Run tests with coverage
python -m pytest tests/ --cov=taskmover_redesign --cov-report=html
```

#### Writing Tests

```python
import unittest
from unittest.mock import Mock, patch
from taskmover_redesign.core.rules import RuleManager

class TestRuleManager(unittest.TestCase):
    """Test cases for RuleManager class."""
    
    def setUp(self) -> None:
        """Set up test fixtures."""
        self.rule_manager = RuleManager("/tmp/test_config")
    
    def test_create_rule_success(self) -> None:
        """Test successful rule creation."""
        rule_id = self.rule_manager.create_rule(
            name="Test Rule",
            patterns=["*.txt"],
            destination="/test/destination"
        )
        self.assertIsNotNone(rule_id)
    
    def test_create_rule_invalid_name(self) -> None:
        """Test rule creation with invalid name."""
        with self.assertRaises(ValueError):
            self.rule_manager.create_rule("", ["*.txt"], "/test")
```

## 🎯 Contribution Types

### Bug Fixes

1. **Find or Create Issue**: Search existing issues or create a new one
2. **Reproduce Bug**: Include steps to reproduce in your issue
3. **Write Test**: Create a test that fails due to the bug
4. **Fix Bug**: Implement the fix
5. **Verify Fix**: Ensure your test now passes

### New Features

1. **Discuss First**: Open a GitHub discussion or issue for new features
2. **Design**: Consider API design and user experience
3. **Implement**: Write clean, tested code
4. **Document**: Update documentation and docstrings
5. **Test**: Include comprehensive tests

### Documentation

1. **Identify Gaps**: Find missing or unclear documentation
2. **Write Content**: Create clear, helpful documentation
3. **Review Examples**: Ensure all examples work correctly
4. **Update References**: Keep cross-references current

### Performance Improvements

1. **Profile First**: Use profiling tools to identify bottlenecks
2. **Benchmark**: Create benchmarks to measure improvements
3. **Optimize**: Implement performance improvements
4. **Verify**: Ensure improvements don't break functionality

## 📋 Pull Request Process

### Before Submitting

- [ ] **Tests Pass**: All existing tests pass
- [ ] **New Tests**: New functionality includes tests
- [ ] **Documentation**: Updated relevant documentation
- [ ] **Code Style**: Follows project coding standards
- [ ] **No Breaking Changes**: Unless discussed and approved

### Pull Request Template

```markdown
## Description
Brief description of the changes in this PR.

## Type of Change
- [ ] Bug fix (non-breaking change that fixes an issue)
- [ ] New feature (non-breaking change that adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed
- [ ] Performance impact assessed

## Checklist
- [ ] My code follows the project's style guidelines
- [ ] I have performed a self-review of my own code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have made corresponding changes to the documentation
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix is effective or that my feature works
```

### Review Process

1. **Automated Checks**: CI/CD pipeline runs automated tests
2. **Code Review**: Maintainers review code for quality and correctness
3. **Discussion**: Address feedback and make requested changes
4. **Approval**: Maintainer approval required before merge
5. **Merge**: Squash and merge with clear commit message

## 🌟 Areas Where We Need Help

### High Priority

- **Performance Optimization**: Improve file processing speed
- **UI/UX Improvements**: Enhance user experience
- **Cross-Platform Testing**: Test on different OS versions
- **Documentation**: Improve and expand user guides
- **Accessibility**: Make UI more accessible

### Medium Priority

- **Plugin System**: Develop plugin architecture
- **Cloud Integration**: Add cloud storage support
- **Mobile App**: Create mobile companion app
- **Internationalization**: Add support for multiple languages
- **Advanced Rules**: More sophisticated rule patterns

### Low Priority

- **Themes**: Create additional UI themes
- **Integrations**: Connect with other tools
- **Analytics**: Usage analytics and reporting
- **Enterprise Features**: Advanced features for business users

## 🏆 Recognition

Contributors are recognized in several ways:

- **Contributors Section**: Listed in README and documentation
- **Release Notes**: Mentioned in changelog for contributions
- **GitHub Recognition**: GitHub contributor statistics
- **Special Thanks**: Major contributors get special recognition

## 🤝 Community Guidelines

### Be Respectful

- **Inclusive Language**: Use welcoming and inclusive language
- **Constructive Feedback**: Provide helpful, actionable feedback
- **Patience**: Remember that contributors have different experience levels
- **Gratitude**: Thank others for their time and contributions

### Communication Channels

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: General questions and discussions
- **Pull Requests**: Code review and technical discussions
- **Email**: Direct contact for sensitive issues

### Code of Conduct

Please read and follow our [Code of Conduct](../CODE_OF_CONDUCT.md).

## 📚 Resources

### Learning Resources

- **Python Style Guide**: [PEP 8](https://pep8.org/)
- **Type Hints**: [Python Typing](https://docs.python.org/3/library/typing.html)
- **Testing**: [pytest Documentation](https://docs.pytest.org/)
- **Git**: [Git Handbook](https://guides.github.com/introduction/git-handbook/)

### Project Resources

- **Architecture**: [API Reference](API_REFERENCE.md)
- **User Guide**: [User Documentation](USER_GUIDE.md)
- **Roadmap**: [Future Features](TODO.md)
- **Changes**: [Changelog](../CHANGELOG.md)

## ❓ Getting Help

### For Contributors

- **Setup Issues**: Check GitHub issues or create a new one
- **Code Questions**: Use GitHub discussions
- **Design Decisions**: Open an issue for architectural discussions
- **General Help**: Contact maintainers directly

### For Users

- **User Guide**: Check the comprehensive user documentation
- **Troubleshooting**: Review common issues and solutions
- **Bug Reports**: Create GitHub issues with detailed information
- **Feature Requests**: Use GitHub discussions to propose new features

---

## 📞 Contact

- **Project Maintainer**: [Your Name](mailto:maintainer@taskmover.dev)
- **GitHub**: [@yourusername](https://github.com/yourusername)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/TaskMover/discussions)

Thank you for contributing to TaskMover! Every contribution, no matter how small, helps make the project better for everyone. 🚀

---

*This document is updated regularly. Last updated: [Current Date]*
