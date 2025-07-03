@echo off
REM TaskMover Test Launcher
REM =======================

echo TaskMover Test Suite Launcher
echo ==============================

:menu
echo.
echo Select test option:
echo 1. Run all tests (console)
echo 2. Launch GUI test runner (with dark mode)
echo 3. Run unit tests only
echo 4. Run integration tests only
echo 5. Run UI tests only
echo 6. Generate test report
echo 7. Quick import test
echo 8. Exit
echo.

set /p choice="Enter choice (1-8): "

if "%choice%"=="1" goto run_all
if "%choice%"=="2" goto run_gui
if "%choice%"=="3" goto run_unit
if "%choice%"=="4" goto run_integration
if "%choice%"=="5" goto run_ui
if "%choice%"=="6" goto generate_report
if "%choice%"=="7" goto quick_test
if "%choice%"=="8" goto exit
goto invalid

:run_all
echo Running all tests...
python run_tests.py --verbose
goto end

:run_gui
echo Launching GUI test runner with dark mode support...
python run_tests.py --gui
goto end

:run_unit
echo Running unit tests...
python run_tests.py --suite unit_tests --verbose
goto end

:run_integration
echo Running integration tests...
python run_tests.py --suite integration_tests --verbose
goto end

:run_ui
echo Running UI tests...
python run_tests.py --suite ui_tests --verbose
goto end

:generate_report
echo Generating test report...
python run_tests.py --report test_report.txt
goto end

:quick_test
echo Running quick import test...
python -c "
try:
    import taskmover
    print('✓ TaskMover package imports successfully')
    
    from taskmover.ui.theme_manager import get_theme_manager
    theme_manager = get_theme_manager()
    print('✓ Theme manager available')
    
    from taskmover.ui.main_application import TaskMoverApplication
    print('✓ Main application can be imported')
    
    print('\n✅ Quick test passed! Core components are working.')
except Exception as e:
    print(f'❌ Quick test failed: {e}')
    import traceback
    traceback.print_exc()
"
goto end

:invalid
echo Invalid choice. Please select 1-8.
goto menu

:end
echo.
pause
goto menu

:exit
echo Goodbye!
