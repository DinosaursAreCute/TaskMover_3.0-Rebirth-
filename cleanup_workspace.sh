#!/bin/bash
# TaskMover Workspace Cleanup Script
# This script removes legacy files and prepares for clean Phase 1 implementation

echo "🧹 Starting TaskMover workspace cleanup..."

# Files and directories to KEEP
KEEP_FILES=(
    ".git"
    ".gitignore" 
    "README.md"
    "docs/Architechture"
    "taskmover/core/logging"
    ".vscode"
)

# Files and directories to REMOVE
REMOVE_FILES=(
    "taskmover_redesign"
    "build"
    "dist"
    "dist_manual"
    ".pytest_cache"
    ".venv"
    "requirements.txt"
    "requirements-dev.txt"
    "settings.yml"
    "TaskMover.spec"
    "*.log"
    "*_SUMMARY.md"
    "*_COMPLETE.md"
    "IMPLEMENTATION*.md"
    "PHASE*.md"
    "PROPORTIONAL_WINDOWS.md"
    "DOCUMENTATION.md"
    "BUILD_SYSTEM_UPDATES.md"
    "WORKSPACE_ORGANIZATION.md"
    "run_*.bat"
    "generate_docs.bat"
    "test_*.py"
    "verify_startup.py"
    "tests"
)

# Create backup directory
mkdir -p .cleanup_backup/$(date +%Y%m%d_%H%M%S)
BACKUP_DIR=".cleanup_backup/$(date +%Y%m%d_%H%M%S)"

echo "📦 Creating backup in $BACKUP_DIR..."

# Backup files before removal
for item in "${REMOVE_FILES[@]}"; do
    if [ -e "$item" ]; then
        echo "  Backing up: $item"
        cp -r "$item" "$BACKUP_DIR/" 2>/dev/null || true
    fi
done

echo "🗑️  Removing legacy files..."

# Remove legacy files and directories
for item in "${REMOVE_FILES[@]}"; do
    if [ -e "$item" ]; then
        echo "  Removing: $item"
        rm -rf "$item"
    fi
done

# Remove any Python cache files
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true
find . -name "*.pyo" -delete 2>/dev/null || true

echo "✅ Workspace cleanup completed!"
echo "📦 Backup created in: $BACKUP_DIR"
echo "🚀 Ready for clean Phase 1 implementation"
