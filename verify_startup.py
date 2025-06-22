#!/usr/bin/env python3
"""
TaskMover Startup Verification Script
This script verifies that TaskMover can start normally and all components are working.
"""

import sys
import os

def test_imports():
    """Test all critical imports"""
    print("🔍 Testing imports...")
    
    try:
        # Test core imports
        from taskmover_redesign.app import TaskMoverApp
        from taskmover_redesign.core import PatternLibrary, RulesetManager
        from taskmover_redesign.ui.pattern_tab import PatternManagementTab
        from taskmover_redesign.ui.rule_components import add_rule_button, edit_rule
        from taskmover_redesign.ui.components import Tooltip
        print("   ✅ All imports successful")
        return True
    except Exception as e:
        print(f"   ❌ Import failed: {e}")
        return False

def test_app_creation():
    """Test app instantiation"""
    print("🔍 Testing app creation...")
    
    try:
        from taskmover_redesign.app import TaskMoverApp
        app = TaskMoverApp()
        print("   ✅ App created successfully")
        
        # Verify key components exist
        if hasattr(app, 'pattern_library') and hasattr(app, 'ruleset_manager'):
            print("   ✅ Core components initialized")
        else:
            print("   ⚠️  Some components missing")
            
        return True
    except Exception as e:
        print(f"   ❌ App creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_pattern_system():
    """Test pattern management system"""
    print("🔍 Testing pattern system...")
    
    try:
        from taskmover_redesign.core.pattern_library import PatternLibrary
        import tempfile
        
        # Create temporary directory
        temp_dir = tempfile.mkdtemp()
        
        # Test pattern library
        lib = PatternLibrary(temp_dir)
        pattern_id = lib.create_pattern("Test Pattern", "*.txt", "glob", "Test pattern for verification")
        
        if pattern_id and len(lib.patterns) > 0:
            print("   ✅ Pattern system working")
            return True
        else:
            print("   ❌ Pattern system not working")
            return False
            
    except Exception as e:
        print(f"   ❌ Pattern system failed: {e}")
        return False

def main():
    """Main verification function"""
    print("🚀 TaskMover Startup Verification")
    print("=" * 50)
    
    success = True
    success &= test_imports()
    success &= test_app_creation()
    success &= test_pattern_system()
    
    print("=" * 50)
    if success:
        print("🎉 ALL TESTS PASSED!")
        print("✅ TaskMover can start normally")
        print("\nTo start TaskMover:")
        print("1. Run: python -m taskmover_redesign")
        print("2. Or:  python taskmover_redesign/__main__.py")
        print("3. Or use the VS Code task: 'Run TaskMover Application'")
    else:
        print("❌ Some tests failed")
        print("🚨 TaskMover may not start correctly")
        
    return success

if __name__ == "__main__":
    main()
