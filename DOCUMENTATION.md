# TaskMover Documentation

## What’s New in 2.0.0

- Major UI and UX improvements for rule management and settings.
- Full test automation for settings, dummy file creation, UI integration, themes, and color application.
- Colorful, detailed test logging for all automated tests.
- Expanded documentation and test case coverage.
- Improved error handling and logging throughout the application.
- Enhanced theme and color customization for the UI.
- Added developer tools and advanced logging for debugging.
- Improved compatibility with Windows and cross-platform environments.

## [2025-05-15] Codebase and Test Improvements

- The `load_settings` function now strictly validates the settings file and raises a `RuntimeError` if the file is invalid or missing required keys.
- UI tests are automatically skipped in headless environments (when no display is available), making CI and remote testing more robust.
- The test suite was refactored for better compatibility with Tkinter/ttkbootstrap and to avoid false negatives in CI.
- Exception handling and import issues were fixed for more reliable script and test execution.

### How to run tests in headless environments
- GUI-related tests will be skipped if no display is detected (e.g., on CI servers or remote shells).
- To run all tests, ensure a display is available (e.g., run locally on your desktop or use a virtual display on Linux).

### How to handle settings files
- The application expects a valid YAML settings file with all required keys. If the file is missing or invalid, a `RuntimeError` will be raised and should be handled appropriately.

## [2.1.0] - 2025-05-17

- All automated tests (UI and non-UI) now pass reliably on all supported platforms.
- UI tests are automatically skipped in headless environments (e.g., CI servers, remote shells).
- Theme Manager UI is fully stable, with all components covered by automated tests.
- Fixed duplicate/hidden Add Theme button logic and improved theme manager code structure.
- YAML config and theme file handling is now robust, with auto-fix and user prompt logic for broken/missing files.
- Documentation and developer comments updated for clarity and maintainability.

## Overview

TaskMover is a file organization tool designed to help users manage and organize their files efficiently. It provides a user-friendly interface and customizable rules for file organization.

## Quick Start Tutorial

See the [README.md](./README.md) for a step-by-step tutorial on installing, launching, and using TaskMover.

## Features

- Dynamic theme loading based on user settings.
- Customizable file organization rules.
- Developer mode for advanced debugging.
- Integrated logging for better traceability.
- Support for custom UI themes and colors.
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

## Theme System and UI Structure (v2.0+)

### Theme Manager

- The Theme Manager tab in Settings is now the single place for all theme customization.
- You can create, edit, save, apply, and delete custom themes.
- Only custom themes are editable; built-in themes are read-only and cannot be overwritten.
- Custom themes are included in the main theme selector in the General tab.
- All theme changes are applied live, and only supported widgets are styled (no more errors for Menubar, Listbox, or Text styling).

### Removal of Colors Tab

- The previous Colors tab has been removed for simplicity and to avoid confusion.
- All color and theme customization is now centralized in the Theme Manager.

### How to Use

1. Open the Settings window from the menu.
2. Go to the Theme Manager tab.
3. Select or create a custom theme.
4. Edit widget/button colors as desired.
5. Save and apply your custom theme.

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

### Known Issues

- **Developer Settings Buttons**: The "Save" and "Cancel" buttons in the developer settings window are positioned outside the visible window.
- **Browse Button**: The "Browse" button is currently not available in some parts of the application.
- **Dummy Files**: Creating dummy files does not work as expected in certain scenarios.
- **Log Categories**: Logging categories are currently unavailable.

This section documents the automated tests included in the `tests/test_app.py` file, providing a health check for core functionalities.

This documentation provides a comprehensive overview of all functions in the TaskMover project, making it easier for developers to understand and contribute to the codebase.
