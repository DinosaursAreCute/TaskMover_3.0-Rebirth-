# TaskMover Documentation

Welcome to the comprehensive TaskMover documentation. This guide will help you get the most out of TaskMover's powerful file organization capabilities.

## 📚 Table of Contents

1. [Getting Started](#getting-started)
2. [User Interface Guide](#user-interface-guide)
3. [Creating Rules](#creating-rules)
4. [Advanced Features](#advanced-features)
5. [Configuration](#configuration)
6. [Troubleshooting](#troubleshooting)
7. [API Reference](#api-reference)

## Getting Started

### System Requirements

**Minimum Requirements:**
- Python 3.11 or higher
- 4GB RAM
- 50MB free disk space
- Internet connection (for initial setup)

**Recommended:**
- Python 3.12+
- 8GB RAM
- SSD storage
- Windows 10+, macOS 11+, or Ubuntu 20.04+

### Installation Guide

#### Method 1: Standard Installation
```bash
# Clone the repository
git clone https://github.com/yourusername/TaskMover.git
cd TaskMover

# Create virtual environment (recommended)
python -m venv taskmover-env
source taskmover-env/bin/activate  # On Windows: taskmover-env\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Launch TaskMover
python -m taskmover_redesign
```

#### Method 2: Development Installation
```bash
# For contributors and advanced users
git clone https://github.com/yourusername/TaskMover.git
cd TaskMover

# Install in development mode
pip install -e .
pip install -r requirements-dev.txt

# Run tests to verify installation
python -m pytest taskmover_redesign/tests/
```

### First Launch

1. **Welcome Screen**: TaskMover will display a welcome screen on first launch
2. **Choose Organization Folder**: Select the folder you want to organize (typically Downloads)
3. **Create First Rule**: Follow the guided setup to create your first organization rule
4. **Test Run**: Use preview mode to see how your rule will work

## User Interface Guide

### Main Window Layout

```
┌─────────────────────────────────────────────────────────────┐
│ File  Edit  View  Tools  Help                    [_ □ ×]    │
├─────────────────────────────────────────────────────────────┤
│ [New] [Add Rule] [Settings] [Preview] [Start]              │
├─────────────────────────────────────────────────────────────┤
│ ┌─ Rules ──────────────┐ ┌─ Preview ──────────────────────┐ │
│ │ ✓ PDF Documents      │ │ Files to be organized:         │ │
│ │ ✓ Photos by Date     │ │                                │ │
│ │ ⨯ Large Files        │ │ document.pdf → Documents/PDFs/  │ │
│ │ ✓ Music Files        │ │ photo.jpg → Pictures/2025/     │ │
│ │                      │ │ archive.zip → Archive/Large/   │ │
│ │ [Add Rule]           │ │                                │ │
│ └──────────────────────┘ └────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│ ┌─ Activity Log ─────────────────────────────────────────┐  │
│ │ [12:34:56] Started organization process                │  │
│ │ [12:34:57] Moved document.pdf to Documents/PDFs/      │  │
│ │ [12:34:58] Organization completed successfully         │  │
│ └────────────────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────────────┤
│ Ready │ 3 rules active │ Last run: 2 minutes ago │ 📁 Downloads │
└─────────────────────────────────────────────────────────────┘
```

### Menu System

#### File Menu
- **New Rule Set** (Ctrl+N): Create a new set of rules
- **Open Rule Set** (Ctrl+O): Load existing rules
- **Save Rule Set** (Ctrl+S): Save current rules
- **Import Rules**: Import rules from file
- **Export Rules**: Export rules to file
- **Start Organization** (F5): Begin file organization
- **Exit**: Close TaskMover

#### Edit Menu
- **Add Rule** (Ctrl+Shift+N): Create new organization rule
- **Edit Rule** (F2): Modify selected rule
- **Duplicate Rule**: Copy existing rule
- **Delete Rule** (Delete): Remove selected rule
- **Enable All Rules**: Activate all rules
- **Disable All Rules**: Deactivate all rules

#### View Menu
- **Refresh** (F5): Update file preview
- **Show Preview Panel**: Toggle preview visibility
- **Show Activity Log**: Toggle log visibility
- **Full Screen** (F11): Toggle full screen mode

#### Tools Menu
- **Settings** (Ctrl+,): Open preferences
- **Test Mode**: Enable safe testing mode
- **Generate Test Files**: Create sample files for testing
- **Plugin Manager**: Manage installed plugins
- **Developer Tools**: Advanced debugging tools

### Toolbar Functions

| Button | Function | Shortcut |
|--------|----------|----------|
| 🆕 New | Create new rule set | Ctrl+N |
| ➕ Add Rule | Add organization rule | Ctrl+Shift+N |
| ⚙️ Settings | Open preferences | Ctrl+, |
| 👁️ Preview | Show file changes | Ctrl+P |
| ▶️ Start | Begin organization | F5 |

## Creating Rules

### Rule Components

Every TaskMover rule consists of:

1. **Name**: Descriptive name for the rule
2. **Patterns**: File patterns to match (glob or regex)
3. **Destination**: Where to move matched files
4. **Conditions**: Additional matching criteria
5. **Actions**: What to do with matched files
6. **Priority**: Execution order (higher numbers first)

### Pattern Matching

#### Glob Patterns (Recommended)
```
*.pdf           # All PDF files
photo_*.jpg     # JPG files starting with "photo_"
*.{jpg,png,gif} # Multiple extensions
**/*.txt        # Text files in any subdirectory
```

#### Regular Expressions (Advanced)
```
^[A-Z].*\.pdf$     # PDFs starting with uppercase letter
\d{4}-\d{2}-\d{2}  # Files with date format YYYY-MM-DD
.*[Ss]creenshot.*  # Files containing "screenshot" or "Screenshot"
```

### Destination Patterns

#### Static Destinations
```
Documents/PDFs/           # Fixed folder
Pictures/Screenshots/     # Another fixed folder
Archive/                  # Simple archive folder
```

#### Dynamic Destinations
```
Pictures/{year}/          # Organize by file year
Documents/{extension}/    # Organize by file extension
Archive/{year}/{month}/   # Organize by year and month
Projects/{parent_folder}/ # Use parent folder name
```

### Example Rules

#### 1. Basic Document Organization
```yaml
name: "PDF Documents"
patterns: ["*.pdf"]
destination: "Documents/PDFs/"
active: true
priority: 10
```

#### 2. Photo Organization by Date
```yaml
name: "Photos by Year"
patterns: ["*.jpg", "*.png", "*.heic", "*.raw"]
destination: "Pictures/{year}/"
conditions:
  - type: "date_based"
    field: "created"
active: true
priority: 20
```

#### 3. Large File Archive
```yaml
name: "Large Files"
patterns: ["*"]
destination: "Archive/Large/"
conditions:
  - type: "size"
    operator: ">="
    value: "100MB"
active: false
priority: 5
```

#### 4. Project Files by Type
```yaml
name: "Code Projects"
patterns: ["*.py", "*.js", "*.html", "*.css"]
destination: "Projects/Code/{extension}/"
conditions:
  - type: "path_contains"
    value: "project"
active: true
priority: 15
```

### Rule Priority System

Rules are executed in priority order (highest first):
- **Priority 50+**: Critical rules (important files)
- **Priority 30-49**: High priority rules (common files)
- **Priority 10-29**: Normal priority rules (general organization)
- **Priority 1-9**: Low priority rules (catch-all rules)

### Conditional Rules

#### Size Conditions
```yaml
conditions:
  - type: "size"
    operator: ">="      # >=, <=, ==, !=
    value: "10MB"       # Supports KB, MB, GB, TB
```

#### Date Conditions
```yaml
conditions:
  - type: "date"
    field: "created"    # created, modified, accessed
    operator: ">"
    value: "2024-01-01"
```

#### Path Conditions
```yaml
conditions:
  - type: "path_contains"
    value: "project"
    case_sensitive: false
```

#### Extension Conditions
```yaml
conditions:
  - type: "extension"
    value: ["pdf", "doc", "docx"]
    exclude: false      # true to exclude these extensions
```

## Advanced Features

### Batch Operations

TaskMover can handle thousands of files efficiently:
- **Multi-threading**: Parallel processing for speed
- **Memory management**: Optimized for large file sets
- **Progress tracking**: Real-time progress updates
- **Error recovery**: Continues despite individual failures

### Custom Scripts

Execute custom Python scripts during organization:

```python
# scripts/custom_processor.py
def process_file(file_path, destination, metadata):
    """Custom file processing function"""
    if file_path.suffix == '.jpg':
        # Extract EXIF data
        from PIL import Image
        img = Image.open(file_path)
        exif = img.getexif()
        
        # Create date-based folder
        if exif:
            date_taken = exif.get(36867)  # DateTimeOriginal
            if date_taken:
                year = date_taken[:4]
                return f"Pictures/{year}/{file_path.name}"
    
    return destination
```

### Network Drive Support

Organize files across network locations:
- **UNC paths**: `\\server\share\folder`
- **Mapped drives**: `Z:\folder`
- **Cloud storage**: OneDrive, Dropbox, Google Drive
- **FTP/SFTP**: Remote file organization

### Plugin System

Extend TaskMover with custom plugins:

```python
# plugins/my_plugin.py
from taskmover_redesign.core.plugin_base import PluginBase

class MyPlugin(PluginBase):
    name = "My Custom Plugin"
    version = "1.0.0"
    
    def process_file(self, file_path, rule, context):
        # Custom file processing logic
        return super().process_file(file_path, rule, context)
    
    def get_settings_ui(self):
        # Return custom settings UI
        pass
```

## Configuration

### Configuration Files

TaskMover uses YAML configuration files:

#### Main Configuration (`config.yml`)
```yaml
# Application settings
app:
  theme: "flatly"
  startup_folder: "~/Downloads"
  auto_save: true
  check_updates: true

# Organization settings  
organization:
  default_action: "move"    # move, copy, link
  create_backups: true
  backup_location: "~/TaskMover/Backups"
  max_backups: 10

# Performance settings
performance:
  thread_count: 4
  batch_size: 100
  memory_limit: "512MB"

# Logging settings
logging:
  level: "INFO"           # DEBUG, INFO, WARNING, ERROR
  file_logging: true
  max_log_size: "10MB"
  log_retention: 30       # days
```

#### Rules Configuration (`rules.yml`)
```yaml
# Rule definitions
rules:
  pdf_docs:
    name: "PDF Documents"
    patterns: ["*.pdf"]
    destination: "Documents/PDFs/"
    active: true
    priority: 10
    
  photos:
    name: "Photos by Date"
    patterns: ["*.jpg", "*.png", "*.heic"]
    destination: "Pictures/{year}/"
    date_based: true
    active: true
    priority: 20
```

### Environment Variables

Set environment variables for advanced configuration:

```bash
# Linux/macOS
export TASKMOVER_CONFIG_DIR="~/.config/taskmover"
export TASKMOVER_LOG_LEVEL="DEBUG"
export TASKMOVER_THEME="darkly"

# Windows
set TASKMOVER_CONFIG_DIR="%APPDATA%\TaskMover"
set TASKMOVER_LOG_LEVEL=DEBUG
set TASKMOVER_THEME=darkly
```

### Command Line Options

```bash
# Launch with specific configuration
python -m taskmover_redesign --config /path/to/config

# Enable debug mode
python -m taskmover_redesign --debug

# Use specific theme
python -m taskmover_redesign --theme darkly

# Run in headless mode (no GUI)
python -m taskmover_redesign --headless --rules /path/to/rules.yml
```

## Troubleshooting

### Common Issues

#### Issue: Files not moving
**Symptoms**: Files appear in preview but don't move during organization
**Solutions**:
1. Check file permissions
2. Ensure destination folder exists and is writable
3. Verify no other programs are using the files
4. Run TaskMover as administrator (Windows)

#### Issue: Slow performance
**Symptoms**: Organization takes very long time
**Solutions**:
1. Increase thread count in settings
2. Reduce batch size for large files
3. Close other applications using system resources
4. Check available disk space

#### Issue: Rules not matching expected files
**Symptoms**: Expected files don't appear in preview
**Solutions**:
1. Test patterns using the rule editor's test feature
2. Check pattern syntax (glob vs regex)
3. Verify case sensitivity settings
4. Check if files are excluded by other rules

### Debug Mode

Enable debug mode for detailed troubleshooting:

```bash
python -m taskmover_redesign --debug
```

Debug mode provides:
- Detailed logging output
- Pattern matching explanations
- Performance metrics
- Memory usage information

### Log Files

Check log files for detailed error information:
- **Windows**: `%APPDATA%\TaskMover\logs\`
- **macOS**: `~/Library/Application Support/TaskMover/logs/`
- **Linux**: `~/.config/TaskMover/logs/`

### Reset Configuration

To reset TaskMover to default settings:

```bash
# Delete configuration directory
# Windows
rmdir /s "%APPDATA%\TaskMover"

# macOS
rm -rf "~/Library/Application Support/TaskMover"

# Linux
rm -rf "~/.config/TaskMover"
```

## API Reference

### Core Classes

#### ConfigManager
```python
from taskmover_redesign.core.config import ConfigManager

# Initialize configuration manager
config = ConfigManager("/path/to/config")

# Load settings
settings = config.load_settings()

# Save settings
config.save_settings(settings)
```

#### RuleManager
```python
from taskmover_redesign.core.rules import RuleManager

# Initialize rule manager
rules = RuleManager(config_manager)

# Add new rule
rules.add_rule(
    name="My Rule",
    patterns=["*.txt"],
    path="/destination/folder"
)

# Get active rules
active_rules = rules.get_active_rules()
```

#### FileOrganizer
```python
from taskmover_redesign.core.file_operations import FileOrganizer

# Initialize organizer
organizer = FileOrganizer("/source/folder", rules_dict)

# Start organization
organizer.start_organization(
    progress_callback=lambda p: print(f"Progress: {p}%"),
    completion_callback=lambda: print("Done!")
)
```

### Utility Functions

#### File Operations
```python
from taskmover_redesign.core.utils import (
    get_file_info,
    create_backup,
    validate_path,
    format_file_size
)

# Get file information
info = get_file_info("/path/to/file.txt")
print(f"Size: {info.size}, Created: {info.created}")

# Create backup
backup_path = create_backup("/path/to/file.txt")

# Validate path
is_valid = validate_path("/some/path")

# Format file size
size_str = format_file_size(1024000)  # "1.0 MB"
```

### Plugin Development

#### Base Plugin Class
```python
from taskmover_redesign.core.plugin_base import PluginBase

class MyPlugin(PluginBase):
    name = "My Plugin"
    version = "1.0.0"
    description = "Custom file processing plugin"
    
    def initialize(self, config):
        """Initialize plugin with configuration"""
        self.config = config
    
    def process_file(self, file_path, rule, context):
        """Process individual file"""
        # Custom processing logic
        return True
    
    def get_settings_ui(self):
        """Return settings UI widget"""
        return None
    
    def cleanup(self):
        """Cleanup resources when plugin is disabled"""
        pass
```

---

This documentation covers the essential aspects of using TaskMover. For more specific use cases or advanced configurations, please refer to the additional documentation files or contact support.
