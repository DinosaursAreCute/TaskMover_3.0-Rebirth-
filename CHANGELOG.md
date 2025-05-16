# Changelog

## [Unreleased] - 2025-05-16

### UI/UX Changes

- Progress window label changed from 'Organizing files, please wait...' to 'File organization in progress...'.
- When file organization completes, the label now updates to 'File organization complete.'

### Changed

- Improved `load_settings` to strictly validate settings and raise `RuntimeError` for invalid files.
- UI tests now skip automatically in headless environments (no display), improving CI reliability.
- Refactored test suite for better compatibility with Tkinter/ttkbootstrap and headless systems.

### Fixed

- Fixed import and exception handling issues for robust test and script execution.

## [2.0.0] - 2025-05-12

### Major Changes

- Major UI and UX improvements for rule management and settings.
- Added full test automation for settings, dummy file creation, UI integration, themes, and color application.
- Colorful, detailed test logging for all automated tests.
- Expanded documentation and test case coverage.
- Improved error handling and logging throughout the application.
- Enhanced theme and color customization for the UI.
- Added developer tools and advanced logging for debugging.
- Improved compatibility with Windows and cross-platform environments.

### Fixed

- Fixed the "Browse" button in the rule edit window to be available and functional.
- Fixed UI issues with the "Save" and "Cancel" buttons in the developer settings window.
- Fixed dummy file creation to work in all scenarios.
- Fixed UI bugs and improved widget layout.
- Fixed bugs where colors could not be changed
- Fixed issue where theme could not be changed
- Fixed issue where ui would sometimes not load
- Fixed issue where rules would not display filepath
- Fixed issue where patterns would not correctly display
- Fixed issue where user could not change organisation directory
- Fixed issue where settings would not be saved properly
- FIxed issue where settings for color  and loggers would not get saved
- Fixed issue where settings would not get loaded properly

### Known Bugs

- [] Default colors do not match themes default colors resulting in wrong colors until
     color reset.

---

## [1.2.1.5] - 2025-05-12

### Added

### Improved

### Fixed

- Fixed the "Browse" button in the rule edit window to be available and functional.
- Fixed UI issues with the "Save" and "Cancel" buttons in the developer settings window to ensure they are positioned correctly within the visible window.
- Fixed the dummy file creation functionality to work as expected in all scenarios.
- Fixed UI bugs

### Known Bugs

- [ ] **Developer Settings Buttons**: The "Save" and "Cancel" buttons in the developer settings window are positioned outside the visible window.
- [ ] **Browse Button**: The "Browse" button is currently not available in some parts of the application.
- [ ] **Dummy Files**: Creating dummy files does not work as expected in certain scenarios.
- [ ] **Log Categories**: Logging categories currently unavailable.

## [1.2.1] - 2025-05-11

### Added

- Added a "License Information" button to the menu bar under the "Help" menu. Clicking it displays the license details in a message box.

### Improved

- Enhanced the `test_create_dummy_files` test to verify specific log messages for each dummy file created.

### Known Bugs

- [ ] **Developer Settings Buttons**: The "Save" and "Cancel" buttons in the developer settings window are positioned outside the visible window.
- [ ] **Browse Button**: The "Browse" button is currently not available in some parts of the application.
- [ ] **Dummy Files**: Creating dummy files does not work as expected in certain scenarios.
- [ ] **Log Categories**: Logging categories currently unavailable.

---

## [1.2.0] - 2025-05-10

### Added

- Added a "Browse" button to the rule edit window to easily change the destination path.
- Added a `.gitignore` file to exclude unnecessary files and folders from being pushed to the repository.
- Added a developer function to create dummy files in the base directory for testing purposes.
- Added logging toggles for different components (UI, File Operations, Rules, Settings) in the developer settings window.
- Added a theme submenu under `Settings -> Themes` with all available themes and visual indicators (colored dots).
- Added a loading bar window with progress updates during file organization.
- **Added automated tests** for core functionalities, including settings management and dummy file creation.

### Fixed

- Fixed `UnboundLocalError` in the theme menu by correctly passing `theme_id` to the lambda function.
- Fixed general logging issues.

### Changed

- Reworked the UI for consistent field and button positions, sizes, and colors.
- Updated binary toggles to visually use switches for a modern appearance.
- New settings menu, including themes and color options, under `Settings`.

### Known Bugs

- [ ] **Browse Button**: The "Browse" button is currently not available in some parts of the application.
- [ ] **Dummy Files**: Creating dummy files does not work as expected in certain scenarios.
- [ ] **Log Categories**: Logging categories currently unavailable.

---

## [1.1.0] - 2025-05-05

### Added

- Added the ability to enable or disable all rules with a single button.
- Added a delete button for individual rules and a "Delete Rules" button to delete multiple rules with confirmation.
- Added the ability to edit rule directories and patterns within the UI.

### Fixed

- Fixed issues with saving and loading settings, ensuring all settings are saved persistently.
- Fixed circular import issues by restructuring imports and moving functions to appropriate modules.

### Changed

- Improved logging functionality to include detailed logs for rule updates and file operations.

---

## [1.0.0] - 2025-05-01

### Added

- Initial release of TaskMover.
- Basic functionality to load, save, and manage rules for file organization.
- File organization based on rules with support for patterns and destination paths.
- Basic UI with options to add, edit, and delete rules.
- Logging functionality to track application events.
