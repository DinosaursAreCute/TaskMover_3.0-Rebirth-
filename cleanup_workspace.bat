@echo off
REM TaskMover Workspace Cleanup Script for Windows
REM This script removes legacy files and prepares for clean Phase 1 implementation

echo 🧹 Starting TaskMover workspace cleanup...

REM Create backup directory
set BACKUP_DIR=.cleanup_backup\%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set BACKUP_DIR=%BACKUP_DIR: =0%
mkdir "%BACKUP_DIR%" 2>nul

echo 📦 Creating backup in %BACKUP_DIR%...

REM Backup and remove legacy directories
if exist "taskmover_redesign" (
    echo   Backing up: taskmover_redesign
    xcopy "taskmover_redesign" "%BACKUP_DIR%\taskmover_redesign\" /E /I /Q >nul 2>&1
    echo   Removing: taskmover_redesign
    rmdir /S /Q "taskmover_redesign" 2>nul
)

if exist "build" (
    echo   Backing up: build
    xcopy "build" "%BACKUP_DIR%\build\" /E /I /Q >nul 2>&1
    echo   Removing: build
    rmdir /S /Q "build" 2>nul
)

if exist "dist" (
    echo   Backing up: dist
    xcopy "dist" "%BACKUP_DIR%\dist\" /E /I /Q >nul 2>&1
    echo   Removing: dist
    rmdir /S /Q "dist" 2>nul
)

if exist "dist_manual" (
    echo   Backing up: dist_manual
    xcopy "dist_manual" "%BACKUP_DIR%\dist_manual\" /E /I /Q >nul 2>&1
    echo   Removing: dist_manual
    rmdir /S /Q "dist_manual" 2>nul
)

if exist "tests" (
    echo   Backing up: tests
    xcopy "tests" "%BACKUP_DIR%\tests\" /E /I /Q >nul 2>&1
    echo   Removing: tests
    rmdir /S /Q "tests" 2>nul
)

if exist ".pytest_cache" (
    echo   Removing: .pytest_cache
    rmdir /S /Q ".pytest_cache" 2>nul
)

if exist ".venv" (
    echo   Removing: .venv
    rmdir /S /Q ".venv" 2>nul
)

REM Backup and remove legacy files
for %%f in (requirements.txt requirements-dev.txt settings.yml TaskMover.spec) do (
    if exist "%%f" (
        echo   Backing up: %%f
        copy "%%f" "%BACKUP_DIR%\" >nul 2>&1
        echo   Removing: %%f
        del "%%f" 2>nul
    )
)

REM Remove log files
echo   Removing: *.log files
del *.log 2>nul

REM Remove summary and status files
for %%f in (*_SUMMARY.md *_COMPLETE.md IMPLEMENTATION*.md PHASE*.md) do (
    if exist "%%f" (
        echo   Backing up: %%f
        copy "%%f" "%BACKUP_DIR%\" >nul 2>&1
        echo   Removing: %%f
        del "%%f" 2>nul
    )
)

REM Remove other legacy files
for %%f in (PROPORTIONAL_WINDOWS.md DOCUMENTATION.md BUILD_SYSTEM_UPDATES.md WORKSPACE_ORGANIZATION.md) do (
    if exist "%%f" (
        echo   Backing up: %%f
        copy "%%f" "%BACKUP_DIR%\" >nul 2>&1
        echo   Removing: %%f
        del "%%f" 2>nul
    )
)

REM Remove batch files
for %%f in (run_*.bat generate_docs.bat) do (
    if exist "%%f" (
        echo   Backing up: %%f
        copy "%%f" "%BACKUP_DIR%\" >nul 2>&1
        echo   Removing: %%f
        del "%%f" 2>nul
    )
)

REM Remove test files
for %%f in (test_*.py verify_startup.py) do (
    if exist "%%f" (
        echo   Backing up: %%f
        copy "%%f" "%BACKUP_DIR%\" >nul 2>&1
        echo   Removing: %%f
        del "%%f" 2>nul
    )
)

REM Remove Python cache files
echo   Removing: Python cache files
for /d /r . %%d in (__pycache__) do @if exist "%%d" rmdir /s /q "%%d" 2>nul
del /s /q *.pyc 2>nul
del /s /q *.pyo 2>nul

echo ✅ Workspace cleanup completed!
echo 📦 Backup created in: %BACKUP_DIR%
echo 🚀 Ready for clean Phase 1 implementation
pause
