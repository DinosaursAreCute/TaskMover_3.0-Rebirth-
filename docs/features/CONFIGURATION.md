# Configuration System

## Overview

TaskMover uses a flexible, YAML-based configuration system that manages both application settings and file organization rules. The system is designed for reliability, extensibility, and user-friendliness.

## Configuration Files

### Default Location
All configuration files are stored in:
```
~/default_dir/config/
```

On Windows, this translates to:
```
C:\Users\<username>\default_dir\config\
```

### Configuration Files

#### `settings.yml` - Application Settings
Contains global application preferences and behavior settings.

**Example structure:**
```yaml
# Application theme
theme: "flatly"

# Default organization folder
organisation_folder: "C:/Users/user/Downloads"

# Developer mode (enables debug logging)
developer_mode: false

# Logging configuration
logging_level: "INFO"
logging_components:
  UI: true
  File Operations: true
  Rules: true
  Settings: true

# UI preferences
collapse_on_start: true
auto_save: true
confirm_deletions: true
show_tooltips: true

# Window management
window_settings:
  main_window:
    width_ratio: 0.6
    height_ratio: 0.7
    remember_position: true
  dialogs:
    width_ratio: 0.4
    height_ratio: 0.5
```

#### `rules.yml` - File Organization Rules
Contains all file organization rules with their patterns and destinations.

**Example structure:**
```yaml
rule_001:
  name: "Text Documents"
  patterns:
    - "*.txt"
    - "*.rtf"
    - "*.doc"
    - "*.docx"
  path: "Documents/Text Files"
  active: true
  priority: 1
  description: "Organize text documents"

rule_002:
  name: "Images"
  patterns:
    - "*.jpg"
    - "*.jpeg"
    - "*.png"
    - "*.gif"
    - "*.bmp"
  path: "Pictures/Sorted"
  active: true
  priority: 2
  description: "Organize image files"
```

## Configuration Management

### ConfigManager Class

The `ConfigManager` class provides centralized configuration handling with the following features:

#### Initialization
```python
from taskmover_redesign.core import ConfigManager

# Use default config directory
config_manager = ConfigManager()

# Use custom config directory
config_manager = ConfigManager("/path/to/custom/config")
```

#### Loading Configuration
```python
# Load application settings
settings = config_manager.load_settings()

# Load file organization rules
rules = config_manager.load_rules()
```

#### Saving Configuration
```python
# Save settings
success = config_manager.save_settings(settings_dict)

# Save rules
success = config_manager.save_rules(rules_dict)
```

### Automatic Features

#### Default Configuration Creation
When no configuration files exist, the system automatically creates sensible defaults:

**Default Settings:**
- Theme: "flatly"
- Organization folder: User's Downloads folder
- Developer mode: disabled
- Auto-save: enabled
- Logging: INFO level

**Default Rules:**
- Basic file type organization rules
- Common document, image, and media patterns
- Organized by file type and purpose

#### Error Recovery
The system includes robust error handling:

- **Corrupted files** - Automatically backed up and regenerated
- **Missing files** - Created with defaults
- **Invalid YAML** - Logged and replaced with working configuration
- **Permission errors** - Graceful fallback to read-only mode

#### Backup System
Automatic backups are created:
- Before any configuration change
- On application startup (if files exist)
- When errors are detected
- Backup files include timestamps

## Settings Categories

### Application Settings

#### Theme Configuration
```yaml
theme: "flatly"  # Available: flatly, darkly, cosmo, journal, etc.
```

#### File Organization
```yaml
organisation_folder: "/path/to/organize"
auto_backup: true
create_missing_folders: true
conflict_resolution: "rename"  # Options: rename, skip, overwrite
```

#### User Interface
```yaml
collapse_on_start: true
show_tooltips: true
confirm_deletions: true
window_animations: true
```

#### Logging
```yaml
logging_level: "INFO"  # DEBUG, INFO, WARNING, ERROR
logging_components:
  UI: true
  File Operations: true
  Rules: true
  Settings: true
```

#### Developer Options
```yaml
developer_mode: false
debug_logging: false
performance_monitoring: false
```

### Rule Configuration

#### Rule Structure
```yaml
rule_id:
  name: "Human-readable name"
  patterns: ["*.ext", "pattern*"]
  path: "relative/destination/path"
  active: true
  priority: 1
  description: "Optional description"
  advanced_options:
    case_sensitive: false
    regex_patterns: false
    exclude_patterns: []
```

#### Pattern Matching
- **Wildcards**: `*.txt`, `file*.doc`
- **Multiple patterns**: List of patterns for each rule
- **Case sensitivity**: Configurable per rule
- **Exclusions**: Patterns to exclude from rule matching

#### Priority System
- Rules are processed in priority order (1 = highest)
- Lower numbers = higher priority
- Equal priorities processed in alphabetical order

## Configuration Validation

### Settings Validation
The system validates all settings on load:

- **Data types** - Ensures correct types for all values
- **Value ranges** - Validates numeric ranges and options
- **Path validation** - Checks if specified paths exist or can be created
- **Theme validation** - Verifies theme availability

### Rule Validation
Rules are validated for:

- **Pattern syntax** - Ensures valid wildcard patterns
- **Path validity** - Checks destination path format
- **Circular references** - Prevents infinite rule loops
- **Duplicate patterns** - Warns about conflicting rules

### Error Reporting
Validation errors are:
- Logged with detailed descriptions
- Displayed to user when appropriate
- Automatically corrected when possible
- Backed up before correction

## Advanced Configuration

### Custom Configuration Locations
```python
# Environment variable
os.environ['TASKMOVER_CONFIG'] = '/custom/path'

# Command line argument
taskmover --config-dir /custom/path

# Programmatic override
ConfigManager(config_dir='/custom/path')
```

### Configuration Import/Export
```python
# Export configuration
config_manager.export_config('backup.json')

# Import configuration
config_manager.import_config('backup.json')

# Export rules only
config_manager.export_rules('rules_backup.yml')
```

### Template System
Pre-defined configuration templates:

- **Basic User** - Simple file organization
- **Power User** - Advanced rules and customization
- **Developer** - Debug options and logging enabled
- **Minimal** - Lightweight configuration

## Migration and Upgrades

### Configuration Migration
When upgrading TaskMover:

1. **Backup creation** - Current config backed up automatically
2. **Schema validation** - Config checked against new requirements
3. **Automatic migration** - Settings migrated to new format
4. **User notification** - Changes reported to user
5. **Rollback option** - Ability to revert if needed

### Version Compatibility
- **Forward compatibility** - Newer versions read older configs
- **Schema versioning** - Config format versions tracked
- **Deprecation warnings** - Old settings marked for removal
- **Smooth transitions** - Gradual migration of deprecated features

## Troubleshooting

### Common Issues

#### Configuration Not Loading
1. Check file permissions
2. Verify YAML syntax
3. Look for backup files
4. Reset to defaults if needed

#### Rules Not Working
1. Validate pattern syntax
2. Check rule priority order
3. Verify destination paths exist
4. Test patterns individually

#### Settings Not Persisting
1. Check write permissions to config directory
2. Verify disk space availability
3. Look for file locking issues
4. Check antivirus interference

### Debug Tools

#### Configuration Validation
```bash
# Validate current configuration
python -m taskmover_redesign --validate-config

# Check specific rule patterns
python -m taskmover_redesign --test-patterns "*.txt"
```

#### Reset Options
```bash
# Reset all settings to defaults
python -m taskmover_redesign --reset-settings

# Reset rules to defaults
python -m taskmover_redesign --reset-rules

# Complete reset
python -m taskmover_redesign --factory-reset
```

### Log Analysis
Configuration issues are logged with specific error codes:

- **CONFIG_001** - File not found
- **CONFIG_002** - Invalid YAML syntax
- **CONFIG_003** - Validation failure
- **CONFIG_004** - Permission error
- **CONFIG_005** - Backup/restore operation

## Best Practices

### Configuration Management
1. **Regular backups** - Keep copies of working configurations
2. **Version control** - Track configuration changes
3. **Documentation** - Comment complex rules
4. **Testing** - Test rule changes in dry-run mode
5. **Gradual changes** - Make incremental modifications

### Rule Organization
1. **Logical grouping** - Group related rules by priority
2. **Clear naming** - Use descriptive rule names
3. **Pattern specificity** - Make patterns as specific as needed
4. **Regular review** - Periodically review and update rules

### Performance Optimization
1. **Rule order** - Place most common patterns first
2. **Pattern efficiency** - Use efficient wildcard patterns
3. **Path optimization** - Keep destination paths short
4. **Regular cleanup** - Remove unused rules

---

The configuration system provides a robust foundation for managing TaskMover's behavior while remaining user-friendly and maintainable.
