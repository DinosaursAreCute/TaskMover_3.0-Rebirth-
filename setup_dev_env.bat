@echo off
REM TaskMover Development Environment Setup Script
REM Sets up Poetry, dependencies, and development tools

echo 🚀 Setting up TaskMover development environment...

REM Check if Python 3.11+ is available
python --version 2>nul | findstr /r "Python 3\.1[1-9]" >nul
if %errorlevel% neq 0 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.11+ from https://python.org
    pause
    exit /b 1
)

REM Get Python version
for /f "tokens=2" %%v in ('python --version 2^>^&1') do set PYTHON_VERSION=%%v
echo ✅ Found Python %PYTHON_VERSION%

REM Check if Poetry is installed
echo 🔍 Checking Poetry installation...
poetry --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 📦 Installing Poetry...
    curl -sSL https://install.python-poetry.org | python -
    if %errorlevel% neq 0 (
        echo ❌ Failed to install Poetry
        echo Please install Poetry manually: https://python-poetry.org/docs/
        pause
        exit /b 1
    )
    echo ✅ Poetry installed successfully
) else (
    echo ✅ Poetry is already installed
)

REM Initialize Poetry project if pyproject.toml doesn't exist
if not exist "pyproject.toml" (
    echo 📝 Initializing Poetry project...
    poetry init --no-interaction --name "taskmover" --version "1.0.0" --description "Advanced File Organization and Automation Tool" --author "TaskMover Team" --python "^3.11"
    
    REM Add core dependencies
    echo 📦 Adding core dependencies...
    poetry add pyyaml colorama ttkbootstrap
    
    REM Add development dependencies
    echo 🔧 Adding development dependencies...
    poetry add --group dev pytest pytest-mock pytest-cov pytest-benchmark black mypy ruff pre-commit sphinx
    
    echo ✅ Poetry project initialized
) else (
    echo 📦 Installing dependencies from pyproject.toml...
    poetry install
)

REM Create virtual environment if it doesn't exist
echo 🏗️ Setting up virtual environment...
poetry env info >nul 2>&1
if %errorlevel% neq 0 (
    poetry install
)
echo ✅ Virtual environment ready

REM Setup pre-commit hooks
echo 🔧 Setting up pre-commit hooks...
poetry run pre-commit install
if %errorlevel% neq 0 (
    echo ⚠️  Pre-commit hooks setup failed (optional)
) else (
    echo ✅ Pre-commit hooks installed
)

REM Create basic project structure
echo 🏗️ Creating project structure...
call :create_directory "taskmover\core\di"
call :create_directory "taskmover\core\storage\backends"
call :create_directory "taskmover\core\storage\serializers"
call :create_directory "taskmover\core\storage\managers"
call :create_directory "taskmover\core\storage\schema"
call :create_directory "taskmover\core\settings"
call :create_directory "tests\unit"
call :create_directory "tests\integration"
call :create_directory "tests\fixtures"
call :create_directory "tests\performance"
call :create_directory "tests\manual"
call :create_directory "config"
call :create_directory "scripts"

REM Create basic configuration files
echo 📝 Creating configuration files...

REM Create pytest.ini
if not exist "pytest.ini" (
    echo [tool:pytest] > pytest.ini
    echo testpaths = tests >> pytest.ini
    echo python_files = test_*.py >> pytest.ini
    echo python_functions = test_* >> pytest.ini
    echo addopts = --cov=taskmover --cov-report=html --cov-report=term-missing --benchmark-skip >> pytest.ini
    echo markers = >> pytest.ini
    echo     unit: Unit tests >> pytest.ini
    echo     integration: Integration tests >> pytest.ini
    echo     performance: Performance tests >> pytest.ini
    echo     manual: Manual test cases >> pytest.ini
)

REM Create .gitignore
if not exist ".gitignore" (
    echo # Python > .gitignore
    echo __pycache__/ >> .gitignore
    echo *.py[cod] >> .gitignore
    echo *$py.class >> .gitignore
    echo. >> .gitignore
    echo # Virtual environments >> .gitignore
    echo .venv/ >> .gitignore
    echo venv/ >> .gitignore
    echo. >> .gitignore
    echo # IDE >> .gitignore
    echo .vscode/ >> .gitignore
    echo .idea/ >> .gitignore
    echo. >> .gitignore
    echo # Testing >> .gitignore
    echo .pytest_cache/ >> .gitignore
    echo htmlcov/ >> .gitignore
    echo .coverage >> .gitignore
    echo. >> .gitignore
    echo # Build >> .gitignore
    echo build/ >> .gitignore
    echo dist/ >> .gitignore
    echo *.egg-info/ >> .gitignore
    echo. >> .gitignore
    echo # Logs >> .gitignore
    echo logs/ >> .gitignore
    echo *.log >> .gitignore
    echo. >> .gitignore
    echo # OS >> .gitignore
    echo .DS_Store >> .gitignore
    echo Thumbs.db >> .gitignore
    echo. >> .gitignore
    echo # Backup >> .gitignore
    echo .cleanup_backup/ >> .gitignore
)

REM Create pre-commit config
if not exist ".pre-commit-config.yaml" (
    echo repos: > .pre-commit-config.yaml
    echo   - repo: https://github.com/psf/black >> .pre-commit-config.yaml
    echo     rev: 23.12.1 >> .pre-commit-config.yaml
    echo     hooks: >> .pre-commit-config.yaml
    echo       - id: black >> .pre-commit-config.yaml
    echo   - repo: https://github.com/charliermarsh/ruff-pre-commit >> .pre-commit-config.yaml
    echo     rev: v0.1.8 >> .pre-commit-config.yaml
    echo     hooks: >> .pre-commit-config.yaml
    echo       - id: ruff >> .pre-commit-config.yaml
    echo   - repo: https://github.com/pre-commit/mirrors-mypy >> .pre-commit-config.yaml
    echo     rev: v1.8.0 >> .pre-commit-config.yaml
    echo     hooks: >> .pre-commit-config.yaml
    echo       - id: mypy >> .pre-commit-config.yaml
)

echo ✅ Development environment setup completed!
echo.
echo 🎯 Next Steps:
echo   1. Run 'poetry shell' to activate the virtual environment
echo   2. Start implementing Phase 1 according to the roadmap
echo   3. Run 'poetry run pytest' to run tests
echo   4. Run 'poetry run black .' to format code
echo   5. Run 'poetry run mypy taskmover' for type checking
echo.
echo 📚 Documentation:
echo   - Architecture docs: docs/Architechture/
echo   - Development roadmap: docs/Architechture/DEVELOPMENT_ROADMAP.md
echo.
echo Happy coding! 🎉
pause
goto :eof

:create_directory
if not exist "%~1" (
    mkdir "%~1" 2>nul
    echo # Directory created by setup script > "%~1\__init__.py" 2>nul
)
goto :eof
