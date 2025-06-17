# TaskMover v3.0.0 - Build Instructions

**Author:** Dino corp  
**Application:** TaskMover  
**Version:** 3.0.0  
**Description:** Automated File Organization Tool

## Overview

This guide explains how to build a standalone executable for TaskMover v3.0.0 using PyInstaller. The resulting .exe file can be distributed to users without requiring Python to be installed.

## Prerequisites

### Required Software
- **Python 3.11+** (recommended: Python 3.12)
- **pip** (Python package installer)
- **PyInstaller** (will be installed automatically)

### System Requirements
- **Windows 10+** (for building Windows executables)
- **4GB RAM minimum** (8GB recommended for faster builds)
- **1GB free disk space** for build artifacts

## Quick Build (Automated)

### Option 1: Using Batch Script (Recommended for Windows)
```batch
# Navigate to the TaskMover project directory
cd TaskMover

# Run the automated build script
build\build.bat
```

### Option 2: Using Python Script
```bash
# Navigate to the TaskMover project directory
cd TaskMover

# Run the build script directly
python build/build_exe.py
```

## Manual Build Process

### Step 1: Install Dependencies
```bash
# Install PyInstaller if not already installed
pip install pyinstaller

# Install project dependencies
pip install -r requirements.txt
```

### Step 2: Clean Previous Builds
```bash
# Remove previous build artifacts (optional)
rmdir /s dist
rmdir /s build\__pycache__
```

### Step 3: Build Executable
```bash
# Use the PyInstaller spec file
pyinstaller build/TaskMover_v3.spec
```

## Build Configuration

### Version Information
- **Version:** Automatically read from `taskmover_redesign/__init__.py`
- **Author:** Dino corp
- **Company:** Dino corp
- **Product Name:** TaskMover
- **Description:** TaskMover - Automated File Organization Tool

### File Details
- **Executable Name:** TaskMover.exe
- **Icon:** Uses default Windows application icon
- **Console Window:** Hidden (GUI-only application)
- **Single File:** Yes (all dependencies bundled)

### Dependencies Included
- Python 3.11+ runtime
- ttkbootstrap (Modern UI library)
- tkinter (GUI framework)
- PyYAML (Configuration files)
- colorlog (Enhanced logging)
- All TaskMover redesigned modules

## Output

### Build Results
After successful build, you'll find:
```
TaskMover/
├── dist/
│   └── TaskMover.exe          # ← Main executable (distribute this)
├── build/                     # Build artifacts (can be deleted)
└── TaskMover_v3.spec         # PyInstaller configuration
```

### Executable Details
- **Size:** Approximately 25-35 MB
- **Type:** Windows Portable Executable (.exe)
- **Dependencies:** None (self-contained)
- **Installation:** Not required (portable application)

## Testing the Executable

### Basic Functionality Test
```bash
# Test the executable
dist\TaskMover.exe

# The application should:
# 1. Launch the GUI interface
# 2. Load without errors
# 3. Display the main TaskMover window
# 4. Allow normal operation
```

### Distribution Testing
1. **Copy** `TaskMover.exe` to a clean Windows machine
2. **Run** the executable without Python installed
3. **Verify** all features work correctly
4. **Test** file organization functionality

## Troubleshooting

### Common Build Issues

#### 1. PyInstaller Not Found
```bash
# Solution: Install PyInstaller
pip install pyinstaller
```

#### 2. Module Import Errors
```bash
# Solution: Install all dependencies
pip install -r requirements.txt

# Or install specific missing modules
pip install ttkbootstrap PyYAML colorlog
```

#### 3. Build Fails with Permission Errors
```bash
# Solution: Run as administrator or check file permissions
# Close any running TaskMover instances
# Ensure antivirus is not blocking the build
```

#### 4. Large Executable Size
The executable includes the entire Python runtime and dependencies. This is normal for PyInstaller builds. Typical size is 25-35 MB.

#### 5. Slow Startup
First launch may be slower as Windows extracts temporary files. Subsequent launches will be faster.

### Getting Help

#### Build Issues
1. Check the build log for specific error messages
2. Ensure all dependencies are installed
3. Try building on a clean Python environment
4. Check GitHub Issues for similar problems

#### Runtime Issues
1. Test on the development machine first
2. Check Windows Event Viewer for error details
3. Run from command prompt to see console output:
   ```bash
   # Build with console visible for debugging
   pyinstaller --console build/TaskMover_v3.spec
   ```

## Advanced Configuration

### Custom Build Options

#### Include Additional Files
Edit `build/TaskMover_v3.spec` and add files to the `datas` section:
```python
datas=[
    ('path/to/file', 'destination/in/exe'),
    ('data/folder', 'data'),
],
```

#### Add Icon
```python
exe = EXE(
    # ... other options ...
    icon='path/to/icon.ico',
)
```

#### Optimize for Size
```python
# Add to Analysis()
excludes=[
    'matplotlib',
    'numpy', 
    'scipy',
    # Other unused modules
],
```

### Build Script Customization

The `build_exe.py` script can be modified to:
- Change output directories
- Add custom validation steps
- Include additional files
- Modify build parameters

## Distribution

### Single File Distribution
- **File:** `dist/TaskMover.exe`
- **Size:** ~25-35 MB
- **Requirements:** Windows 10+ (64-bit)
- **Installation:** None required (portable)

### Professional Distribution
For professional distribution, consider:
1. **Code Signing:** Sign the executable with a certificate
2. **Installer Creation:** Use NSIS or similar to create an installer
3. **Documentation:** Include user manual and license files
4. **Testing:** Test on multiple Windows versions

### Security Considerations
- The executable may trigger antivirus warnings (false positive)
- Code signing reduces security warnings
- Distribute through trusted channels only

---

## Build Information

**Last Updated:** June 17, 2025  
**Build Script Version:** 3.0.0  
**Author:** Dino corp  
**Python Version Required:** 3.11+  
**Target Platform:** Windows 10+ (64-bit)

For questions or issues, please check the project documentation or create an issue on GitHub.
