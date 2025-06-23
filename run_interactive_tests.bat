@echo off
echo Starting Interactive UI Tests...
cd /d "%~dp0"
python -m taskmover.ui.component_tester --mode interact
pause
