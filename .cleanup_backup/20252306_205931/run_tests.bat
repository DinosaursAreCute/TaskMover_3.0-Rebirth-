@echo off
echo Running TaskMover UI Component Tests...
cd /d "%~dp0"
python -m taskmover.ui.component_tester --mode test
pause
