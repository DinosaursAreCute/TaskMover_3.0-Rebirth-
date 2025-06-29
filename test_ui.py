#!/usr/bin/env python3
"""
TaskMover Application Test Runner
================================

Simple test runner to verify the UI implementation works correctly.
"""

import sys
import os
import traceback

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_imports():
    """Test that all UI modules can be imported."""
    try:
        print("Testing imports...")
        
        # Test core imports
        from taskmover.core.exceptions import TaskMoverError, PatternError, RuleError
        print("✓ Core exceptions imported")
        
        # Test UI imports
        from taskmover.ui.base_component import BaseComponent, ModernButton
        print("✓ Base components imported")
        
        from taskmover.ui.theme_manager import get_theme_manager
        print("✓ Theme manager imported")
        
        from taskmover.ui.navigation_components import ModernSidebar, ModernToolbar
        print("✓ Navigation components imported")
        
        from taskmover.ui.input_components import SmartPatternInput, ModernEntry
        print("✓ Input components imported")
        
        from taskmover.ui.pattern_management_components import PatternLibrary
        print("✓ Pattern management components imported")
        
        from taskmover.ui.rule_management_components import RuleManagementView
        print("✓ Rule management components imported")
        
        from taskmover.ui.execution_components import ExecutionView
        print("✓ Execution components imported")
        
        from taskmover.ui.history_components import HistoryAndStatsView
        print("✓ History components imported")
        
        from taskmover.ui.dialog_components import ConfirmationDialog, ProgressDialog
        print("✓ Dialog components imported")
        
        from taskmover.ui.main_application import TaskMoverApplication
        print("✓ Main application imported")
        
        return True
        
    except Exception as e:
        print(f"✗ Import failed: {e}")
        traceback.print_exc()
        return False

def test_application_creation():
    """Test that the application can be created."""
    try:
        print("\nTesting application creation...")
        
        from taskmover.ui.main_application import TaskMoverApplication
        app = TaskMoverApplication()
        print("✓ Application created successfully")
        
        # Test theme manager
        from taskmover.ui.theme_manager import get_theme_manager
        theme_manager = get_theme_manager()
        tokens = theme_manager.get_current_tokens()
        print(f"✓ Theme manager working, current mode: {theme_manager.current_mode.value}")
        
        return True
        
    except Exception as e:
        print(f"✗ Application creation failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("TaskMover UI Implementation Test")
    print("=" * 40)
    
    success = True
    
    # Test imports
    if not test_imports():
        success = False
    
    # Test application creation
    if not test_application_creation():
        success = False
    
    print("\n" + "=" * 40)
    if success:
        print("✓ All tests passed! The UI implementation is working correctly.")
        print("\nTo run the application, use:")
        print("  python -m taskmover")
    else:
        print("✗ Some tests failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
