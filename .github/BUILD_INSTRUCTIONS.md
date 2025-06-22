# TaskMover Build Instructions

This document provides instructions for building the TaskMover application from source code.

## Prerequisites

### Required Software

- Python 3.11 or newer
- pip (Python package manager)
- Git (for version control)

### Development Environment Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/[username]/TaskMover.git
   cd TaskMover
   ```

2. Create a virtual environment (recommended):

   ```bash
   python -m venv venv
   ```

3. Activate the virtual environment:
   - On Windows:

     ```cmd
     venv\Scripts\activate
     ```
   
   - On macOS/Linux:

     ```bash
     source venv/bin/activate
     ```

4. Install development dependencies:

   ```bash
   pip install -r requirements-dev.txt
   ```

## Running the Application in Development Mode

You can run the application directly using Python:

```bash
python -m taskmover_redesign
```

Alternatively, if you're using Visual Studio Code, you can use the predefined task:

- Open the Command Palette (Ctrl+Shift+P)
- Type "Tasks: Run Task"
- Select "Run TaskMover Application"

## Building the Executable

### Option 1: Using PyInstaller Directly

1. Make sure you've installed all dependencies:

   ```bash
   pip install -r requirements-dev.txt
   ```

2. Run PyInstaller with the spec file:

   ```bash
   pyinstaller .github\TaskMover.spec
   ```

3. The executable will be generated in the `dist` directory.

### Option 2: Using GitHub Actions (Automated Build)

The project includes GitHub Actions workflows that automatically build the executable when:

- Code is pushed to the main branch
- A pull request is submitted
- A release is published

To trigger a build manually:

1. Go to the GitHub repository page
2. Click on the "Actions" tab
3. Select the "Build Windows EXE" workflow
4. Click "Run workflow"

### Option 3: Using the Simplified Build Script

For a quick build on Windows:

```cmd
cd build
build_simple.bat
```

This will automatically run PyInstaller with the correct settings and place the executable in the `dist` folder.

## Build Configuration

The build process is configured using the following files:

- `.github\TaskMover.spec`: The PyInstaller specification file that defines how the executable is built
- `build\version_info.txt`: Contains version information that is embedded in the Windows executable
- `build\build_exe.py`: Advanced Python build script with validation and error handling
- `build\build_simple.bat`: Simplified Windows batch build script
- `requirements-dev.txt`: Lists all dependencies needed for development and building

## Customizing the Build

### Changing Version Information

Edit `build\version_info.txt` to update the version information that appears in the Windows executable file properties.

### Adjusting Build Parameters

If you need to customize the build process, you can modify the `.github\TaskMover.spec` file. 
Common customizations include:

- Adding additional data files
- Including or excluding specific modules
- Changing the executable icon
- Modifying console visibility settings

## Distribution

After building, the standalone executable (`TaskMover.exe`) can be found in the `dist` directory. 
This file can be distributed to users and does not require Python or any other dependencies to be installed.

## Troubleshooting

### Missing Dependencies

If you encounter errors related to missing modules during the build process, ensure that all requirements are installed:

```bash
pip install -r requirements-dev.txt
```

### Version File Issues

If the build fails with errors related to the version file, ensure that `build\version_info.txt` exists and is properly formatted according to PyInstaller's requirements.

### Import Errors in the Built Application

If the built application has import errors, they may be caused by hidden imports that PyInstaller didn't detect automatically. Add them to the `hiddenimports` list in the spec file.
