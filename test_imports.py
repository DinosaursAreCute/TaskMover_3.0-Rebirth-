#!/usr/bin/env python3
"""
Quick test script to verify TaskMover imports
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

print("=== TaskMover Import Test ===")
print(f"Python version: {sys.version}")
print(f"Project root: {project_root}")
print()

# Test 1: Basic package import
try:
    import taskmover
    print("✅ TaskMover package imports successfully")
except Exception as e:
    print(f"❌ TaskMover import failed: {e}")

# Test 2: Core exceptions
try:
    from taskmover.core.exceptions import TaskMoverException
    print("✅ Core exceptions available")
except Exception as e:
    print(f"❌ Core exceptions import failed: {e}")

# Test 3: Theme manager
try:
    from taskmover.ui.theme_manager import get_theme_manager
    theme_manager = get_theme_manager()
    print("✅ Theme manager available")
except Exception as e:
    print(f"❌ Theme manager import failed: {e}")

# Test 4: Main application
try:
    from taskmover.ui.main_application import TaskMoverApplication
    print("✅ Main application can be imported")
except Exception as e:
    print(f"❌ Main application import failed: {e}")

print("\n=== Test completed ===")
