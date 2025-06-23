@echo off
setlocal enabledelayedexpansion

echo TaskMover Build Script
echo ---------------------
echo [%date% %time%] Build started

rem Verify we're in the right directory
if not exist "..\taskmover" (
    echo ERROR: Please run this script from the 'build' directory
    echo ERROR: TaskMover main directory not found
    goto :error
)
    exit /b 1
)

rem Check for Python
where python >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ERROR: Python not found. Please install Python 3.11 or newer.
    exit /b 1
)

rem Check Python version
python -c "import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)" >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ERROR: Python 3.11 or newer is required.
    python --version
    exit /b 1
)

rem Check for PyInstaller
where pyinstaller >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo PyInstaller not found. Installing...
    python -m pip install pyinstaller
    if %ERRORLEVEL% neq 0 (
        echo ERROR: Failed to install PyInstaller
        exit /b 1
    )
)

echo Checking dependencies...
python -m pip install -r ..\requirements-dev.txt
if %ERRORLEVEL% neq 0 (
    echo ERROR: Failed to install dependencies
    exit /b 1
)

rem Check if spec file exists
if not exist "..\.github\TaskMover.spec" (
    echo ERROR: Spec file not found at ..\.github\TaskMover.spec
    exit /b 1
)

echo Building TaskMover...
pyinstaller ..\.github\TaskMover.spec
if %ERRORLEVEL% neq 0 (
    echo ERROR: Build failed
    exit /b 1
)

rem Verify the build succeeded
if not exist "..\dist\TaskMover.exe" (
    echo ERROR: Build failed - executable not found in dist directory
    exit /b 1
)

echo Build completed successfully!
echo The executable can be found in the dist directory.
echo [%date% %time%] Build finished

pause
