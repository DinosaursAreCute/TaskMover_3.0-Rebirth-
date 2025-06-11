# TaskMover Documentation

## What’s New in 2.1.0

- Modularized UI logic into helper modules for maintainability and clarity.
- Removed the Theme Manager and all custom theme/color management features.
- Removed the Colors tab; all theme management is now handled by a built-in theme.
- Fixed all major theme application errors and UI crashes.
- Cleaned up all __pycache__ folders and checked for other unnecessary files.
- Added type hints and docstrings to all major functions in ui_settings_helpers.py and other helpers.
- Updated and clarified documentation for theme management and UI structure.
- Prevented crashes related to unsupported style keys (e.g., Menubar, Listbox, Text).
- Fixed all crashes related to theme application and widget styling.
- Broke circular imports and standardized function signatures across UI modules.
- Used PowerShell Remove-Item to clean up bytecode and __pycache__ folders.
- Improved code documentation and maintainability.
- All automated tests now pass reliably, including UI and non-UI tests.
- UI tests are automatically skipped in headless environments (e.g., CI servers).
- Documentation and developer comments updated for clarity and maintainability.

## Overview

TaskMover is a file organization tool designed to help users manage and organize their files efficiently. It provides a user-friendly interface and customizable rules for file organization.

## Quick Start Tutorial

See the [README.md](./README.md) for a step-by-step tutorial on installing, launching, and using TaskMover.

## Features

- Built-in theme for the UI (no custom theme or color management).
- Customizable file organization rules.
- Developer mode for advanced debugging.
- Integrated logging for better traceability.
- Automated tests for all major features.

## Setup

1. Clone the repository.
2. Install the required dependencies using `pip install -r requirements.txt`.
3. Run the application using `python -m taskmover`.

## Key Functions

### `run()`

**Description:**
Main function to initialize and run the TaskMover application.

**Key Steps:**

1. Configure the logger.
2. Define configuration paths.
3. Load or initialize rules.
4. Load user settings.
5. Dynamically apply themes and settings.
6. Set up the user interface.
7. Start the main application loop.

### `check_first_run(config_directory, base_directory_var, settings, save_settings, logger)`

**Purpose**: Checks if the application is being run for the first time, prompts the user to select a base directory, and saves the organization folder to the settings.

**Parameters**:

- `config_directory` (str): Path to the configuration directory.
- `base_directory_var` (tk.StringVar): Variable to store the base directory path.
- `settings` (dict): Application settings.
- `save_settings` (function): Function to save updated settings.
- `logger` (logging.Logger): Logger instance for logging events.

**Updates**:

- Prompts the user to select a folder to organize (`organisation_folder`).
- Saves the selected folder to the settings.

**Usage**:

```python
check_first_run(config_directory, base_directory_var, settings, save_settings, logger)
```

### `main(rules, logger)`

**Purpose**: Entry point for the application. Initializes the UI, loads settings, and starts the main loop.

**Parameters**:

- `rules` (dict): Dictionary of rules for file organization.
- `logger` (logging.Logger): Logger instance for logging events.

**Usage**:

```python
main(rules, logger)
```

### `browse_path(path_var, logger)`

**Purpose**: Opens a directory selection dialog and updates the provided path variable.

**Parameters**:

- `path_var` (tk.StringVar): Variable to store the selected path.
- `logger` (logging.Logger): Logger instance for logging events.

**Usage**:

```python
browse_path(path_var, logger)
```

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

### `save_settings(settings, logger)`

**Purpose**: Saves application settings to a YAML file.

**Parameters**:

- `settings` (dict): Settings to save.
- `logger` (logging.Logger): Logger instance for logging events.

**Usage**:

```python
save_settings(settings, logger)
```

### `organize_files(settings, rules, logger)`

**Purpose**: Organizes files in the folder specified by the `organisation_folder` setting.

**Parameters**:

- `settings` (dict): Application settings containing the organization folder.
- `rules` (dict): Dictionary of rules for organizing files.
- `logger` (logging.Logger): Logger instance for logging events.

**Usage**:

```python
organize_files(settings, rules, logger)
```

### `start_organization(settings, rules, logger)`

**Purpose**: Organizes files in the folder specified by the `organisation_folder` setting with progress updates.

**Parameters**:

- `settings` (dict): Application settings containing the organization folder.
- `rules` (dict): Dictionary of rules for organizing files.
- `logger` (logging.Logger): Logger instance for logging events.

**Usage**:

```python
start_organization(settings, rules, logger)
```

### `create_dummy_files(base_directory, logger)`

**Purpose**: Creates dummy files in the base directory for testing purposes.

**Parameters**:

- `base_directory` (str): Path to the base directory.
- `logger` (logging.Logger): Logger instance for logging events.

**Usage**:

```python
create_dummy_files(base_directory, logger)
```

### `show_license_info()`

**Description:**
Displays the license information in a message box.

### `setup_ui(root, base_path_var, rules, config_directory, style, settings, logger)`

**Description:**
Sets up the user interface, including the rule list, buttons, and menu bar.

**Parameters:**

- `root`: The main application window.
- `base_path_var`: The base directory path variable.
- `rules`: The file organization rules.
- `config_directory`: The configuration directory path.
- `style`: The UI style object.
- `settings`: The user settings.
- `logger`: The logger instance.

## Configuration

Settings are stored in `~/default_dir/config/settings.yml`. The following settings can be customized:

- `theme`: The UI theme.
- `developer_mode`: Enable or disable developer mode.
- `logging_level`: Set the logging level.
- `accent_color`, `background_color`, `text_color`: Customize UI colors.

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## `ui_helpers.py`

### `center_window(window)`

**Purpose**: Centers the given window on the screen.

**Parameters**:

- `window` (tk.Tk or tk.Toplevel): The window to center.

**Usage**:

```python
center_window(window)
```

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

### `trigger_developer_function(base_directory, logger)`

**Purpose**: Developer function to create dummy files in the base directory.

**Parameters**:

- `base_directory` (str): Path to the base directory.
- `logger` (logging.Logger): Logger instance for logging events.

**Usage**:

```python
trigger_developer_function(base_directory, logger)
```

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

## Theme System and UI Structure (v2.1.0+)

### Theme Management

- TaskMover now uses a single built-in theme for its appearance.
- The Theme Manager tab, custom themes, and color customization features have been removed as of v2.1.0.
- All color and theme customization is currently unavailable.

### How to Use

- Theme customization is not available in this version. The application uses a default built-in theme.

---

## Known Issues

- None as of v2.1.0.

This documentation provides a comprehensive overview of all functions in the TaskMover project, making it easier for developers to understand and contribute to the codebase.
