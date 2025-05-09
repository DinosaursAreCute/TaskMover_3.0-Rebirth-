# Changelog

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
