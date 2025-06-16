# TaskMover API Documentation

This document provides comprehensive API documentation for TaskMover's core components, suitable for developers who want to extend TaskMover or integrate it into other applications.

## Table of Contents

1. [Core Architecture](#core-architecture)
2. [Configuration API](#configuration-api)
3. [Rules Management API](#rules-management-api)
4. [File Operations API](#file-operations-api)
5. [UI Components API](#ui-components-api)
6. [Plugin Development API](#plugin-development-api)
7. [Examples](#examples)

## Core Architecture

TaskMover follows a modular architecture with clear separation between core logic and user interface:

```
taskmover_redesign/
├── core/           # Business logic and data management
├── ui/             # User interface components
├── tests/          # Test suite
└── app.py          # Main application entry point
```

### Key Design Principles

- **Separation of Concerns**: Core logic is independent of UI
- **Type Safety**: Full type annotations throughout
- **Extensibility**: Plugin-ready architecture
- **Testability**: Comprehensive test coverage

## Configuration API

### ConfigManager Class

The `ConfigManager` handles all configuration persistence and loading.

```python
from taskmover_redesign.core.config import ConfigManager
from pathlib import Path
from typing import Dict, Any

class ConfigManager:
    """Manages configuration files and settings persistence."""
    
    def __init__(self, config_directory: str = None):
        """
        Initialize configuration manager.
        
        Args:
            config_directory: Path to configuration directory.
                             If None, uses platform default.
        """
```

#### Methods

##### load_settings()
```python
def load_settings(self) -> Dict[str, Any]:
    """
    Load application settings from configuration file.
    
    Returns:
        Dictionary containing all application settings.
        Returns default settings if config file doesn't exist.
        
    Raises:
        ConfigurationError: If settings file is corrupted
    """
```

##### save_settings()
```python
def save_settings(self, settings: Dict[str, Any]) -> bool:
    """
    Save application settings to configuration file.
    
    Args:
        settings: Dictionary containing settings to save
        
    Returns:
        True if save was successful, False otherwise
        
    Raises:
        ConfigurationError: If unable to write to config file
    """
```

##### load_rules()
```python
def load_rules(self) -> Dict[str, Any]:
    """
    Load organization rules from configuration file.
    
    Returns:
        Dictionary containing all organization rules
        
    Raises:
        ConfigurationError: If rules file is corrupted
    """
```

##### save_rules()
```python
def save_rules(self, rules: Dict[str, Any]) -> bool:
    """
    Save organization rules to configuration file.
    
    Args:
        rules: Dictionary containing rules to save
        
    Returns:
        True if save was successful, False otherwise
    """
```

#### Usage Example

```python
# Initialize configuration manager
config = ConfigManager("/path/to/config")

# Load current settings
settings = config.load_settings()
print(f"Current theme: {settings.get('theme', 'flatly')}")

# Modify settings
settings['theme'] = 'darkly'
settings['auto_save'] = True

# Save updated settings
if config.save_settings(settings):
    print("Settings saved successfully")
```

## Rules Management API

### RuleManager Class

The `RuleManager` provides high-level rule management operations.

```python
from taskmover_redesign.core.rules import RuleManager
from taskmover_redesign.core.config import ConfigManager
from typing import Dict, Any, List, Tuple, Optional

class RuleManager:
    """Centralized rule management with CRUD operations."""
    
    def __init__(self, config_manager: ConfigManager):
        """
        Initialize rule manager.
        
        Args:
            config_manager: ConfigManager instance for persistence
        """
```

#### Properties

##### rules
```python
@property
def rules(self) -> Dict[str, Any]:
    """Get current rules dictionary."""
```

#### Methods

##### add_rule()
```python
def add_rule(self, name: str, patterns: Optional[List[str]] = None, 
             path: str = "", active: bool = True, priority: int = 10,
             **kwargs) -> bool:
    """
    Add a new organization rule.
    
    Args:
        name: Unique name for the rule
        patterns: List of file patterns to match (glob or regex)
        path: Destination path for matched files
        active: Whether rule is enabled
        priority: Execution priority (higher = earlier)
        **kwargs: Additional rule properties
        
    Returns:
        True if rule was added successfully
        
    Raises:
        ValueError: If rule name already exists or is invalid
    """
```

##### update_rule()
```python
def update_rule(self, name: str, **kwargs) -> bool:
    """
    Update an existing rule.
    
    Args:
        name: Name of rule to update
        **kwargs: Properties to update
        
    Returns:
        True if rule was updated successfully
        
    Raises:
        KeyError: If rule doesn't exist
    """
```

##### delete_rule()
```python
def delete_rule(self, name: str) -> bool:
    """
    Delete a rule.
    
    Args:
        name: Name of rule to delete
        
    Returns:
        True if rule was deleted successfully
        
    Raises:
        KeyError: If rule doesn't exist
    """
```

##### validate_rule()
```python
def validate_rule(self, rule_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validate rule data for correctness.
    
    Args:
        rule_data: Dictionary containing rule properties
        
    Returns:
        Tuple of (is_valid, list_of_error_messages)
    """
```

##### get_active_rules()
```python
def get_active_rules(self) -> Dict[str, Any]:
    """
    Get only active (enabled) rules.
    
    Returns:
        Dictionary containing only active rules
    """
```

#### Usage Example

```python
# Initialize managers
config = ConfigManager()
rules = RuleManager(config)

# Add a new rule
rules.add_rule(
    name="PDF Documents",
    patterns=["*.pdf"],
    path="Documents/PDFs",
    active=True,
    priority=20
)

# Update existing rule
rules.update_rule("PDF Documents", priority=30)

# Get active rules for processing
active_rules = rules.get_active_rules()
print(f"Found {len(active_rules)} active rules")
```

## File Operations API

### FileOrganizer Class

The `FileOrganizer` handles the actual file organization process.

```python
from taskmover_redesign.core.file_operations import FileOrganizer
from pathlib import Path
from typing import Dict, Any, Optional, Callable
import threading

class FileOrganizer:
    """Handles file organization operations with progress tracking."""
    
    def __init__(self, organization_folder: str, rules: Dict[str, Any]):
        """
        Initialize file organizer.
        
        Args:
            organization_folder: Path to folder containing files to organize
            rules: Dictionary of organization rules
        """
```

#### Methods

##### start_organization()
```python
def start_organization(self, 
                      progress_callback: Optional[Callable[[int], None]] = None,
                      file_moved_callback: Optional[Callable[[str, str], None]] = None,
                      completion_callback: Optional[Callable[[], None]] = None) -> bool:
    """
    Start the file organization process.
    
    Args:
        progress_callback: Called with progress percentage (0-100)
        file_moved_callback: Called when a file is moved (source, destination)
        completion_callback: Called when organization completes
        
    Returns:
        True if organization started successfully
        
    Raises:
        OrganizationError: If organization cannot start
    """
```

##### stop_organization()
```python
def stop_organization(self) -> None:
    """Stop the organization process if running."""
```

##### preview_organization()
```python
def preview_organization(self) -> List[Tuple[str, str]]:
    """
    Preview what files would be moved without actually moving them.
    
    Returns:
        List of (source_path, destination_path) tuples
    """
```

#### Usage Example

```python
# Initialize organizer
organizer = FileOrganizer("/path/to/organize", rules_dict)

# Set up callbacks
def on_progress(percent):
    print(f"Progress: {percent}%")

def on_file_moved(source, dest):
    print(f"Moved: {source} → {dest}")

def on_complete():
    print("Organization completed!")

# Start organization
organizer.start_organization(
    progress_callback=on_progress,
    file_moved_callback=on_file_moved,
    completion_callback=on_complete
)
```

### Utility Functions

#### get_file_info()
```python
from taskmover_redesign.core.utils import get_file_info, FileInfo
from pathlib import Path
from datetime import datetime

def get_file_info(file_path: Path) -> FileInfo:
    """
    Get comprehensive information about a file.
    
    Args:
        file_path: Path to the file
        
    Returns:
        FileInfo object containing file metadata
        
    Raises:
        FileNotFoundError: If file doesn't exist
    """

class FileInfo:
    """Container for file information."""
    size: int
    created: datetime
    modified: datetime
    accessed: datetime
    extension: str
    is_directory: bool
    permissions: str
```

#### validate_path()
```python
def validate_path(path: str) -> bool:
    """
    Validate if a path is accessible and writable.
    
    Args:
        path: Path to validate
        
    Returns:
        True if path is valid and writable
    """
```

#### format_file_size()
```python
def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted size string (e.g., "1.2 MB")
    """
```

## UI Components API

### Core UI Components

#### Tooltip Class
```python
from taskmover_redesign.ui.components import Tooltip
import tkinter as tk

class Tooltip:
    """Modern tooltip implementation."""
    
    def __init__(self, widget: tk.Widget, text: str, delay: int = 500):
        """
        Create tooltip for a widget.
        
        Args:
            widget: Widget to attach tooltip to
            text: Tooltip text to display
            delay: Delay in milliseconds before showing tooltip
        """
```

#### ProgressDialog Class
```python
from taskmover_redesign.ui.components import ProgressDialog

class ProgressDialog:
    """Progress dialog with cancel capability."""
    
    def __init__(self, parent: tk.Widget, title: str = "Progress"):
        """
        Create progress dialog.
        
        Args:
            parent: Parent widget
            title: Dialog title
        """
    
    def update_progress(self, percent: int, message: str = "") -> None:
        """Update progress bar and message."""
    
    def show(self) -> bool:
        """Show dialog and return True if not canceled."""
```

#### ConfirmDialog Class
```python
from taskmover_redesign.ui.components import ConfirmDialog

class ConfirmDialog:
    """Modern confirmation dialog."""
    
    def __init__(self, parent: tk.Widget, title: str, message: str):
        """
        Create confirmation dialog.
        
        Args:
            parent: Parent widget
            title: Dialog title
            message: Message to display
        """
    
    def show(self) -> bool:
        """Show dialog and return user's choice."""
```

### Rule Management UI

#### RuleEditor Class
```python
from taskmover_redesign.ui.rule_components import RuleEditor

class RuleEditor:
    """Rule editing dialog with validation."""
    
    def __init__(self, parent: tk.Widget, rules: Dict[str, Any], 
                 config_directory: str, rule_name: str = None):
        """
        Create rule editor dialog.
        
        Args:
            parent: Parent widget
            rules: Current rules dictionary
            config_directory: Configuration directory path
            rule_name: Name of rule to edit (None for new rule)
        """
    
    def show(self) -> Optional[str]:
        """
        Show dialog and return rule name if saved.
        
        Returns:
            Rule name if saved, None if canceled
        """
```

## Plugin Development API

### PluginBase Class

```python
from taskmover_redesign.core.plugin_base import PluginBase
from typing import Dict, Any, Optional
import tkinter as tk

class PluginBase:
    """Base class for TaskMover plugins."""
    
    # Plugin metadata (override in subclass)
    name: str = "Base Plugin"
    version: str = "1.0.0"
    description: str = "Base plugin class"
    author: str = ""
    
    def initialize(self, config: Dict[str, Any]) -> None:
        """
        Initialize plugin with configuration.
        
        Args:
            config: Plugin configuration dictionary
        """
    
    def process_file(self, file_path: str, rule: Dict[str, Any], 
                    context: Dict[str, Any]) -> bool:
        """
        Process a file during organization.
        
        Args:
            file_path: Path to file being processed
            rule: Rule that matched this file
            context: Processing context
            
        Returns:
            True if processing was successful
        """
    
    def get_settings_ui(self) -> Optional[tk.Widget]:
        """
        Return settings UI widget for this plugin.
        
        Returns:
            Tkinter widget for settings or None
        """
    
    def cleanup(self) -> None:
        """Cleanup resources when plugin is disabled."""
```

### Plugin Example

```python
from taskmover_redesign.core.plugin_base import PluginBase
from pathlib import Path
import shutil

class BackupPlugin(PluginBase):
    """Plugin that creates backups before moving files."""
    
    name = "Backup Plugin"
    version = "1.0.0"
    description = "Creates backups before moving files"
    author = "TaskMover Team"
    
    def initialize(self, config):
        self.backup_dir = config.get('backup_directory', '~/TaskMover/Backups')
        self.enabled = config.get('enabled', True)
    
    def process_file(self, file_path, rule, context):
        if not self.enabled:
            return True
            
        # Create backup before processing
        backup_path = Path(self.backup_dir) / Path(file_path).name
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            shutil.copy2(file_path, backup_path)
            return True
        except Exception as e:
            print(f"Backup failed: {e}")
            return False
```

## Examples

### Complete Organization Example

```python
from taskmover_redesign.core import ConfigManager, RuleManager, FileOrganizer
from pathlib import Path

def organize_downloads():
    """Complete example of organizing downloads folder."""
    
    # Initialize configuration
    config = ConfigManager()
    rules_manager = RuleManager(config)
    
    # Add rules for common file types
    rules_manager.add_rule(
        name="Documents",
        patterns=["*.pdf", "*.doc", "*.docx", "*.txt"],
        path="Documents",
        active=True,
        priority=20
    )
    
    rules_manager.add_rule(
        name="Images",
        patterns=["*.jpg", "*.png", "*.gif", "*.bmp"],
        path="Pictures",
        active=True,
        priority=25
    )
    
    rules_manager.add_rule(
        name="Archives",
        patterns=["*.zip", "*.rar", "*.7z", "*.tar.gz"],
        path="Archive",
        active=True,
        priority=15
    )
    
    # Get active rules
    active_rules = rules_manager.get_active_rules()
    
    # Initialize organizer
    downloads_path = str(Path.home() / "Downloads")
    organizer = FileOrganizer(downloads_path, active_rules)
    
    # Preview organization
    preview = organizer.preview_organization()
    print(f"Would move {len(preview)} files:")
    for source, dest in preview[:5]:  # Show first 5
        print(f"  {source} → {dest}")
    
    # Confirm and organize
    if input("Proceed with organization? (y/N): ").lower() == 'y':
        def progress_callback(percent):
            print(f"\rProgress: {percent}%", end="", flush=True)
        
        def completion_callback():
            print("\nOrganization completed!")
        
        organizer.start_organization(
            progress_callback=progress_callback,
            completion_callback=completion_callback
        )

if __name__ == "__main__":
    organize_downloads()
```

### Custom UI Component Example

```python
import tkinter as tk
from tkinter import ttk
import ttkbootstrap as ttkb
from taskmover_redesign.ui.components import Tooltip

class CustomFileList(ttk.Frame):
    """Custom file list widget with tooltips."""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        # Create listbox with scrollbar
        self.listbox = tk.Listbox(self, selectmode=tk.EXTENDED)
        scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.listbox.yview)
        self.listbox.config(yscrollcommand=scrollbar.set)
        
        # Layout
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Add tooltip
        Tooltip(self.listbox, "List of files to be organized")
        
        # Bind events
        self.listbox.bind('<Double-Button-1>', self.on_double_click)
    
    def add_file(self, file_path: str, destination: str):
        """Add file to the list."""
        display_text = f"{file_path} → {destination}"
        self.listbox.insert(tk.END, display_text)
    
    def clear(self):
        """Clear all files from list."""
        self.listbox.delete(0, tk.END)
    
    def get_selected_files(self):
        """Get selected file indices."""
        return self.listbox.curselection()
    
    def on_double_click(self, event):
        """Handle double-click on file."""
        selection = self.listbox.curselection()
        if selection:
            file_text = self.listbox.get(selection[0])
            print(f"Double-clicked: {file_text}")

# Usage example
if __name__ == "__main__":
    root = ttkb.Window(themename="flatly")
    
    file_list = CustomFileList(root)
    file_list.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # Add sample files
    file_list.add_file("document.pdf", "Documents/PDFs/")
    file_list.add_file("photo.jpg", "Pictures/2025/")
    file_list.add_file("archive.zip", "Archive/")
    
    root.mainloop()
```

### Testing Example

```python
import unittest
import tempfile
import shutil
from pathlib import Path
from taskmover_redesign.core import ConfigManager, RuleManager

class TestRuleManager(unittest.TestCase):
    """Test cases for RuleManager."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.config = ConfigManager(self.temp_dir)
        self.rules = RuleManager(self.config)
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)
    
    def test_add_rule(self):
        """Test adding a new rule."""
        result = self.rules.add_rule(
            name="Test Rule",
            patterns=["*.txt"],
            path="/test/path"
        )
        
        self.assertTrue(result)
        self.assertIn("Test Rule", self.rules.rules)
    
    def test_duplicate_rule_name(self):
        """Test adding rule with duplicate name."""
        self.rules.add_rule(name="Test Rule", patterns=["*.txt"], path="/test")
        
        with self.assertRaises(ValueError):
            self.rules.add_rule(name="Test Rule", patterns=["*.pdf"], path="/test")
    
    def test_rule_validation(self):
        """Test rule validation."""
        valid_rule = {
            "patterns": ["*.txt"],
            "path": self.temp_dir
        }
        
        invalid_rule = {
            "patterns": [],  # Empty patterns
            "path": ""       # Empty path
        }
        
        is_valid, errors = self.rules.validate_rule(valid_rule)
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)
        
        is_valid, errors = self.rules.validate_rule(invalid_rule)
        self.assertFalse(is_valid)
        self.assertGreater(len(errors), 0)

if __name__ == "__main__":
    unittest.main()
```

---

This API documentation provides a comprehensive guide for developers working with TaskMover's codebase. For additional examples and advanced usage patterns, please refer to the source code in the `taskmover_redesign` package.
