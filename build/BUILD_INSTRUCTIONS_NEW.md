# TaskMover Build Instructions (Updated v4.0)

## Project Structure Update

The project has been restructured:
- **OLD**: `taskmover_redesign/` directory
- **NEW**: `taskmover/` directory with proper package structure
- **UI Components**: Located in `taskmover/ui/` with comprehensive component system

## Prerequisites

1. **Python 3.11 or higher**
2. **PyInstaller** (automatically installed by build script)
3. **Project dependencies** (automatically installed from requirements-dev.txt)

## Build Methods

### Method 1: Automated Build Script (Recommended)

```bash
cd build
python build_exe.py
```

This method:
- Validates environment and dependencies
- Installs PyInstaller if needed
- Uses the updated spec file with proper module inclusion
- Provides detailed logging
- Cleans up artifacts appropriately

### Method 2: Simple Batch File

```bash
cd build
build.bat
```

### Method 3: Quick Batch Build

```bash
cd build
build_simple.bat
```

### Method 4: Manual PyInstaller

```bash
# From project root
pyinstaller TaskMover.spec
```

Or use the comprehensive v4 spec:

```bash
# From project root  
pyinstaller build/TaskMover_v4.spec
```

## Updated Spec File Features

The new `TaskMover_v4.spec` includes:

### Hidden Imports
- All TaskMover modules (`taskmover.*`)
- Complete UI component system
- Theme and layout managers
- All component categories (input, display, layout, navigation, etc.)
- Testing and demo frameworks

### Data Files
- Configuration files (`settings.yml`)
- UI documentation
- Requirements files for reference

### Optimizations
- Excludes development tools (pytest, black, etc.)
- Excludes large unused libraries
- Optimized for size and performance
- UPX compression enabled

## Build Outputs

Successful builds create:
- `dist/TaskMover.exe` - Main executable
- Build logs with timestamps
- Version information from `build/version_info.txt`

## Troubleshooting

### Missing Modules
If you get import errors, add missing modules to the `hiddenimports` list in the spec file.

### Size Issues
The executable includes the full UI framework. Typical size: 15-25 MB

### Console vs Windowed
- Set `console=True` in spec file for debugging
- Set `console=False` for production (default)

## GitHub Actions

The workflow file `.github/workflows/build-windows-exe.yml` automatically:
- Builds on Windows runners
- Uses Python 3.11
- Installs dependencies from requirements-dev.txt
- Uses the updated spec file
- Uploads artifacts for releases

## Version Management

Update version information in:
- `build/version_info.txt` - Executable version details
- `taskmover/__init__.py` - Package version
- GitHub releases for distribution

## File Structure

```
TaskMover/
├── taskmover/                 # Main application package
│   ├── __init__.py
│   ├── __main__.py           # Application entry point
│   ├── app.py                # Main application logic
│   └── ui/                   # UI components
│       ├── __init__.py
│       ├── base_component.py
│       ├── theme_manager.py
│       ├── layout_manager.py
│       ├── input_components.py
│       ├── display_components.py
│       ├── layout_components.py
│       ├── navigation_components.py
│       ├── data_display_components.py
│       ├── dialog_components.py
│       ├── pattern_management_components.py
│       ├── rule_management_components.py
│       ├── ruleset_management_components.py
│       ├── file_organization_components.py
│       ├── advanced_ui_features.py
│       ├── demo_gallery.py
│       ├── component_tester.py
│       ├── doc_generator.py
│       └── docs/              # Generated documentation
├── build/                     # Build configuration
│   ├── build_exe.py          # Main build script
│   ├── TaskMover_v4.spec     # Comprehensive spec file
│   ├── version_info.txt      # Version information
│   └── *.bat                 # Batch build scripts
├── .github/
│   ├── TaskMover.spec        # GitHub Actions spec
│   └── workflows/
│       └── build-windows-exe.yml
├── TaskMover.spec            # Root spec file
├── settings.yml              # Application settings
├── requirements.txt          # Runtime dependencies
└── requirements-dev.txt      # Development dependencies
```

## Testing the Build

After building, test the executable:

1. **Basic Launch Test**:
   ```bash
   cd dist
   TaskMover.exe
   ```

2. **UI Component Test**:
   - Launch the application
   - Test basic functionality
   - Verify theme switching works
   - Check component gallery if available

3. **Console Test** (for debugging):
   - Set `console=True` in spec file
   - Rebuild and check console output

## Deployment

For distribution:
1. Test the executable on a clean Windows machine
2. Include any necessary redistributables
3. Consider creating an installer (NSIS, Inno Setup, etc.)
4. Document system requirements

## Development Notes

- The build system now includes comprehensive UI testing
- All component imports are explicitly included
- Documentation is bundled with the executable
- Build artifacts are optimized for size and performance
