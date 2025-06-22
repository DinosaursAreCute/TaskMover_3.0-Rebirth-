# Changelog
## [3.0.1] - 2025-06-17
### Fixed
- Fixed an issue where windows would open in the wrong position on some systems.
- Fixed and issue where windows would not open in the correct size on some systems.
## [3.0.0] - 2025-06-16

### 🚀 MAJOR RELEASE: Complete Application Redesign

This is a **major breaking release** with a complete rewrite of TaskMover. The application has been fully redesigned from the ground up with modern architecture, improved maintainability, and enhanced user experience.

#### ✨ New Architecture
- **New Package**: Introduced `taskmover_redesign` package with clean, modular architecture
- **Core Separation**: Clear separation between business logic (`core/`) and UI (`ui/`)
- **Type Safety**: 100% type annotations throughout the codebase
- **Modern Python**: Updated to use latest Python best practices and patterns

#### 🏗️ Package Structure
```
taskmover_redesign/
├── core/                    # Business logic
│   ├── config.py           # Configuration management
│   ├── rules.py            # Rule operations
│   ├── file_operations.py  # File organization
│   └── utils.py            # Utilities
├── ui/                     # User interface
│   ├── components.py       # Reusable UI components
│   ├── rule_components.py  # Rule management UI
│   └── settings_components.py # Settings dialog
├── tests/                  # Comprehensive test suite
└── app.py                  # Main application
```

#### 🎯 Key Improvements
- **Clean Architecture**: Modular design with single responsibility principle
- **Modern UI**: Built with ttkbootstrap for professional appearance
- **Comprehensive Testing**: Full test suite with import, integration, and verification tests
- **Better Error Handling**: Robust error management throughout
- **Extensible Design**: Easy to add new features and modify existing ones
- **Zero Legacy Code**: No backwards compatibility shims or deprecated patterns

#### 📦 Migration & Organization
- **Legacy Archive**: All legacy code moved to `legacy/` folder for reference
- **Organized Structure**: Clear project organization with dedicated folders
- **Updated Documentation**: Complete rewrite of README and documentation
- **Test Integration**: All tests moved into the redesigned package

#### 🧪 Testing & Quality
- **Import Tests**: Verify all modules load correctly
- **Integration Tests**: Test core functionality works together
- **Final Verification**: End-to-end application testing
- **Code Quality**: 100% type coverage and modern Python patterns

#### 🔄 Breaking Changes
- **New Entry Point**: Use `python -m taskmover_redesign` instead of `python -m taskmover`
- **Configuration Format**: New configuration system (migration tools available)
- **API Changes**: Completely new internal APIs (external usage patterns remain similar)
- **File Locations**: New file organization (legacy files preserved in `legacy/`)

#### 🎉 For Users
- **Same Functionality**: All existing features preserved and enhanced
- **Better Performance**: Optimized code with improved responsiveness
- **Modern Interface**: Professional UI with consistent theming
- **Reliable Operation**: Comprehensive testing ensures stability

#### 🎯 For Developers
- **Clean Codebase**: Modern, maintainable code following best practices
- **Type Safety**: Full IntelliSense support and compile-time error detection
- **Modular Design**: Easy to understand, modify, and extend
- **Comprehensive Tests**: Reliable test suite for confident development

### Migration Guide
1. **Backup**: Your existing rules and settings are preserved
2. **Update Command**: Use `python -m taskmover_redesign` to run the new version
3. **Configuration**: Settings will be migrated automatically on first run
4. **Legacy Access**: Old version remains available in `legacy/` folder if needed

---

## [2.2.0] - 2025-06-13

### Major UI/UX Improvements

- Scrollable main window with smooth scrolling for all rule content (except log area).
- Inline pattern editing with dynamic add fields and a plus (+) button for adding multiple patterns at once.
- Only the last add pattern field shows a plus button; focus moves to new field automatically.
- Change destination path by clicking the destination field.
- UI now uses a single, unified scrollbar for the main content area.
- Mousewheel scrolling is only enabled when hovering over the main content area.


### Changed

- Removed redundant scrollbars and canvas logic from both app.py and ui_rule_helpers.py.
- Improved pattern editing workflow and usability.

### Fixed

- Fixed geometry manager conflicts and duplicate function declarations in pattern editing logic.
- Fixed issues with pattern field focus and placeholder handling.
- Fixed issue where widgets would not use the full width

---

## [2.1.0] - 2025-05-17

### Major UI/UX and Theme System Changes

- Modularized UI logic into helper modules (e.g., ui_menu_helpers.py, ui_rule_helpers.py, etc.) for maintainability and clarity.
- Removed the Theme Manager and all custom theme/color management features.
- Removed the Colors tab; all theme management is now handled by a built-in theme.
- Fixed all major theme application errors (e.g., no more attempts to style unsupported widgets like Menubar, Listbox, or Text
  via ttkbootstrap).
- Suppressed info popups for theme save/apply actions for a smoother workflow.
- Cleaned up all __pycache__ folders and checked for other unnecessary files.
- Added type hints and docstrings to all major functions in ui_settings_helpers.py and other helpers.
- Updated and clarified documentation for theme management and UI structure.

### Bug Fixes

- Prevented crashes related to unsupported style keys (e.g., Menubar, Listbox, Text).
- Fixed all crashes related to theme application and widget styling.
- Fixed logic to prevent built-in theme modification.
- Fixed all references to removed Colors tab and legacy color logic.
- Fixed all previously known UI bugs, including:
  - Developer Settings "Save" and "Cancel" button positioning.
  - Browse button availability in all relevant windows.
  - Dummy file creation in all scenarios.

### Developer/Codebase

- Broke circular imports and standardized function signatures across UI modules.
- Used PowerShell Remove-Item to clean up bytecode and __pycache__ folders.
- Improved code documentation and maintainability.
- All automated tests now pass reliably, including UI and non-UI tests.
- UI tests are automatically skipped in headless environments (e.g., CI servers).
- Improved YAML config and theme file handling, with robust auto-fix and user prompt logic.
- Documentation and developer comments updated for clarity and maintainability.

### Improvements & Fixes

- Resolved all test failures related to Tkinter/ttkbootstrap context and style usage in automated UI tests.
- Improved test automation: all UI and non-UI tests now pass reliably, including in headless/CI environments (UI tests are skipped if no display is available).
- Enhanced robustness of YAML config and theme file handling, including auto-fix and user prompt logic for broken or missing files.
- Cleaned up and modularized UI helper code for maintainability.
- Improved documentation and developer comments throughout the codebase.
- Updated requirements and documentation for new test and runtime dependencies.

### Known Bugs

- None as of this release.

---

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
