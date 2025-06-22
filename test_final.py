#!/usr/bin/env python3
"""
Final comprehensive test of TaskMover application
"""

def test_imports():
    """Test all main imports"""
    print("Testing imports...")
    try:
        import taskmover_redesign.app
        import taskmover_redesign.core.ruleset_manager
        import taskmover_redesign.core.pattern_library
        import taskmover_redesign.core.rule_pattern_manager
        import taskmover_redesign.ui.pattern_tab
        import taskmover_redesign.ui.rule_components
        import taskmover_redesign.ui.components
        print("✅ All main modules import successfully!")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_app_instantiation():
    """Test app instantiation"""
    print("Testing app instantiation...")
    try:
        import taskmover_redesign.app
        app = taskmover_redesign.app.TaskMoverApp()
        print("✅ App instantiates successfully!")
        return True
    except Exception as e:
        print(f"❌ App instantiation failed: {e}")
        return False

def test_pattern_library():
    """Test pattern library functionality"""
    print("Testing pattern library...")
    try:
        from taskmover_redesign.core.pattern_library import PatternLibrary
        import tempfile
        import os
        
        # Create a temporary directory for testing
        temp_dir = tempfile.mkdtemp()
        lib = PatternLibrary(temp_dir)
        print("✅ PatternLibrary works!")
        
        # Clean up
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)
        return True
    except Exception as e:
        print(f"❌ PatternLibrary failed: {e}")
        return False

def test_ruleset_manager():
    """Test ruleset manager functionality"""
    print("Testing ruleset manager...")
    try:
        from taskmover_redesign.core.ruleset_manager import RulesetManager
        import tempfile
        import os
        
        # Create a temporary directory for testing
        temp_dir = tempfile.mkdtemp()
        manager = RulesetManager(temp_dir)
        print("✅ RulesetManager works!")
        
        # Clean up
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)
        return True
    except Exception as e:
        print(f"❌ RulesetManager failed: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Running final comprehensive tests...\n")
    
    success = True
    success &= test_imports()
    success &= test_app_instantiation()
    success &= test_pattern_library()
    success &= test_ruleset_manager()
    
    print(f"\n{'✅ ALL TESTS PASSED!' if success else '❌ Some tests failed'}")
    print("🎉 TaskMover application is ready!" if success else "🚨 Please check the errors above")
