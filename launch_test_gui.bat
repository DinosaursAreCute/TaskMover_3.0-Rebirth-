@echo off
echo TaskMover Test Runner Launcher
echo ==============================
echo.
echo Select Test Runner:
echo 1. Modern Test Runner (Recommended)
echo 2. Simple Test Runner  
echo 3. Exit
echo.

:choice
set /p choice="Enter your choice (1-3): "

if "%choice%"=="1" goto modern
if "%choice%"=="2" goto simple  
if "%choice%"=="3" goto exit
echo Invalid choice. Please try again.
goto choice

:modern
echo.
echo Starting Modern Test Runner...
cd /d "%~dp0"
python tests\modern_test_gui.py
goto end

:simple
echo.
echo Starting Simple Test Runner...
cd /d "%~dp0" 
python tests\simple_test_gui.py
goto end

:exit
echo Goodbye!
goto end

:end
if %ERRORLEVEL% neq 0 (
    echo.
    echo Error: Failed to start test runner
    pause
)
