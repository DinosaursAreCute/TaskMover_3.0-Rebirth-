@echo off
echo Generating UI Documentation...
cd /d "%~dp0"
python -m taskmover.ui.doc_generator
pause
