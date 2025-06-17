# TaskMover Redesigned - Build Instructions

## Creating an Executable (.exe) for TaskMover v3.0.0

This guide will help you create a standalone executable file for the redesigned TaskMover application using PyInstaller.

## Prerequisites

### 1. Install PyInstaller
```bash
pip install pyinstaller
```

### 2. Install All Dependencies
Make sure all required packages are installed:
```bash
pip install -r requirements.txt
```

### 3. Verify Application Works
Test that the application runs correctly before building:
```bash
python -m taskmover_redesign
```

## Building the Executable

### Method 1: Quick Build (Simple)
```bash
# Navigate to the project root
cd TaskMover

# Create executable with PyInstaller
pyinstaller --onefile --windowed --name "TaskMover" taskmover_redesign/__main__.py
```

### Method 2: Advanced Build (Recommended)
Use the provided PyInstaller spec file for better control:

```bash
# Navigate to the project root
cd TaskMover

# Build using the spec file
pyinstaller build/TaskMover_v3.spec
```

### Method 3: Custom Build Script
Use the automated build script:

```bash
# Navigate to the project root  
cd TaskMover

# Run the build script
python build/build_exe.py
```

## Build Options Explained

### Basic PyInstaller Options
- `--onefile`: Creates a single executable file
- `--windowed`: Hides the console window (for GUI apps)
- `--name "TaskMover"`: Sets the executable name
- `--icon`: Adds an icon to the executable
- `--add-data`: Includes additional files

### Advanced Options (in spec file)
- `console=False`: GUI application (no console window)
- `upx=True`: Compress executable with UPX
- `version`: Include version information
- `hiddenimports`: Force include specific modules

## Output Location

After building, the executable will be located in:
- **Simple build**: `dist/TaskMover.exe`
- **Spec file build**: `dist/TaskMover/TaskMover.exe` or `dist/TaskMover.exe`

## File Size Optimization

### Reduce Executable Size
1. **Exclude unnecessary modules**:
   ```bash
   pyinstaller --exclude-module tkinter.test taskmover_redesign/__main__.py
   ```

2. **Use UPX compression**:
   ```bash
   pyinstaller --upx-dir /path/to/upx taskmover_redesign/__main__.py
   ```

3. **Strip debugging symbols**:
   ```bash
   pyinstaller --strip taskmover_redesign/__main__.py
   ```

## Testing the Executable

### 1. Basic Functionality Test
```bash
# Run the executable
./dist/TaskMover.exe

# Test with command line
./dist/TaskMover.exe --help
```

### 2. Full Integration Test
- Launch the GUI application
- Create a test rule
- Organize test files
- Verify all features work

### 3. System Compatibility Test
- Test on different Windows versions
- Test with different Python versions
- Test on systems without Python installed

## Troubleshooting

### Common Issues

#### 1. **ModuleNotFoundError**
```
Solution: Add missing modules to hiddenimports in the spec file
```

#### 2. **Large File Size**
```
Solution: Use --exclude-module for unnecessary packages
Expected size: 50-100MB for TaskMover
```

#### 3. **Slow Startup**
```
Solution: Use --onefile for single executable or optimize imports
```

#### 4. **Missing GUI Themes**
```
Solution: Include ttkbootstrap themes in the build
```

### Debug Mode
Build with debug mode to see detailed error messages:
```bash
pyinstaller --debug=all taskmover_redesign/__main__.py
```

## Distribution

### 1. Single File Distribution
- Pros: Easy to distribute, no dependencies
- Cons: Larger file size, slower startup
- Use: `--onefile` option

### 2. Directory Distribution  
- Pros: Faster startup, smaller individual files
- Cons: Multiple files to distribute
- Use: Default PyInstaller behavior

### 3. Installer Creation
Consider creating an installer using:
- **NSIS** (Nullsoft Scriptable Install System)
- **Inno Setup**
- **WiX Toolset**

## Version Information

The executable includes version information:
- **Version**: 3.0.0 (Architecture Redesign)
- **Company**: TaskMover Team
- **Description**: Modern File Organization Tool
- **Copyright**: 2025 TaskMover Project

## Build Automation

For automated builds, see:
- `build/build_exe.py` - Python build script
- `build/TaskMover_v3.spec` - PyInstaller configuration
- `build/version_info.txt` - Version information file

## Performance Notes

### Expected Performance
- **Startup Time**: 2-5 seconds (first run), 1-2 seconds (subsequent)
- **Memory Usage**: 50-100MB baseline
- **File Size**: 50-100MB executable
- **Compatibility**: Windows 10+ (primary), Windows 7+ (limited)

### Optimization Tips
1. **Minimize imports** in the main module
2. **Use lazy loading** for heavy dependencies
3. **Exclude test modules** from the build
4. **Compress with UPX** if available

---

## Quick Start Commands

```bash
# 1. Install PyInstaller
pip install pyinstaller

# 2. Simple build
pyinstaller --onefile --windowed --name "TaskMover" taskmover_redesign/__main__.py

# 3. Run the executable
./dist/TaskMover.exe
```

**Result**: You'll have a standalone `TaskMover.exe` that can run on any Windows system without requiring Python to be installed!

---

*Build instructions for TaskMover v3.0.0 - June 17, 2025*
