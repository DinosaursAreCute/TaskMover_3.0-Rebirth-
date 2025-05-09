# TaskMover Documentation

This document provides detailed information about the functions used in TaskMover, including their purposes, parameters, and usage.

---

## `app.py`

### `check_first_run(config_directory, base_directory_var, logger)`
**Purpose**: Checks if the application is being run for the first time and prompts the user to select a base directory.

**Parameters**:
- `config_directory` (str): Path to the configuration directory.
- `base_directory_var` (tk.StringVar): Variable to store the base directory path.
- `logger` (logging.Logger): Logger instance for logging events.

**Usage**:
```python
check_first_run(config_directory, base_directory_var, logger)
```

---

### `main(rules, logger)`
**Purpose**: Entry point for the application. Initializes the UI, loads settings, and starts the main loop.

**Parameters**:
- `rules` (dict): Dictionary of rules for file organization.
- `logger` (logging.Logger): Logger instance for logging events.

**Usage**:
```python
main(rules, logger)
```

---

### `browse_path(path_var, logger)`
**Purpose**: Opens a directory selection dialog and updates the provided path variable.

**Parameters**:
- `path_var` (tk.StringVar): Variable to store the selected path.
- `logger` (logging.Logger): Logger instance for logging events.

**Usage**:
```python
browse_path(path_var, logger)
```

---

### `load_settings(logger)`
**Purpose**: Loads application settings from a YAML file. Creates default settings if the file does not exist.

**Parameters**:
- `logger` (logging.Logger): Logger instance for logging events.

**Returns**:
- `dict`: Loaded settings.

**Usage**:
```python
settings = load_settings(logger)
```

---

### `save_settings(settings, logger)`
**Purpose**: Saves application settings to a YAML file.

**Parameters**:
- `settings` (dict): Settings to save.
- `logger` (logging.Logger): Logger instance for logging events.

**Usage**:
```python
save_settings(settings, logger)
```

---

### `start_organization(base_directory, rules, logger)`
**Purpose**: Organizes files in the base directory based on the provided rules.

**Parameters**:
- `base_directory` (str): Path to the base directory.
- `rules` (dict): Dictionary of rules for file organization.
- `logger` (logging.Logger): Logger instance for logging events.

**Usage**:
```python
start_organization(base_directory, rules, logger)
```

---

### `create_dummy_files(base_directory, logger)`
**Purpose**: Creates dummy files in the base directory for testing purposes.

**Parameters**:
- `base_directory` (str): Path to the base directory.
- `logger` (logging.Logger): Logger instance for logging events.

**Usage**:
```python
create_dummy_files(base_directory, logger)
```

---

### `show_license_info()`
**Purpose**: Displays the license information in a message box.

**Parameters**:
- None

**Usage**:
```python
show_license_info()
```

---

## `ui_helpers.py`

### `center_window(window)`
**Purpose**: Centers the given window on the screen.

**Parameters**:
- `window` (tk.Tk or tk.Toplevel): The window to center.

**Usage**:
```python
center_window(window)
```

---

### `add_menubar_with_settings(window, style, settings, save_settings, logger, base_directory)`
**Purpose**: Adds a menubar with various settings options to the given window.

**Parameters**:
- `window` (tk.Tk): The main application window.
- `style` (ttkbootstrap.Style): The style instance for theming.
- `settings` (dict): Application settings.
- `save_settings` (function): Function to save settings.
- `logger` (logging.Logger): Logger instance for logging events.
- `base_directory` (str): Path to the base directory.

**Updates**:
- Added a "License Information" button under the "Help" menu. Clicking it calls `show_license_info()` to display the license details.

**Usage**:
```python
add_menubar_with_settings(window, style, settings, save_settings, logger, base_directory)
```

---

### `trigger_developer_function(base_directory, logger)`
**Purpose**: Developer function to create dummy files in the base directory.

**Parameters**:
- `base_directory` (str): Path to the base directory.
- `logger` (logging.Logger): Logger instance for logging events.

**Usage**:
```python
trigger_developer_function(base_directory, logger)
```

---

### `update_rule_list(rule_frame, rules, config_path, logger)`
**Purpose**: Updates the rule list in the UI.

**Parameters**:
- `rule_frame` (ttk.Frame): Frame containing the rule list.
- `rules` (dict): Dictionary of rules.
- `config_path` (str): Path to the configuration file.
- `logger` (logging.Logger): Logger instance for logging events.

**Usage**:
```python
update_rule_list(rule_frame, rules, config_path, logger)
```

---

### `edit_rule(rule_key, rules, config_path, logger, rule_frame)`
**Purpose**: Opens a window to edit a specific rule.

**Parameters**:
- `rule_key` (str): Key of the rule to edit.
- `rules` (dict): Dictionary of rules.
- `config_path` (str): Path to the configuration file.
- `logger` (logging.Logger): Logger instance for logging events.
- `rule_frame` (ttk.Frame): Frame containing the rule list.

**Usage**:
```python
edit_rule(rule_key, rules, config_path, logger, rule_frame)
```

---

### `delete_rule(rule_key, rules, config_path, logger, rule_frame)`
**Purpose**: Deletes a specific rule after user confirmation.

**Parameters**:
- `rule_key` (str): Key of the rule to delete.
- `rules` (dict): Dictionary of rules.
- `config_path` (str): Path to the configuration file.
- `logger` (logging.Logger): Logger instance for logging events.
- `rule_frame` (ttk.Frame): Frame containing the rule list.

**Usage**:
```python
delete_rule(rule_key, rules, config_path, logger, rule_frame)
```

---

### `delete_multiple_rules(rules, config_path, logger, rule_frame)`
**Purpose**: Opens a window to delete multiple rules after user confirmation.

**Parameters**:
- `rules` (dict): Dictionary of rules.
- `config_path` (str): Path to the configuration file.
- `logger` (logging.Logger): Logger instance for logging events.
- `rule_frame` (ttk.Frame): Frame containing the rule list.

**Usage**:
```python
delete_multiple_rules(rules, config_path, logger, rule_frame)
```

---

### `enable_all_rules(rules, config_path, rule_frame, logger)`
**Purpose**: Enables all rules.

**Parameters**:
- `rules` (dict): Dictionary of rules.
- `config_path` (str): Path to the configuration file.
- `rule_frame` (ttk.Frame): Frame containing the rule list.
- `logger` (logging.Logger): Logger instance for logging events.

**Usage**:
```python
enable_all_rules(rules, config_path, rule_frame, logger)
```

---

### `disable_all_rules(rules, config_path, rule_frame, logger)`
**Purpose**: Disables all rules.

**Parameters**:
- `rules` (dict): Dictionary of rules.
- `config_path` (str): Path to the configuration file.
- `rule_frame` (ttk.Frame): Frame containing the rule list.
- `logger` (logging.Logger): Logger instance for logging events.

**Usage**:
```python
disable_all_rules(rules, config_path, rule_frame, logger)
```

---

## `tests/test_app.py`

### `TestApp`
**Purpose**: Contains unit tests for core functions in `app.py`.

#### `setUp()`
**Purpose**: Sets up the test environment by initializing a mock logger and defining test paths.

#### `tearDown()`
**Purpose**: Cleans up test files and directories created during the tests.

#### `test_load_settings_creates_defaults()`
**Purpose**: Tests that default settings are created if no settings file exists.
**Assertions**:
- Checks that the `theme` and `developer_mode` keys exist in the settings.
- Verifies that the logger logs a success message.

#### `test_save_settings()`
**Purpose**: Tests that settings are saved to the correct file.
**Assertions**:
- Checks that the settings file exists after saving.
- Verifies that the logger logs a success message.

#### `test_create_dummy_files()`
**Purpose**: Tests that dummy files are created in the base directory.
**Assertions**:
- Checks that the base directory exists.
- Ensures that dummy files are created in the directory.
- Verifies that the logger logs messages for directory creation and file creation.
- Ensures cleanup after the test.

---

### Known Issues
- **Developer Settings Buttons**: The "Save" and "Cancel" buttons in the developer settings window are positioned outside the visible window.
- **Browse Button**: The "Browse" button is currently not available in some parts of the application.
- **Dummy Files**: Creating dummy files does not work as expected in certain scenarios.
- **Log Categories**: Logging categories are currently unavailable.

---

This section documents the automated tests included in the `tests/test_app.py` file, providing a health check for core functionalities.

This documentation provides a comprehensive overview of all functions in the TaskMover project, making it easier for developers to understand and contribute to the codebase.
