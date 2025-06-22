# TaskMover

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)](./taskmover_redesign/tests/)
[![Status](https://img.shields.io/badge/status-beta%20development-orange.svg)](./docs/features/RULESET_MANAGEMENT.md)

> **⚠️ DEVELOPMENT IN PROGRESS**: TaskMover is currently undergoing significant enhancements! The Multiple Ruleset Management feature is being implemented and some functionality may be unstable. See [RULESET_MANAGEMENT.md](./docs/features/RULESET_MANAGEMENT.md) for details on the current development status.

**TaskMover** is a powerful, modern file organization tool that automatically organizes your files based on customizable rules and patterns. Say goodbye to cluttered folders and hello to an organized digital life!

> ⚠️ **Warning**  
> Ensure you have a backup of your files before running TaskMover. While the application is designed to be safe and reliable, unexpected issues may occur during file operations.

## ✨ Features

### 🎯 Core Functionality
- **Smart File Organization**: Automatically move files based on patterns, extensions, and custom rules
- **Rule-Based System**: Create powerful organization rules with glob patterns and regex support
- **Real-time Processing**: Watch folders and organize files as they arrive
- **Batch Operations**: Handle thousands of files efficiently
- **Undo Support**: Safely reverse organization operations

### 🎨 Modern Interface
- **Clean GUI**: Professional interface built with ttkbootstrap
- **Multiple Themes**: Light, dark, and custom themes
- **Drag & Drop**: Easy file and folder selection
- **Progress Tracking**: Real-time progress updates with detailed logging
- **Responsive Design**: Works great on any screen size

### 🛡️ Safety & Reliability
- **Preview Mode**: See what will happen before moving files
- **Backup Creation**: Automatic backups before major operations
- **Conflict Resolution**: Smart handling of duplicate files
- **Error Recovery**: Robust error handling and recovery mechanisms
- **Comprehensive Logging**: Detailed logs for troubleshooting

### 🔧 Advanced Features
- **Custom Scripts**: Run custom Python scripts during organization
- **File Validation**: Verify file integrity during moves
- **Network Support**: Organize files across network drives
- **Schedule Support**: Automatic organization on schedules
- **Plugin Architecture**: Extensible with custom plugins

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+** (recommended)
- **Windows 10+**, **macOS 10.15+**, or **Linux** (Ubuntu 18.04+)
- 50MB free disk space

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/TaskMover.git
   cd TaskMover
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run TaskMover:**
   ```bash
   python -m taskmover_redesign
   ```

### First Time Setup

1. **Launch TaskMover** - The application will open with a welcome screen
2. **Select Organization Folder** - Choose the folder you want to organize (e.g., Downloads)
3. **Create Your First Rule** - Click "Add Rule" and define your first organization rule
4. **Test & Organize** - Use preview mode to test, then run the organization

## 📖 User Guide

### Creating Rules

Rules are the heart of TaskMover. Each rule defines:
- **Patterns**: What files to match (e.g., `*.pdf`, `*.jpg`, `photo_*`)
- **Destination**: Where to move matched files
- **Conditions**: Additional criteria (file size, date, etc.)
- **Actions**: What to do with the files (move, copy, organize)

#### Example Rules

```yaml
# Documents Rule
name: "PDF Documents"
patterns: ["*.pdf", "*.doc", "*.docx"]
destination: "Documents/PDFs"
active: true

# Photos by Date
name: "Photos by Year"
patterns: ["*.jpg", "*.png", "*.heic"]
destination: "Pictures/{year}"
date_based: true
active: true

# Large Files
name: "Large Files"
patterns: ["*"]
destination: "Archive/Large"
min_size: "100MB"
active: false
```

### Organization Modes

1. **Preview Mode**: See what will happen without moving files
2. **Move Mode**: Move files to their destinations
3. **Copy Mode**: Copy files while keeping originals
4. **Archive Mode**: Compress files during organization

### Settings & Configuration

Access settings through **File → Settings** or **Ctrl+,**:

- **Appearance**: Themes, colors, and UI preferences
- **Behavior**: Default actions, confirmations, and safety settings
- **Performance**: Thread count, memory usage, and optimization
- **Advanced**: Logging levels, plugin management, and expert options

## 📁 Project Structure

```
TaskMover/
├── taskmover_redesign/          # 🚀 Main Application
│   ├── core/                    # 🧠 Business Logic
│   │   ├── config.py           # Configuration management
│   │   ├── rules.py            # Rule engine and management
│   │   ├── file_operations.py  # File organization operations
│   │   └── utils.py            # Utility functions
│   ├── ui/                     # 🎨 User Interface
│   │   ├── components.py       # Reusable UI components
│   │   ├── rule_components.py  # Rule management interface
│   │   └── settings_components.py # Settings and preferences
│   ├── tests/                  # 🧪 Test Suite
│   └── app.py                  # Main application entry point
├── docs/                       # 📚 Documentation
├── legacy/                     # 🗄️ Legacy Code (v2.x)
├── README.md                   # This file
├── CHANGELOG.md               # Version history
└── requirements.txt           # Python dependencies
```

## 🧪 Testing

TaskMover includes a comprehensive test suite to ensure reliability:

```bash
# Run all tests
cd taskmover_redesign
python -m pytest tests/ -v

# Run specific test types
python tests/test_imports.py      # Import verification
python tests/test_integration.py  # Integration tests
python tests/test_final_verification.py # End-to-end tests
```

### Test Coverage
- ✅ Core functionality tests
- ✅ UI component tests
- ✅ Integration tests
- ✅ Performance tests
- ✅ Error handling tests

## 🎨 Themes & Customization

TaskMover supports multiple beautiful themes:

### Built-in Themes
- **Flatly** (default): Clean, modern light theme
- **Darkly**: Professional dark theme
- **Cosmo**: Vibrant and colorful
- **Solar**: High contrast theme
- **And 20+ more**: Full ttkbootstrap theme library

### Custom Themes
Create your own themes by modifying the theme configuration files in the settings directory.


## 🛠️ Configuration

### Configuration Files

TaskMover stores configuration in your user directory:

- **Windows**: `%APPDATA%\TaskMover\`
- **macOS**: `~/Library/Application Support/TaskMover/`
- **Linux**: `~/.config/TaskMover/`

### Configuration Structure
```
TaskMover/
├── config.yml        # Main application settings
├── rules.yml         # Organization rules
├── themes.yml        # Custom theme definitions
├── plugins/          # Plugin configurations
└── logs/             # Application logs
```

## 🤝 Contributing

We welcome contributions! Here's how to get started:

### Development Setup

1. **Fork the repository** on GitHub
2. **Clone your fork:**
   ```bash
   git clone https://github.com/yourusername/TaskMover.git
   cd TaskMover
   ```
3. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
4. **Install development dependencies:**
   ```bash
   pip install -r requirements-dev.txt
   ```
5. **Run tests to verify setup:**
   ```bash
   python -m pytest taskmover_redesign/tests/
   ```

### Making Changes

1. **Create a feature branch:**
   ```bash
   git checkout -b feature/amazing-feature
   ```
2. **Make your changes** following the code style guidelines
3. **Add tests** for new functionality
4. **Run the test suite:**
   ```bash
   python -m pytest taskmover_redesign/tests/ -v
   ```
5. **Commit your changes:**
   ```bash
   git commit -m "Add amazing feature"
   ```
6. **Push to your fork:**
   ```bash
   git push origin feature/amazing-feature
   ```
7. **Open a Pull Request** on GitHub

### Code Style Guidelines

- Follow **PEP 8** formatting standards
- Use **type hints** for all function parameters and return values
- Write **comprehensive docstrings** for all public functions and classes
- Add **unit tests** for new features
- Keep **line length under 100 characters**
- Use **meaningful variable and function names**

## 📜 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

### What this means:
- ✅ Commercial use allowed
- ✅ Modification allowed
- ✅ Distribution allowed
- ✅ Private use allowed
- ❌ No warranty provided
- ❌ No liability assumed

## 🙏 Acknowledgments

### Built Using:
- **[Python](https://python.org)** - Core language
- **[ttkbootstrap](https://ttkbootstrap.readthedocs.io/)** - Modern UI components
- **[PyYAML](https://pyyaml.org/)** - Configuration management
- **[pytest](https://pytest.org/)** - Testing framework

### Getting Help
- 📖 **Documentation**: Check the [docs folder](docs/) for detailed guides

### Community Guidelines
Please read our [Code of Conduct](CODE_OF_CONDUCT.md) to understand our community standards.

### Roadmap
Check out our [roadmap](docs/TODO.md) to see what's coming next!

---

<div align="center">

**TaskMover** - *Organize your digital life, one file at a time* ✨

[🏠 Home](https://github.com/DinosaursAreCute/TaskMover) • 
[📖 Docs](docs/) • 
[🚀 Releases](https://github.com/DinosaursAreCute/TaskMover/releases) • 
[💬 Community](https://github.com/DinosaursAreCute/TaskMover/discussions)

*Made by Dino*

</div>
